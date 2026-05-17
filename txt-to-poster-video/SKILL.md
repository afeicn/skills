---
name: txt-to-poster-video
description: End-to-end workflow for turning a prepared Chinese narration script into a vertical short video. Use when the user provides or wants to provide a口播稿/文案 and asks to generate a video, cover poster, end card, gpt-image-2 body visuals, VoxCPM2 voiceover, captions, or a Video Account/Xiaohongshu-style 9:16 MP4.
---

# Txt To Poster Video

## Purpose

Convert a narration script into a complete vertical short-video package: video-ready script, generated illustration frames, matching cover and end card, VoxCPM2 voiceover, captioned 9:16 MP4.

This is an orchestration skill. It coordinates:
- `video-script-generator` — videoizing the script into pure narration (no annotations)
- `poster-style-generator` — cover + end card design via gpt-image-2
- `video-illustration-generator` — body illustration frames via gpt-image-2
- `pic-to-video-generator` — image sequence + 口播稿 → VoxCPM2 voiceover + captions + 9:16 MP4
- `bgm-video-mixer` — background music: intro chime + BGM + ending signature sound
- `jianying-editor-skill` — only when complex post-production polish is needed

## Image Gen Provider

All gpt-image-2 calls go through Hermes `image_gen` toolset:

| Provider | Auth | Setup |
|----------|------|-------|
| `openai-codex` ✅ | OAuth (ChatGPT Plus, no API key) | `hermes login --provider openai-codex` (device code flow), then `image_gen.provider: openai-codex` |
| `openai` | API key | `OPENAI_API_KEY` in `.env`, `image_gen.provider: openai` |

This user (沈飞) uses `openai-codex`. Model: `gpt-image-2-medium`.

## Inputs

Required: narration script / 口播稿正文, title (or permission to extract).

Recommended: poster style number (1-10), visual direction, target platform.

Default assumptions:
- 9:16 vertical video
- Cover/end-card 3:4 (1024×1536 portrait)
- End card CTA: follow + like + save
- One VoxCPM2 environment only

## Orchestration

This skill coordinates:
- `video-script-generator` — videoizing the script into pure narration (no annotations)
- `humanizer` — strip AI writing patterns from 口播稿 before finalizing
- `poster-style-generator` — cover + end card design via gpt-image-2
- `video-illustration-generator` — body illustration frames via gpt-image-2
- `pic-to-video-generator` — image sequence + 口播稿 → VoxCPM2 voiceover + captions + 9:16 MP4
- `bgm-video-mixer` — background music: intro chime + BGM + ending signature sound (+ volume=1.0 原音直出)

## Workflow

### 1. Prepare Working Folder

```
<task-folder>/
├── 口播稿.md          # Pure narration, no annotations
├── images/
│   ├── 00_cover.png   # Cover (copied from ./cover.png)
│   ├── 01.png         # Body illustrations
│   ├── ...            # (02-06.png etc)
│   └── 99_end_card.png
└── video_output/      # Auto-created by synthesize.py
    └── output_video.mp4
```

⚠️ **Naming is critical**: `pic-to-video-generator` reads `images/` in dictionary order. `00_cover.png` must sort first, `99_end_card.png` last.

### 2. Videoize The Script

Use `video-script-generator`.

CRITICAL: The output must be **PURE NARRATION TEXT** — no markdown, no headers, no timestamps, no `**bold**` markers. Just the spoken words with natural spacing for rhythm.

Example of correct format:
```
上一期我讲到， 企业做 AI 转型， 千万不要一上来就全员铺工具。

那接下来问题就来了：
如果不全员铺开， 第一步到底该从哪开始？
```

⚠️ **DO NOT** include: title suggestions, estimated duration, time-slot headers (`## 00:00 - 00:22`), `**keyword**` markdown. These will be read aloud by VoxCPM2 and corrupt subtitle layout.

Keyword highlighting is handled by `synthesize.py`'s built-in `HIGHLIGHTS` list — not by markdown in the script.

### 3. Humanize The Script（去 AI 味儿）

Use `humanizer` skill. The output from step 2 often has latent AI patterns — signpost phrases
("让我们看看", "接下来需要关注的是"), filler hedging ("可能", "一般来说"),
over-structured transitions, and neutral/voiceless prose.

Load the humanizer skill, then apply its 29-pattern checklist to the 口播稿.md:
- Remove signposting (pattern #28: "让我们深入探讨")
- Remove negative parallelisms (pattern #9: "不是...而是...")
- Remove filler hedging (pattern #24: "可能", "一般来说", "某种程度上")
- Remove pivot language (pattern #27: "关键在于", "核心问题是")
- Make sure it reads like real person talking: short sentences, first-person experience,
  specific concrete examples, opinions, varied rhythm

After humanizing, overwrite 口播稿.md with the clean version.

### 4. Generate Cover And End Card

Use `poster-style-generator`. Call `image_generate` with `aspect_ratio=portrait`.

Rules:
- Cover and end card must share the same visual system.
- Save as `cover.png` and `end_card.png` in task folder.
- Copy to images: `cp cover.png images/00_cover.png && cp end_card.png images/99_end_card.png`.
- Output the style reference for step 4.

### 5. Generate Body Illustration Frames

Use `video-illustration-generator`. Call `image_generate` with `aspect_ratio=portrait`.

- Reference cover/end card visual style from step 3.
- One image per major script beat (typically 6 frames for ~2 min video).
- Save as `images/01.png` through `images/06.png`.
- No text in illustrations — captions come from subtitle rendering.
- All prompts must share consistent visual system.

### 6. Build The Video

Use `pic-to-video-generator`'s `synthesize.py` script (Python, NOT the old generate_video.mjs).

Prerequisites:
- `images/` exists with properly ordered images
- `口播稿.md` exists (pure narration)
- Python 3 + Pillow, Node.js, FFmpeg, VoxCPM2 available
- LXGW WenKai font installed (download once: `curl -L -o ~/Library/Fonts/LXGWWenKai-Regular.ttf "https://github.com/lxgw/LxgwWenKai/releases/download/v1.522/LXGWWenKai-Regular.ttf"`)

Set environment variables:
```bash
export VOXCPM_BIN="/Users/liuwei/.local/miniforge3/envs/voxcpm2/bin/voxcpm"
export VOXCPM_REF_AUDIO="video_output/ref.wav"
```

Run:
```bash
cp ~/.hermes/skills/creative/pic-to-video-generator/scripts/synthesize.py ./
```

**⚠️ Before running, do two edits in the local `synthesize.py`:**
1. **编辑 `HIGHLIGHTS` 列表** — add key terms from this video's script as cyan-highlighted keywords. Place longest phrases first for correct matching priority.
2. **可选：口播倍速** — 如需加速口播，取消 `atempo=1.2` 相关代码的注释（位于 STEP 1 末尾），修改倍速值。默认匀速。修改后需删除 `video_output/narration.wav` 缓存再执行。

Then run:
```bash
python3 synthesize.py
# Output: video_output/output_video.mp4
```

### 7. Add Background Music (BGM)

Use `bgm-video-mixer`'s `add_bgm.py`. This adds three audio layers to the finished video:

1. **开场品牌音** — 0~2.3s, C-E-G 上行钟声 + 0.7s 停顿（口播从 3.0s 开始，不重叠）
2. **背景轻音乐** — 3.0s 到结束前 2.2s，15% 低音量循环
3. **结尾标志音** — 口播结束后 0.5s 停顿 + G-E-C 下行"叮" 1.7s

视频首尾帧自动冻结以匹配 padding，口播音量 100% 不变。时序对齐用 `adelay` 滤镜（将口播延后 3s 与 BGM music 起始点对齐），**禁止使用 concat 拼静音垫片**。

Music is auto-selected from Mixkit free library based on 口播稿 content mood analysis:
- 活力/科技 → *Raising Me Higher*
- 舒缓/反焦虑 → *Piano Reflections*
- 激励/行动 → *Motivating Mornings*
- 默认 → *Curiosity*

Run:
```bash
cp ~/.hermes/skills/creative/bgm-video-mixer/scripts/add_bgm.py ./
python3 add_bgm.py
# Output: video_output/output_video_bgm.mp4
```

⚠️ **音频噪音陷阱（重要）**：`add_bgm.py` 使用 `adelay` 替代 `concat` 来对齐时间线。**禁止改为 concat 拼静音垫片** — ffmpeg 的 `concat` 滤镜在拼接 anullsrc（数字零值）和 PCM WAV 时会引入约 -58 dB 的底噪，用户可清晰感知。详见 `bgm-video-mixer/references/narration-delay-approach.md`。
1. **volume=1.5（轻微增益）** — 不加过多以免放大 VoxCPM2 建模底噪。1.5× 在人耳可接受范围。
2. **adelay 替代 concat** — 用 `adelay` 将口播延后 3s，避免 `concat` 滤镜拼接 anullsrc(静音) 时引入 ~-58 dB 底噪。
详见 `bgm-video-mixer` skill 的噪音陷阱章节。|

Options:
- `--mood upbeat|calm|professional|motivating|warm|corporate` — force mood
- `--bgm <path>` — manually specify background music file
- `--no-bgm` — only add intro/ending, skip background music

### 8. VoxCPM2 Reference Audio

Get ref.wav from user's voice message on Feishu:
1. Voice message cached at `~/.hermes/audio_cache/audio_*.m4a`
2. Convert: `ffmpeg -y -i <m4a> -ar 16000 -ac 1 video_output/ref.wav`

Fallback (no voice message): use `voxcpm design` mode to generate a ref:
```bash
/Users/liuwei/.local/miniforge3/envs/voxcpm2/bin/voxcpm design \
  --text "测试文本" --control "专业沉稳的男声" --output video_output/ref.wav
```

### 9. Subtitle Fixes (if needed)

If only subtitles need fixing (font, size, highlights), do NOT re-run VoxCPM2. Use a fix script that only regenerates the subtitle overlay and re-muxes.

### 10. Verify Output

- `video_output/output_video.mp4` exists, ~4-8 MB (depends on duration), 720×1280 H.264
- `video_output/output_video_bgm.mp4` exists (after BGM step), with intro + BGM + ending audio
- Audio present (AAC 160k, stereo for BGM version)
- Images visible (not all black ⚠️)
- Subtitles readable with correct font and highlights (check HIGHLIGHTS were updated per video)
- Cover → body → end card in order
- Background music audible but not overpowering narration
- Volume test: BGM version should be ~3dB louder than original (not quieter)

## ⚠️ Common Pitfalls

| Problem | Root Cause | Fix |
|---------|-----------|-----|
| Video all black | ffmpeg `yuva420p` silently falls back to opaque → subtitle overlay covers everything | Use `yuv420p` + `colorkey` green screen (see pic-to-video-generator skill) |
| Subtitle layout garbled | `\\n` newlines in 口播稿.md not stripped | Always `replace('\\n', ' ')` before parsing |
| Subtitles too low / covered | BOTTOM_MARGIN=140 too close to bottom | Changed to 300px (~3 lines up) in synthesize.py |
| Wrong font / tiny text | PingFang.ttc path doesn't exist on macOS | Use LXGW WenKai (~/Library/Fonts/) or STHeiti Medium |
| Images out of order | Dictionary sort puts "10" before "2" | Use zero-padded names: 00_cover, 01, 02, ..., 99_end |
| Cover not in video | cover.png in root, not in images/ | `cp cover.png images/00_cover.png` |
| `voxcpm: command not found` | Using `source activate` instead of direct path | Use `VOXCPM_BIN` pointing to bin/voxcpm |
| Audio has noise artifacts | ffmpeg `concat` 滤镜拼 anullsrc(静音)和PCM narration时引入 -58dB 底噪 | add_bgm.py 已改用 `adelay` 替代 concat — 口播延后3s直接混BGM，静音间隙-91dB |
| Audio too quiet overall | VoxCPM2 output naturally quiet (-25 dB mean) | volume=1.0 原音直出，用户调节设备音量。与 BGM 混合后音量已足够。不放大底噪是首要目标 |
| Subtitles out of sync after speed change | 加速口播后字幕仍按原速均匀分布 | 删除 narration.wav 缓存重新跑生成，字幕时序自动按新音频时长重新计算 |
| BGM missing after mix | `add_bgm.py` not run | Run step 7 after `synthesize.py` completes |
| BGM too quiet / sounds same as original | ffmpeg amix default normalization halves both tracks | Script uses `amix:normalize=0` — check it's in the local add_bgm.py |
| Music download timeout | Network/CF block on Mixkit | Script auto-falls back to offline ffmpeg tone synthesis |
| BGM too loud / covers voice | Default volume too high | Script uses 15% volume — adjust via `volume=0.15` in add_bgm.py |

## Final Response

Report: task folder, MP4 paths (with and without BGM), cover path, style number, duration, music track used, any blockers.
