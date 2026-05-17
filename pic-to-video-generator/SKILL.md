---
name: pic-to-video-generator
description: 自动将一组图片和纯口播稿转换为带有动效、VoxCPM2 真人配音、霞鹜文楷高亮字幕的竖版短视频。支持绿幕抠像字幕（无需 libass）、关键词高亮、分片配音。
---

# Pic-to-Video Generator

将图片 + 口播稿全自动转化为高质量竖版短视频。包含动效、VoxCPM2 分片配音、霞鹜文楷自适应字幕（含关键词高亮）。

## 环境要求

1. **Node.js** + **FFmpeg**（Homebrew 版即可，无需 libass）
2. **Python 3** + Pillow（`pip3 install Pillow`）
3. **LXGW WenKai 字体**（霞鹜文楷）— 需手动下载
4. **VoxCPM2** 本地已部署

## 前置准备

工作目录下准备：
- `images/` 目录，图片按字典序命名（`00_cover.png`, `01.png`, ..., `99_end_card.png`）
- `口播稿.md` — **纯口播文案**，不得含标题/时间戳/markdown。用空格控制节奏。

环境变量（音频生成用）：
- `VOXCPM_BIN` — VoxCPM2 可执行文件路径（如 `/Users/liuwei/.local/miniforge3/envs/voxcpm2/bin/voxcpm`）
- `VOXCPM_REF_AUDIO` — 参考音频（克隆音色用）

## 完整流程

### 1. 生成图片（通过 gpt-image-2 等工具）
封面 + 6-8张插图 + 封底，均为 1024×1536（竖版 2:3），统一风格。

### 2. 准备口播稿
纯文本格式，无任何注释标签。示例：
```
上一期我讲到， 企业做 AI 转型， 千万不要一上来就全员铺工具。

那接下来问题就来了：
如果不全员铺开， 第一步到底该从哪开始？
```

⚠️ **严禁**：标题行、时间戳、`**加粗**` 标记、Markdown 标题。这些都不可出现。

### 3. 获取参考音频（ref.wav）
如果没有预先录制的参考音频，让用户通过飞书发送语音消息：
1. 语音文件在 `~/.hermes/audio_cache/audio_*.m4a`
2. 转换：`ffmpeg -y -i <m4a> -ar 16000 -ac 1 ref.wav`
3. 复制到 `video_output/ref.wav`

没有参考音频时可用 `voxcpm design` 模式（效果不如克隆）：
```bash
voxcpm design --text "测试" --control "专业沉稳的男声" --output ref.wav
```

### 4. 安装字体
```bash
curl -L -o ~/Library/Fonts/LXGWWenKai-Regular.ttf \
  "https://github.com/lxgw/LxgwWenKai/releases/download/v1.522/LXGWWenKai-Regular.ttf"
```
备选：`/System/Library/Fonts/STHeiti Medium.ttc`（系统黑体，无需下载）
### 4. 复制合成脚本并执行

```bash
cp ~/.hermes/skills/creative/pic-to-video-generator/scripts/synthesize.py ./synthesize.py
```

**⚠️ 重要：编辑 `HIGHLIGHTS` 列表** — 在 `synthesize.py` 中找到 `HIGHLIGHTS` 列表，根据本期口播稿内容替换为需要高亮的关键词（长串优先）。

**可选：口播倍速** — 如需加速口播（如 1.2 倍速），编辑 `synthesize.py` 中的 `atempo=1.2` 参数（位于 STEP 1 末尾）。默认为不加速（即不执行 atempo 块）。修改后删除缓存 `video_output/narration.wav` 再执行。

然后执行：
```bash
python3 synthesize.py
```

脚本自动执行：
1. VoxCPM2 分片配音（~120字/段，按句号切割，防止噪音）
2. **可选：atempo 倍速处理** — 口播音频按指定倍速加速（如 1.2x），同时字幕和幻灯片自动适配加速后的时长
3. 图片幻灯片（封面→插图→封底，缩放+模糊背景+推拉动效）
4. 字幕渲染（霞鹜文楷 46px + 白字灰描边 + 关键词青色高亮）
5. **中文禁则处理** — 字幕断句检查标点不出现在行首（`LINE_START_BAD` 集合）
6. **连续时序** — 字幕均匀分布于全部口播时长（无间隙，覆盖 100%）
7. 绿幕抠像叠加 → 最终合成 `video_output/output_video.mp4`

## 音频分片机制

- 口播稿按句号 `。！？` 边界切分为 ~120字一段（约30秒语音）
- 逐段调用 VoxCPM2 生成 → 转为 WAV → ffmpeg concat 拼接
- 每段独立缓存：只改字幕时无需重跑 VoxCPM2
- 超长句在逗号/分号处智能切分

## 字幕技术方案（绿幕抠像）

Homebrew ffmpeg 不编入 `libass`，且 `libx264` 不支持 `yuva420p`（alpha通道）。

采用 **绿幕抠像** 方案：
1. 字幕渲染在纯绿底（#00FF00）上
2. 白色文字 + 灰色描边 + 暗绿底色块
3. 关键词（"AI 转型"等9个）用青色（#00D7FF）高亮
4. 最终合成用 `colorkey` 滤镜去除绿色：
   ```
   -filter_complex "[1:v]colorkey=0x00FF00:0.2:0.1[sub];[0:v][sub]overlay=format=auto[outv]"
   ```

详见 `references/subtitle-fallback.md`。

## ⚠️ 常见陷阱

1. **口播稿含 `\n` 换行符** → 必须先 `replace('\n', ' ')` 再解析字幕，否则排版错乱
2. **ffmpeg 用 `yuva420p`** → 静默回退为 `yuv420p`，字幕层变纯黑覆盖画面！必须用 yuv420p + colorkey
3. **图片排序** → 文件名决定顺序：`00_cover.png` < `01.png` < `99_end_card.png`
4. **字体不存在** → `/System/Library/Fonts/PingFang.ttc` 路径错误！PingFang 在 `/System/Library/AssetsV2/...` 长路径下，改用 LXGW WenKai 或 STHeiti Medium
5. **音频噪点/杂音** → 
   - **VoxCPM2 自身噪音**：检查 ref.wav 质量。飞书语音消息若环境嘈杂，clone 模式会忠实还原噪声。解决方案：换安静环境下的语音消息，或用 `voxcpm design` 控制语气
   - **AAC 重编码噪音**（更常见）：当 BGM 混音从 AAC 视频提取音频 + volume=3.0 时，量化噪音被放大。解决方案：`add_bgm.py` 现已直接从原始 PCM `narration.wav` 读取，跳过 AAC 编解码。参见 bgm-video-mixer skill 的注意事项
6. **字幕断句标点出现在行首** → `word_wrap` 函数在 max_chars 处硬断时，若下个字符是标点（。，！？；等），会违反中文禁则。**修复**：`word_wrap` 已加入禁则检查 —— 断点后首个字符若为禁则标点，前移断点或吸收到当前行。详见 `synthesize.py` 中的 `LINE_START_BAD` 集合。
7. **音频重新生成** → 除非修改了口播稿，否则 narration.wav 有缓存，不要重跑 VoxCPM2

## VoxCPM2 环境排查

- 路径用 `VOXCPM_BIN` 直接指向 bin/voxcpm，不用 `source activate`
- MPS 设备（Apple Silicon）可用，`--inference-timesteps 10` 默认
- HF 镜像：`export HF_ENDPOINT=https://hf-mirror.com`
- 模型缓存：`~/.cache/huggingface/hub/models--openbmb--VoxCPM2/`

## 关键词高亮列表（示例 — 每期视频自行编辑）

以下短语会被渲染为青色高亮（按长串优先匹配）。**每期视频需根据口播稿内容自定义**：

示例：
- 智能问答
- 评测集
- 财务共享
- 自动评测
- 人工评测
- 标准答案

**⚠️ 排序规则**：长短语放前面，短视频放后面。脚本用 `sorted(HIGHLIGHTS, key=len, reverse=True)` 确保长优先匹配，比如"答得不准"会在"不准"之前匹配。

## 视觉规格

- 分辨率：720×1280（9:16 竖屏）
- 图片适配：缩放+模糊背景+居中+推拉动效
- 字幕字体：霞鹜文楷 46px，行距 56px
- 字幕位置：距底部 300px（上移约3行文字高度，避免被遮挡）
- 字幕底色：半透明黑（暗绿底经抠像后呈现透明度）
- 高亮色：青色 #00D7FF
- 描边：淡灰 (180,180,180) 1px 四向偏置
- FPS：24，编码：H.264 + AAC 160k
