# VoxCPM2 Chunked Audio Generation

## Problem

VoxCPM2 produces noticeable noise/artifacts when generating long-form narration (>60 seconds) in a single pass. Audio quality degrades as the generation progresses.

## Solution

Split the narration text into ~30-second chunks, generate each chunk separately, then concatenate.

## Implementation

Handled inside `scripts/generate_video.mjs`:

1. **`splitIntoAudioChunks(text)`** function:
   - Strips markdown `**` highlight markers
   - Splits text at Chinese sentence boundaries (`。！？?`)
   - Groups sentences into ~120-character chunks (~30 seconds speech at 235 chars/min)
   - For sentences longer than 120 chars: splits at inner pauses (`，；：`) or hard-splits at 120 chars

2. **Per-chunk generation loop**:
   - Each chunk: `voxcpm clone --text "$chunk" --reference-audio "$ref" --output chunk_N.aiff`
   - Convert to WAV: `ffmpeg -i chunk_N.aiff chunk_N.wav`
   - Per-chunk cache: if `chunk_N.wav` already exists, skip

3. **Concatenation**:
   - FFmpeg concat demuxer on all chunk WAVs → `narration.wav`

## Cache Strategy

- `narration.wav` (final output): if exists, skip all audio generation
- Per-chunk WAVs: if a specific `narration_chunk_N.wav` exists, skip only that chunk
- This allows partial cache hits when only some chunks changed
