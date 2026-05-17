---
name: poster-style-generator
description: 海报风格生成器。Generate a vertical Chinese short-video cover and matching end card via Hermes image_gen tool.
---

# Poster Style Generator / 海报风格生成器

## Purpose

Generate only the cover poster and end card:
- Cover / 封面: title-forward poster for click appeal.
- End card / 封底: CTA for 关注 / 点赞 / 收藏.

Body video illustrations belong to `video-illustration-generator`.

## Image Generation

Use Hermes `image_generate` tool. The provider and model are pre-configured in config.yaml:

| Config key | Value |
|------------|-------|
| `image_gen.provider` | `openai-codex` (OAuth, no API key needed) |
| `image_gen.model` | `gpt-image-2-medium` |
| `image_gen` toolset | Must be enabled (`hermes tools`) |

Call `image_generate` with `aspect_ratio="portrait"` for 1024x1536 output.

## Universal Design Rule（通用设计铁律）

**所有封面都是纯文字排版，不配图、不装饰。** 风格之间的区别只是配色和字体气质不同。

### 排版统一要求

- ✅ **满屏大标题** — 标题文字撑满整张画面，不留大片空白
- ✅ **无配图/无装饰** — 不要插图、图标、渐变背景、几何图形。**仅纯文字**
- ✅ **错落有致** — 多行错位、大小穿插，制造视觉节奏感
- ✅ **手写/有冲击力的字体** — 手写体、霹雳体、榜书体、楷体等。不用常规黑体/宋体
- ✅ **留白呼吸** — 文字之间有空隙，不拥挤

### 排版结构参考

```
┌──────────────────────────┐
│                          │
│    企 业    做  AI      │ ← 大号，偏左
│                          │
│    千 万    不 要        │ ← 超大号，居中
│                          │
│    一  上  来  就         │
│                          │
│    全 员 铺 工 具         │ ← 小号，偏右，错位
│                          │
│         —— 飞哥说         │ ← 落款小字
└──────────────────────────┘
```

## Style Slots（配色/字体风格，共 10 套）

以下风格共享上述纯文字排版规则，区别仅在于**配色方案和字体气质**。

### 1. 高级商务杂志风
- **配色**：深蓝 + 米白 + 少量金色
- **字体气质**：端庄楷体 / 宋体变体，稳重
- **背景**：纯白或浅米色底
- **适用**：管理、战略、企业话题

### 2. 科技增长蓝
- **配色**：科技蓝 + 白色 + 青色(#00D7FF)高亮
- **字体气质**：现代感字体，利落有力
- **背景**：深蓝渐变底
- **适用**：AI、数字化转型、效率工具

### 3. 黑金战略感
- **配色**：黑色 + 金色 + 深红
- **字体气质**：榜书体/厚重字体，霸气
- **背景**：纯黑或深灰底
- **适用**：战略、破局、重大判断

### 4. 新中式理性风
- **配色**：墨绿/赭石 + 米白 + 朱砂红
- **字体气质**：书法体/行楷，有文化感
- **背景**：浅宣纸色或米白底
- **适用**：人文、管理哲学、职场洞察

### 5. 极简白底观点风
- **配色**：纯黑 + 白色 + 单一强调色
- **字体气质**：简洁有力的大标题体
- **背景**：纯白底，极致干净
- **适用**：直给观点、反常识结论

### 6. 温暖访谈纪实风
- **配色**：暖橙/驼色 + 米白 + 深灰
- **字体气质**：手写体/圆润字体，亲切
- **背景**：暖白渐变底
- **适用**：故事、访谈、真人分享

### 7. 数据图表决策风（保留命名，但仍是纯文字）
- **配色**：深灰蓝 + 酸橙绿 + 白色
- **字体气质**：干净利落的现代字体
- **背景**：深色底
- **适用**：方法论、框架、决策类

### 8. 深色霓虹 AI 风
- **配色**：纯黑 + 霓虹紫/蓝 + 白色
- **字体气质**：未来感字体，带发光效果
- **背景**：纯黑底
- **适用**：AI前沿、未来趋势

### 9. 红蓝冲突辩题风
- **配色**：红色 + 蓝色 + 白色（对比强烈）
- **字体气质**：粗犷有力的大标题
- **背景**：纯白或浅灰底
- **适用**：辩题、矛盾观点、"别再…"

### 10. 小红书醒目标题风
- **配色**：亮橙/粉红 + 白色 + 深灰
- **字体气质**：可爱手写体/圆体，有亲和力
- **背景**：纯白或浅粉底
- **适用**：轻松话题、个人经验、建议类

## Workflow

1. Read the title and topic/script.
2. Select one style (1-10) based on topic mood and user preference.
3. Build prompt using the universal typography rule + specific style's color/font scheme.
4. Generate `cover.png` with `image_generate(aspect_ratio="portrait", prompt="...")`.
5. Generate `end_card.png` with `image_generate(aspect_ratio="portrait", prompt="...")`.
6. If the end card should appear in the video, also save it as `images/99_end_card.png`.

### Prompt 构建公式

所有 prompt 遵循统一结构：

```
[Aspect ratio instruction] + [Universal typography rule] + [Style color/font spec] + [Title text layout]
```

**示例（风格2 - 科技增长蓝）：**
```
Vertical portrait poster, ONLY Chinese typography filling the entire frame.
No images, no illustrations, no icons, no decorations. Pure text only.
Modern tech aesthetic: deep blue gradient background, white and cyan (#00D7FF)
characters. Clean, bold display font. Staggered layout with varying character sizes.
Title "企业做AI千万不要一上来就全员铺工具" arranged in 3-4 lines
with oversized and medium contrast. "——飞哥说" as small signature at bottom.
High-impact, minimal, like a tech keynote title slide.
```

### 封底（end_card）

封底固定格式，纯文字排版：
```
┌──────────────────────────┐
│                          │
│     👍 点赞  ⭐ 收藏       │
│     🔔 加关注              │
│                          │
│      我们下期见！          │
│          —— 飞哥          │
└──────────────────────────┘
```
配色与封面保持一致。无配图。

## Final Report

Report the selected style (number + name), output paths, and any generation failure.
