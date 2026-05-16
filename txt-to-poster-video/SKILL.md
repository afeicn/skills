---
name: txt-to-poster-video
description: End-to-end workflow for turning a prepared Chinese narration script into a vertical short video. Use when the user provides or wants to provide a口播稿/文案 and asks to generate a video, cover poster, end card, gpt-image-2 body visuals, VoxCPM2 voiceover, captions, or a Video Account/Xiaohongshu-style 9:16 MP4.
---

# Txt To Poster Video

## Purpose

Use this skill to convert a prepared narration script into a complete vertical short-video package: video-ready script, generated illustration frames, matching cover and end card, VoxCPM2 voiceover, captioned 9:16 MP4, and final delivery notes.

This is an orchestration skill. It coordinates these skills/tools:
- `video-script-generator` for videoizing the script, segmenting subtitles, and marking highlights.
- `poster-style-generator` / 海报风格生成器 for matching cover and end card. It must use OpenAI `gpt-image-2`.
- `video-illustration-generator` for body illustration frames. It must use OpenAI `gpt-image-2`.
- `pic-to-video-generator` for image sequence + `口播稿.md` -> voiceover + captions + 9:16 MP4.
- `jianying-editor-skill` only when the user needs complex post-production polish.

## Inputs To Request

Ask only for missing inputs that materially affect the result.

Required:
- Prepared narration script / 口播稿正文.
- Title, or permission to extract title options from the script.

Recommended:
- Poster style number from `poster-style-generator`'s 10 styles, or permission to choose.
- Visual direction for `gpt-image-2` frames, such as realistic photo, illustration, workplace, technology, new Chinese style, warm documentary, or cinematic.
- Target platform: 视频号, 小红书, 抖音, or generic vertical short video.

Optional:
- Must-keep sentences or phrases that should not be rewritten.
- Desired number of body images.
- Whether to include the end card inside the final video.

Default assumptions:
- Output ratio is 9:16 for video.
- Cover/end-card ratio is 3:4 unless the platform or poster skill requires otherwise.
- End card CTA is limited to following, liking, and saving/collecting.
- Use one VoxCPM2 environment only. Do not run `voxcpm-audio-generator` separately unless the user asks for separate audio, preview, a different voice, or reusable audio.

## Workflow

### 1. Prepare The Working Folder

Create or choose a task folder for the video package. Standard structure:

```text
<task-folder>/
├── 口播稿.md
├── images/
│   ├── 01.png
│   ├── 02.png
│   └── 99_end_card.png
├── cover.png
└── video_output/
    └── output_video.mp4
```

Use stable numeric filenames because `pic-to-video-generator` plays `images/` in dictionary order.

### 2. Videoize The Script

Use `video-script-generator`.

Do:
- Preserve the user's voice and core wording.
- Split the script into video-friendly paragraphs and subtitle chunks.
- Add `**keyword**` highlights sparingly for important terms; `pic-to-video-generator` renders these as gold subtitle highlights.
- Produce `口播稿.md`.

Do not:
- Rewrite the whole script unless the user explicitly asks.
- Add stage directions that should not be spoken unless they are kept outside the narration text.

### 3. Generate Cover And End Card (Sets The Visual Style)

Use `poster-style-generator` / 海报风格生成器 first — this determines the visual direction that all subsequent images will follow.

Required model:
- OpenAI `gpt-image-2`
- Tool model string: `openai/gpt-image-2`

Generate both:
- Cover: title-forward poster for click appeal.
- End card: CTA image asking for 关注 / 点赞 / 收藏.

Rules:
- Cover and end card define the unified visual system: palette, subject style, camera language, typography, mood.
- Use the selected poster style number; if none is provided, recommend one based on the topic.
- Save cover separately as `cover.png`.
- Save the end card separately as `end_card.png`.
- Save or copy the end card into `images/` as the last frame, usually `99_end_card.png`, when it should appear at the end of the video.
- **Output the style reference** (color palette, mood, composition notes) for `video-illustration-generator` to consume.

### 4. Generate Body Illustration Frames (Follows Poster Style)

Use `video-illustration-generator`.

Required model:
- OpenAI `gpt-image-2`
- Tool model string: `openai/gpt-image-2`

Process:
- **Reference the cover/end card's visual style** from step 3 — derive prompts that match its palette, mood, character style, and composition language.
- Derive one image prompt per major script beat or scene, maintaining strict visual consistency with the poster.
- Generate vertical-friendly images suitable for 9:16 composition.
- Save images in `images/` as `01.png`, `02.png`, etc.

Guidance:
- If the user does not choose image count, use enough frames to avoid monotony while keeping production fast.
- Avoid embedding dense text in body illustrations; captions will be added by the video generator.

### 5. Build The Video

Use `pic-to-video-generator`.

Prerequisites:
- `images/` exists and contains at least one image.
- `口播稿.md` exists.
- Node.js, FFmpeg, LXGW WenKai, and VoxCPM2 are available.
- Set VoxCPM variables to the existing single environment:

```bash
export VOXCPM_VENV_PATH="/Users/afeicn/Documents/55XHS_content_os/voxcpm/.venv/bin/activate"
export VOXCPM_REF_AUDIO="/Users/afeicn/Documents/55XHS_content_os/voxcpm/1.0/ref.wav"
```

Run the generator per `pic-to-video-generator` instructions:
- Copy its `scripts/generate_video.mjs` into the task folder.
- Run `node generate_video.mjs`.
- Expected output: `video_output/output_video.mp4`.

Important:
- `pic-to-video-generator` invokes VoxCPM2 only while generating narration. It is not a long-running service.
- Do not also run `voxcpm-audio-generator` in the same normal flow.

### 6. Verify Output

Check before reporting completion:
- `video_output/output_video.mp4` exists and is non-empty.
- Audio was generated and muxed.
- Captions appear and do not obviously overlap.
- The end card appears at the end if requested.
- The cover file exists for platform upload.
- The video plays or at least probes successfully with FFmpeg/ffprobe.

For complex edits, use `jianying-editor-skill` after this step only when needed for custom transitions, stickers, openings/endings, or platform packaging.

## Final Response

Report:
- The task folder.
- The final MP4 path.
- The cover path.
- The end-card path if separate.
- Any assumptions made, such as selected style number or default visual direction.
- Any verification performed or blockers encountered.

