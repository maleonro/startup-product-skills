#!/usr/bin/env python3
"""Consolida rondas de inversión LATAM en un ledger acumulativo.

Uso:
  python3 consolidar.py --input raw.csv --ledger data/rondas-latam.csv --run-date 2026-07-16 [--fx-brl 5.45] [--seed]

Input crudo (columnas; las que falten se asumen vacías):
  company, country, round_type, amount, currency, date, investors, sector,
  source_url, source_type, linkedin_person, linkedin_post_url
  (acepta `amount_usd` como alias de amount con currency=USD)

Salida: ledger actualizado in-place + data/nuevas-<run-date>.csv (salvo --seed)
+ quality report por stdout.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

LEDGER_COLUMNS = [
    "company", "country", "round_type", "amount_usd", "date", "investors",
    "sector", "source_url", "source_type", "confidence", "signal",
    "first_seen_date", "linkedin_person", "linkedin_post_url",
]

ROUND_MAP = {
    "pre-seed": "pre-seed", "preseed": "pre-seed", "pre seed": "pre-seed",
    "angel": "pre-seed", "seed": "seed", "seed extension": "seed",
    "seed+": "seed", "semilla": "seed", "pre-series a": "seed",
    "pre-serie a": "seed", "series a": "series-a", "series-a": "series-a",
    "serie a": "series-a", "series b": "series-b", "series-b": "series-b",
    "serie b": "series-b", "series c": "series-c", "series-c": "series-c",
    "serie c": "series-c", "series d": "series-d", "series-d": "series-d",
    "serie d": "series-d", "growth": "growth",
    "debt": "debt", "debt facility": "debt", "debt issuance": "debt",
    "credit line": "debt", "credit facility": "debt", "fidc": "debt",
    "venture debt": "debt", "grant": "grant",
}
# "equity"/"equity financing" NO se mapea: es etiqueta genérica de agregadores
# (latamfintech la usa igual para US$100K que para US$500M) — queda "other".

# Alias observados entre fuentes: clave = variante, valor = nombre canónico del ledger.
ALIASES = {
    "bianca": "bianca ai",
    "telepatia": "telepatia ai",
    "plata": "banco plata",
}
LEGAL_SUFFIX = re.compile(r"[,\s]+(s\.?a\.?(\s+de\s+c\.?v\.?)?|s\.?a\.?s\.?|inc\.?|ltda\.?|ltd\.?)$")


def canonical_company(name):
    key = name.strip().lower()
    key = LEGAL_SUFFIX.sub("", key).strip()
    return ALIASES.get(key, key)

CONFIDENCE_BY_SOURCE = {
    "latamlist": "high", "latamfintech": "high",
    "newsletter": "medium", "prensa-br": "medium", "linkedin_search": "low",
}

CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1, "": 0}

EXPANSION_ROUNDS = {"series-a", "series-b", "series-c"}
EARLY_ROUNDS = {"pre-seed", "seed"}
SCALE_ROUNDS = {"series-d", "growth"}


def normalize_round(raw):
    key = raw.strip().lower()
    if key in ROUND_MAP:
        return ROUND_MAP[key]
    for pattern, value in ROUND_MAP.items():
        if key.startswith(pattern):
            return value
    return "other" if key else ""


def normalize_amount(raw, currency, fx_brl):
    """Devuelve entero USD o None. Mantiene el fix validado: una cifra
    'pelada' menor a 1000 se interpreta como millones."""
    raw = str(raw or "").strip()
    if not raw:
        return None
    is_brl = "R$" in raw.upper() or currency.upper() == "BRL"
    text = raw.upper().replace(",", "").replace("US$", "").replace("R$", "").replace("$", "")
    match = re.search(r"([\d.]+)\s*(BN|B|MM|M|MILLION|MILLONES|MILHOES|MILHÕES|K|MIL)?", text)
    if not match or not match.group(1):
        return None
    try:
        num = float(match.group(1))
    except ValueError:
        return None
    unit = match.group(2) or ""
    if unit in ("BN", "B"):
        num *= 1_000_000_000
    elif unit in ("MM", "M", "MILLION", "MILLONES", "MILHOES", "MILHÕES"):
        num *= 1_000_000
    elif unit in ("K", "MIL"):
        num *= 1_000
    elif num < 1000:
        num *= 1_000_000
    if is_brl:
        num /= fx_brl
    return int(num)


def normalize_date(raw):
    raw = str(raw or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw) or re.fullmatch(r"\d{4}-\d{2}", raw) or re.fullmatch(r"\d{4}", raw):
        return raw
    return ""


def classify_signal(round_type, date, run_date):
    if round_type in EXPANSION_ROUNDS and date and date[:4] >= str(int(run_date[:4]) - 1):
        return "expansion"
    if round_type in EARLY_ROUNDS:
        return "early"
    if round_type in SCALE_ROUNDS:
        return "scale"
    return "other"


def dedup_key(row):
    amount = row["amount_usd"]
    bucket = int(amount) // 1_000_000 if amount not in (None, "") else None
    return (canonical_company(row["company"]), row["round_type"], bucket)


def months_apart(d1, d2):
    """Distancia en meses entre dos fechas YYYY[-MM[-DD]]. Sin fecha => 0 (no bloquea)."""
    if len(d1) < 7 or len(d2) < 7:
        return 0
    return abs((int(d1[:4]) - int(d2[:4])) * 12 + int(d1[5:7]) - int(d2[5:7]))


def find_ledger_match(ledger, row):
    """Busca la ronda en el ledger. Primero llave exacta; si no, misma empresa y
    tipo de ronda con monto a ±15% y fechas a ≤3 meses (la misma ronda reportada
    en otra moneda o con otra tasa FX cae en buckets distintos — caso UY3:
    R$200M valían US$37.2M en enero y US$39.4M a la tasa de julio)."""
    key = dedup_key(row)
    if key in ledger:
        return key
    company, round_type, bucket = key
    # "other"/vacío significa tipo desconocido, no un tipo distinto: actúa como comodín
    # (caso UY3: el agregador no decía el tipo -> "other"; Finsiders dice FIDC -> "debt").
    unknown = ("", "other")
    candidates = [k for k in ledger if k[0] == company
                  and (k[1] == round_type or k[1] in unknown or round_type in unknown)]
    if not candidates:
        return None
    if bucket is None:
        return candidates[0] if len(candidates) == 1 else None
    amount = int(row["amount_usd"])
    for k in candidates:
        other = ledger[k]["amount_usd"]
        if not other:
            return k
        other = int(other)
        if abs(amount - other) / max(amount, other) <= 0.15 \
                and months_apart(row["date"], ledger[k]["date"]) <= 3:
            return k
    return None


def merge_rows(winner, loser):
    for col in LEDGER_COLUMNS:
        if not winner.get(col) and loser.get(col):
            winner[col] = loser[col]
    # Una fecha más precisa (mismo prefijo, más larga) refina a la gruesa:
    # "2026-07-02" reemplaza "2026-07".
    wd, ld = winner.get("date", ""), loser.get("date", "")
    if ld and wd and len(ld) > len(wd) and ld.startswith(wd):
        winner["date"] = ld
    # Un tipo de ronda específico le gana al desconocido.
    if winner.get("round_type") in ("", "other") and loser.get("round_type") not in ("", "other"):
        winner["round_type"] = loser["round_type"]
    return winner


def normalize_row(raw, fx_brl, run_date, report):
    row = {col: str(raw.get(col, "") or "").strip() for col in LEDGER_COLUMNS}
    amount_input = raw.get("amount") or raw.get("amount_usd") or ""
    currency = str(raw.get("currency", "") or "USD")
    amount = normalize_amount(amount_input, currency, fx_brl)
    row["amount_usd"] = str(amount) if amount is not None else ""
    if amount is None:
        report["sin_monto"].append(row["company"])
    row["round_type"] = normalize_round(raw.get("round_type", ""))
    row["date"] = normalize_date(raw.get("date", ""))
    if not row["date"]:
        report["sin_fecha"].append(row["company"])
    row["source_type"] = row["source_type"] or "latamlist"
    row["confidence"] = row["confidence"] or CONFIDENCE_BY_SOURCE.get(row["source_type"], "medium")
    row["signal"] = classify_signal(row["round_type"], row["date"], run_date)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--run-date", required=True)
    parser.add_argument("--fx-brl", type=float, default=5.3, help="tasa BRL por USD del día de corrida")
    parser.add_argument("--seed", action="store_true", help="migración inicial: no escribe archivo delta")
    args = parser.parse_args()

    if not normalize_date(args.run_date) or len(args.run_date) != 10:
        sys.exit("--run-date debe ser YYYY-MM-DD")

    report = {"sin_monto": [], "sin_fecha": [], "deduplicadas": [], "nuevas": 0, "mergeadas": 0}

    ledger_path = Path(args.ledger)
    ledger = {}
    if ledger_path.exists():
        with open(ledger_path, newline="", encoding="utf-8") as f:
            for raw in csv.DictReader(f):
                row = {col: str(raw.get(col, "") or "").strip() for col in LEDGER_COLUMNS}
                key = dedup_key(row)
                if key in ledger:
                    report["deduplicadas"].append(f"{row['company']} (ledger)")
                    ledger[key] = merge_rows(ledger[key], row)
                else:
                    ledger[key] = row

    with open(args.input, newline="", encoding="utf-8") as f:
        incoming = [normalize_row(raw, args.fx_brl, args.run_date, report) for raw in csv.DictReader(f)]

    batch = {}
    for row in incoming:
        key = dedup_key(row)
        if key in batch:
            report["deduplicadas"].append(row["company"])
            a, b = batch[key], row
            winner, loser = (a, b) if CONFIDENCE_RANK[a["confidence"]] >= CONFIDENCE_RANK[b["confidence"]] else (b, a)
            batch[key] = merge_rows(winner, loser)
        else:
            batch[key] = row

    new_rows = []
    for key, row in batch.items():
        match = find_ledger_match(ledger, row)
        if match is not None:
            merged = merge_rows(ledger[match], row)
            merged["signal"] = classify_signal(merged["round_type"], merged["date"], args.run_date)
            ledger[match] = merged
            report["mergeadas"] += 1
        else:
            row["first_seen_date"] = args.run_date
            ledger[key] = row
            new_rows.append(row)
    report["nuevas"] = len(new_rows)

    rows = sorted(ledger.values(), key=lambda r: r["date"], reverse=True)
    with open(ledger_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    if new_rows and not args.seed:
        delta_path = ledger_path.parent / f"nuevas-{args.run_date}.csv"
        with open(delta_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS)
            writer.writeheader()
            writer.writerows(new_rows)
        print(f"Delta: {delta_path}")

    total = sum(int(r["amount_usd"]) for r in rows if r["amount_usd"])
    expansion_nuevas = [r for r in new_rows if r["signal"] == "expansion"]
    print(f"Ledger: {len(rows)} rondas | total disclosed US${total / 1e9:.2f}B")
    print(f"Corrida {args.run_date}: {report['nuevas']} nuevas ({len(expansion_nuevas)} expansion), {report['mergeadas']} mergeadas con existentes")
    if report["deduplicadas"]:
        print(f"Dedup intra-corrida: {', '.join(report['deduplicadas'])}")
    if report["sin_monto"]:
        print(f"Sin monto ({len(report['sin_monto'])}): {', '.join(report['sin_monto'][:10])}{'…' if len(report['sin_monto']) > 10 else ''}")
    if report["sin_fecha"]:
        print(f"Sin fecha parseable ({len(report['sin_fecha'])}): {', '.join(report['sin_fecha'][:10])}{'…' if len(report['sin_fecha']) > 10 else ''}")


if __name__ == "__main__":
    main()
