# Subtitle Fallback: Pillow PNG + Chroma-Key Overlay

Use this when ffmpeg lacks `libass` (no `ass`/`subtitles`/`drawtext` filter).
Tested on Homebrew ffmpeg 8.1.1 on Apple Silicon.

**CRITICAL**: Homebrew ffmpeg also does NOT support `yuva420p` (alpha channel) via libx264.
Using `-pix_fmt yuva420p` silently falls back to `yuv420p`, producing a BLACK overlay
that completely covers the background video.

## Correct Approach: Chroma-Key (Green Screen)

Render subtitles on a pure green (#00FF00) background, then use ffmpeg's `colorkey`
filter to make green transparent during final mux.

### Pipeline

1. **Parse narration** — Split at punctuation `[。，！？?：]`. Group into ~28-char
   segments. Wrap each segment to max 14 chars per line (max 2 lines).
   
   ⚠️ **MUST** replace `\n` with space before parsing — raw newlines in the
   narration text cause corrupted subtitle layout.

2. **Render PNGs** — For each segment, use Pillow:
   ```python
   FONT_PATH = "~/Library/Fonts/LXGWWenKai-Regular.ttf"
   FONT_SIZE = 46
   LINE_SPACING = 56
   BOTTOM_MARGIN = 140
   
   img = Image.new("RGB", (720, 1280), (0, 255, 0))  # Green background
   
   # Dark green box behind text (renders as semi-transparent black after chroma-key)
   draw.rounded_rectangle([30, y-pad, W-30, y+h+pad], radius=14, fill=(0, 45, 0))
   
   # White text with light gray outline
   for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
       draw.text((x+dx, y+dy), text, font=font, fill=(180, 180, 180))  # outline
   draw.text((x, y), text, font=font, fill=(255, 255, 255))  # main
   ```

3. **Keyword Highlighting** — Key phrases rendered in cyan (#00D7FF) instead of white.
   Highlight list defined at top of script, longest-match-first:
   ```python
   HIGHLIGHTS = ["AI 转型", "最痛的场景", "最怕做成展示项目", ...]
   ```
   Text is tokenized into (text, is_highlight) spans before rendering.

4. **Create clips** — `ffmpeg -y -loop 1 -t <dur> -i sub_xxx.png -c:v libx264 -pix_fmt yuv420p -r 24 -an clip_xxx.mp4`
   (Note: `yuv420p`, NOT `yuva420p`)

5. **Fill gaps** — Pure green PNG rendered as MP4 for silent segments.

6. **Concat** — `ffmpeg -f concat -safe 0 -i segments.txt -c copy subtitles_chromakey.mp4`

7. **Final mux with chroma-key**:
   ```bash
   ffmpeg -y \
     -i slideshow.mp4 \
     -i subtitles_chromakey.mp4 \
     -i narration.wav \
     -filter_complex "[1:v]colorkey=0x00FF00:0.2:0.1[sub];[0:v][sub]overlay=format=auto[outv]" \
     -map "[outv]" -map "2:a" \
     -c:v libx264 -c:a aac -b:a 160k -shortest -pix_fmt yuv420p \
     output_video.mp4
   ```

## Font Installation

LXGW WenKai (霞鹜文楷) is NOT bundled with macOS. Download from GitHub:
```bash
curl -L -o ~/Library/Fonts/LXGWWenKai-Regular.ttf \
  "https://github.com/lxgw/LxgwWenKai/releases/download/v1.522/LXGWWenKai-Regular.ttf"
```

Fallback: STHeiti Medium at `/System/Library/Fonts/STHeiti Medium.ttc` (bold Chinese, readable).

## Key Values
- Canvas: 720×1280
- Font: LXGW WenKai 46px, line spacing 56px
- Highlight color: Cyan (0, 215, 255) — matches original ASS `&H00D7FF&`
- Outline: Light gray (180, 180, 180) — simulates 0.5px white stroke
- Box: dark green (0, 45, 0), radius 14px, padding 20px
- Box Y: `H - 140 - (lines * 56)` to `H - 120`
- FPS: 24, codec: libx264
