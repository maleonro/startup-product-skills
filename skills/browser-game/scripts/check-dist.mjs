#!/usr/bin/env node
// Fails the build if a reference or source-art file ended up in the published folder.
// It compares content hashes, so a renamed or re-hashed copy is caught too.
//
//   node check-dist.mjs [--dist dist] [--forbid ref] [--forbid art-src] [--allow assets]
//                       [--name 'mockup|benchmark|turnaround']
//
// --forbid  folders that must never ship: look references, screenshots of other games, raw
//           generated art (repeatable; default: ref, art-src).
// --allow   folders the game ships on purpose. A file there may also sit in a forbidden folder
//           (a brand font kept next to the references) without failing (default: assets).
// --name    a regex for file names that must never ship, whatever their content.
//
// Run it at the end of the build script: "build": "vite build && node scripts/check-dist.mjs".
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';

const args = process.argv.slice(2);
const many = (flag, fallback) => {
  const out = [];
  for (let i = 0; i < args.length; i++) if (args[i] === flag && args[i + 1]) out.push(args[++i]);
  return out.length > 0 ? out : fallback;
};
const one = (flag, fallback) => many(flag, [fallback])[0];

const root = process.cwd();
const dist = resolve(root, one('--dist', 'dist'));
const forbid = many('--forbid', ['ref', 'art-src']).map((d) => resolve(root, d));
const allow = many('--allow', ['assets']).map((d) => resolve(root, d));
const banned = new RegExp(one('--name', 'mockup|benchmark|turnaround|(^|[\\\\/])ref[\\\\/]'), 'i');

function walk(dir) {
  if (!existsSync(dir)) return [];
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}
const sha1 = (p) => createHash('sha1').update(readFileSync(p)).digest('hex');

if (!existsSync(dist)) {
  console.error(`check-dist: ${relative(root, dist)}/ does not exist. Build first.`);
  process.exit(1);
}

const shipped = new Set(allow.flatMap(walk).map(sha1));
const forbidden = new Map(forbid.flatMap(walk).map((p) => [sha1(p), relative(root, p)]));
const files = walk(dist);
const problems = [];
for (const p of files) {
  const rel = relative(root, p);
  const hit = shipped.has(sha1(p)) ? undefined : forbidden.get(sha1(p));
  if (hit) problems.push(`${rel} is a copy of ${hit}`);
  if (banned.test(relative(dist, p))) problems.push(`${rel} has a reference-style name`);
}

if (problems.length > 0) {
  console.error('check-dist: the build contains files that must not ship:');
  for (const m of problems) console.error(`  - ${m}`);
  process.exit(1);
}
console.log(`check-dist: ok (${files.length} files in ${relative(root, dist)}/, none from ${forbid.map((d) => relative(root, d)).join(', ')})`);
