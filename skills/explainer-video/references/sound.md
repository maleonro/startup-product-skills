# Voice, music and sound

You cannot hear. Every audio decision is a measurement plus the owner's ear on a sample.

The same rule as the images applies: use what the owner already pays for first (an ElevenLabs plan,
a music subscription, a royalty-free library), then a paid API under a quoted cap. The first video
ran voice and music through Higgsfield, so one balance covered images, voice and music.

## 1. Voice

- The first video used ElevenLabs v4 through Higgsfield:
  `higgsfield generate create elevenlabs_v4 --dialogue '[{"text":"...","voice_id":"<uuid>"}]' --wait --json`.
  The `voice_id` is a UUID from `higgsfield voices list`. ElevenLabs' own API offers the same model
  with its own key; the call and the voice IDs differ.
- **Run every CLI call with stdin closed (`< /dev/null`) and a timeout.** `higgsfield generate cost`
  for a voice hung forever when it inherited stdin. macOS has no `timeout`: set it in the runner.
- Record the hook in 3 voices (about 4 credits each) and let the owner choose.
- Cost was about 4.5-5 credits per 1,000 characters, and a longer text cost more than its quote
  (approved 4.14, charged 4.60). Quote again with the final text and ask if it moved.
- Record per section, so a script fix re-records one section only.
- A system voice (`say` on macOS) is fine for a rough timing, never for the final pace: it came out
  more than a minute short in ten.

## 2. Word times

- Local Whisper (`mlx_whisper` with `large-v3-turbo` on Apple silicon; `openai-whisper` or
  `faster-whisper` elsewhere) gives a time for every word. The edit, the subtitles and the music
  cuts all hang off these times.
- Whisper writes digits ("150"), misspells brand names and can miss a regional register (it heard
  "tú" forms in a voseo take). For subtitles, use the script's words with Whisper's times, never
  Whisper's text.
- Whisper invents zero-length words at the end of a take. Cut at the first zero-length word in the
  last 1.5 s. Dropping only very short words left garbage behind.

## 3. Music

The owner's note on the first score: "too loud, very monotone, always goes from less to more, almost
lo-fi or aspirational". What fixed it:

- **One piece per chapter, each with its own mood** (hook intriguing, the AI chapter colder, a
  playful chapter, a tense one, a calm close). Two short takes looped 20 times sounded monotone. The
  owner chose the style from 3 samples of the hook: "detective" (plucked double bass, woodblock) won.
- **No "hopeful", "wonder" or "slow build" in the prompt.** Ask for sparse and steady. The model
  builds a crescendo anyway (one piece went from -20 to -9 dB with the same notes), so level each
  piece with a slow gain until it stays within 1 dB.
- **14 dB under the voice.** It was 7. Measure it; do not trust the gain number.
- The piece starts with the chapter card and stops on the chapter's last word. It goes silent on the
  key moments (the bets, the key numbers) and comes back after.
- First video: Higgsfield's `sonilo_music --duration <s> --prompt ...`, 0.0625 credits a second; 9
  pieces cost 42.30 credits.
- Asked "which is the most engaging?": say you cannot hear it. Measure the pulse (autocorrelation of
  the onsets), the change in note density and the energy in the voice band, and say what you measured.

## 4. Paper sounds

- Kenney's CC0 packs (RPG Audio, Impact Sounds; kenney.nl/assets) plus a pencil made in code. CC0
  needs no permission and no credit (this skill credits Kenney anyway).
- Put the sound inside the component that makes it (mark, stamp, note, counter), so it plays by
  itself. The first video had 144 hits, median peak -19 dBFS in a mix at about -20.6.
- A mono file lands 3 dB lower in a stereo mix. A sound mounted late (behind an early `return null`)
  loses its start. Align two-hit sounds (a stamp) by their peaks. Start a sound at 30 % of its peak,
  not at the first soft touch.

## 5. How to measure audio

- Render the audio twice as WAV, with and without the layer (input props `music:false`,
  `sfx:false`), and subtract. In an MP4 the AAC noise (about -31 dB) hides quiet layers.
- On macOS, `afconvert -f WAVE -d LEI16@48000 -c 1` turns a Remotion WAV into one Python's `wave`
  can read.
- Remotion's bundled ffmpeg has no `volumedetect`: compute levels in Python.
- Targets that passed: music about 14 dB under the voice; no 0.5 s window of music under -30 dB
  where it should play; no peak over 0 dBFS after levelling.
