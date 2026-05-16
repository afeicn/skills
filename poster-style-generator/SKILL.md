---
name: poster-style-generator
description: 海报风格生成器。Generate a vertical Chinese short-video cover and matching end card with OpenAI gpt-image-2.
---

# Poster Style Generator / 海报风格生成器

## Purpose

Generate only the cover poster and end card:
- Cover / 封面: title-forward poster for click appeal.
- End card / 封底: CTA for 关注 / 点赞 / 收藏.

Body video illustrations belong to `video-illustration-generator`.

## Required Model

Always generate images with OpenAI `gpt-image-2`.

Use the image generation tool with:
- model: `openai/gpt-image-2`
- ratio: 3:4
- preferred size: `1024x1536`
- format: png

Do not use the ambiguous `image2` alias.

## Inputs

Required:
- Video title.
- Topic or script summary.

Recommended:
- Style number from the 10 poster styles.
- Shared visual direction for the whole video.
- Target platform: 视频号, 小红书, 抖音, or generic vertical video.

## Style Slots

1. 高级商务杂志风
2. 科技增长蓝
3. 黑金战略感
4. 新中式理性风
5. 极简白底观点风
6. 温暖访谈纪实风
7. 数据图表决策风
8. 深色霓虹 AI 风
9. 红蓝冲突辩题风
10. 小红书醒目标题风

## Workflow

1. Read the title and topic/script.
2. Select or confirm one style slot.
3. Generate `cover.png` with `openai/gpt-image-2`.
4. Generate `end_card.png` with `openai/gpt-image-2`.
5. If the end card should appear in the video, also save it as `images/99_end_card.png`.

## Quality Rules

- Cover, end card, and body illustrations must share the same visual direction.
- Keep Chinese text large and readable.
- Avoid tiny paragraphs, QR codes, or dense UI.
- The end card should stay clean enough to append after the captioned video.

## Final Report

Report the selected style, output paths, model used, and any generation failure.
