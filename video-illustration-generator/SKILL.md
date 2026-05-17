---
name: video-illustration-generator
description: Generate ordered vertical body illustration images for short-video scripts. Use for images/01.png, images/02.png, etc. from a 分镜 or 口播稿. Must use OpenAI gpt-image-2.
---

# Video Illustration Generator

## Purpose

Generate only the body illustration frames for a vertical short video.

This skill is responsible for:
- Splitting a video script into visual beats.
- Generating ordered images in `images/`.

Cover and end card generation belongs to `poster-style-generator`.

## Required Model

Always generate images with OpenAI `gpt-image-2`.

Use the Hermes `image_gen` tool with:
- model: `gpt-image-2-medium` (or `gpt-image-2-low` for speed, `gpt-image-2-high` for quality)
- vertical-friendly source images for 9:16 video
- preferred size: `1024x1536`
- format: png

Do not use the ambiguous `image2` alias.

## Provider Setup

Same setup as `poster-style-generator`:

| Provider | Auth | Config |
|----------|------|--------|
| `openai-codex` | OAuth (ChatGPT Plus) | `hermes config set image_gen.provider openai-codex` → device code login via `hermes model` |
| `openai` | API key | Set `OPENAI_API_KEY` in `.env`; `hermes config set image_gen.provider openai` |

**For this user (沈飞):** `openai-codex` is configured. The agent calls the Hermes `image_gen` tool automatically — no manual invocation needed.

## Inputs

Required:
- Video-ready narration script, `口播稿.md`, or 分镜.
- Overall visual direction, or permission to infer it from the topic.

Recommended:
- Number of body images.
- Cover/end-card style selected by `poster-style-generator`.
- Target platform: 视频号, 小红书, 抖音, or generic vertical video.

Defaults:
- Generate 6-8 body images for a 2-3 minute 口播 video.
- Avoid dense embedded text because captions are added by the video generator.
- Leave lower-third negative space for subtitles.
- Keep all frames consistent with the cover and end-card style.

## Workflow

1. Read `口播稿.md` or the 分镜 script.
2. Split the content into major beats.
3. Create one concise image prompt per beat.
4. Keep one consistent visual system across all prompts: palette, lighting, subject style, composition, and business/AI visual language.
5. Generate each image using `gpt-image-2-medium` (via Hermes image_gen tool).
6. Save files in dictionary order:
   - `images/01.png`
   - `images/02.png`
   - `images/03.png`
   - ...
7. Do not overwrite `images/99_end_card.png` if it already exists.

## Prompt Rules

- Prefer concrete scenes over abstract slogans.
- Avoid text-heavy designs.
- Use enough negative space for captions.
- Avoid tiny unreadable UI dashboards.
- For enterprise AI topics, prefer strategy rooms, workflow maps, sales/customer/operations scenes, human plus AI collaboration, and growth curve metaphors.

## Verification

After generation:
- Confirm every expected file exists.
- Check image dimensions and non-zero file size.
- Ensure filenames are ordered correctly.
- Visually inspect representative frames when possible.

## Final Report

Report the number of images, output directory, model used (`gpt-image-2-medium`), and any failed prompt or fallback.
