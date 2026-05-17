---
name: bgm-video-mixer
description: 为竖版短视频添加背景音乐 — 个性化开场音 + 背景轻音乐 + 标志性结尾音效。自动根据内容分析情绪选择曲风（欢快/舒缓/专业/激励），从 Mixkit 免费音乐库下载。支持 ffmpeg 合成开场/结尾音效（无需联网）。
---

# BGM Video Mixer

## 功能

为已合成的视频（含口播配音和字幕）添加：
1. **开场品牌音** — 0~2.3s，3 音上行钟声（C-E-G），个性化标志。**之后 0.7s 停顿，口播从 3.0s 才开始，不叠加**。
2. **背景轻音乐** — 3.0s 到口播结束，15% 低音量循环，自动根据内容选曲
3. **结尾标志音** — 口播结束后 0.5s 停顿，然后 G-E-C 下行"叮"（1.7s），落在"点赞收藏加关注"之后

### 时间线设计

```
0s ─── 2.3s ── 3.0s ──────────────────── 97.6s ── 98.1s ─── 99.8s
│  🔔 钟声  │ 停顿  │  🗣️ 口播 + 🎵 BGM 15%  │ 停顿  │ 🔔 叮  │
│          │       │  口播音量 100% 不变       │       │        │
```

- 视频首尾帧冻结以匹配 padding 时长
- 口播通过静音垫片实现与钟声/叮零重叠

## 音乐来源

**Mixkit** — 免费可商用，无需署名，直链下载。

下载 URL 格式：`https://assets.mixkit.co/music/{id}/{id}.mp3`

### 预选曲库

| ID | 曲名 | 情绪 | 适用场景 |
|----|------|------|----------|
| 34 | Raising Me Higher | 🚀 活力 | AI 转型、效率工具、落地实践 |
| 33 | Motivating Mornings | ❤️ 激励 | 行动建议、方法论、鼓励 |
| 480 | Curiosity | 💼 专业 | 科技科普、深度分析（默认） |
| 22 | Piano Reflections | 🧘 舒缓 | 反焦虑、降温、理性思考 |
| 85 | Break Away | ⚡ 驱动 | 紧迫感、行动号召 |
| 150 | A Blue Day | 🌿 温暖 | 人文关怀、故事叙事 |
| 479 | The Boss | 🏢 稳重 | 企业战略、管理话题 |

## 情绪自动判断

分析 口播稿.md 内容关键词：

| 情绪 | 关键词 | 选中曲目 |
|------|--------|----------|
| 活力/科技 | 转型、效率、落地、工具、AI、数字 | Raising Me Higher (34) |
| 舒缓/反焦虑 | 焦虑、别急、没关系、慢慢、放松 | Piano Reflections (22) |
| 激励/行动 | 建议、行动、试试、开始、推荐 | Motivating Mornings (33) |
| 专业/稳重 | 企业、战略、管理、标准、架构 | The Boss (479) |
| 温暖/人文 | 故事、经历、朋友、真实 | A Blue Day (150) |
| 默认 | — | Curiosity (480) |

## 环境要求

- ffmpeg（Homebrew 版即可）
- Python 3
- 网络连接（下载音乐），离线时用 ffmpeg 合成音效兜底

## 使用方式

```bash
# 在包含 output_video.mp4 的工作目录下运行
cp ~/.hermes/skills/creative/bgm-video-mixer/scripts/add_bgm.py .
python3 add_bgm.py [--mood auto|upbeat|calm|professional|motivating|warm]
```

### 输入

- `video_output/output_video.mp4` — 已合成的视频（含口播配音+字幕）
- `口播稿.md` — （可选）用于情绪分析

### 输出

- `video_output/output_video_bgm.mp4` — 添加了 BGM 的最终视频
- `video_output/bgm/` — 中间产物（音乐文件、混合音轨）

## 音量设计

| 音轨 | 处理方式 | 说明 |
|------|----------|------|
| 口播配音 | volume=1.5（轻微增益） | 不加过多的增益以免放大 VoxCPM2 建模底噪。1.5× 在人耳可接受范围内，2× 以上底噪开始明显。 |
| 开场音 | 60% → 混合前 bake | 有存在感，不压配音 |
| 背景音乐 | 15% → 混合前 bake | 若有若无，不抢注意力 |
| 结尾音 | 50% → 混合前 bake | 温和收束 |

### ⚠️ 噪音陷阱（重要历史教训）

**问题根源**：VoxCPM2 输出的 PCM 音频在句间停顿处底噪为 -49 ~ -53 dB（干净），但**说话时的建模过程会引入不可消除的背景噪音**（约 -25 dB 量级）。 

**曾经尝试过的方案及结论**：
- ❌ `volume=3.0`（固定增益 +9.5 dB）→ 建模噪音同步放大，用户明显可闻 ❌  
- ❌ `loudnorm=I=-16`（EBU R128 标准化）→ 把静音段当"需要提升的音量"给抬上来了，比固定增益更糟 ❌  
- ✅ **volume=1.0（原音直出）** → 不加任何增益，噪音不被人耳感知，但人声偏小 ✅  
- ✅ **volume=1.5（当前最佳）** → 轻微增益，在噪音可接受范围内提升人声清晰度 ✅
- ❌ `volume=2.0` 及以上 → 底噪开始明显可闻 ❌

**核心原则**：VoxCPM2 的建模噪音只在增益后被感知为"噪音"。当前最佳实践为 volume=1.5，既提升人声又不暴露底噪。其他修复措施（跳过 AAC 重编码、使用原始 PCM、adelay 替代 concat）一并保留。

**诊断方法**：当用户反馈新的噪音时，使用 `references/systematic-noise-diagnosis.md` 中的 4 版本对比法逐步隔离变量，避免臆测。|

## ffmpeg 音效合成（离线兜底）

开场音（C-E-G 上行钟声）：
```bash
ffmpeg -y -f lavfi -i "
  sine=f=523.25:d=0.6,adelay=0:all=1[s1];
  sine=f=659.25:d=0.6,adelay=600:all=1[s2];
  sine=f=783.99:d=1.2,adelay=1200:all=1[s3];
  [s1][s2][s3]amix=inputs=3:duration=longest,afade=t=in:d=0.1,afade=t=out:st=2.2:d=0.3
" bgm/intro.wav
```

结尾音（G-E-C 下行"叮" + 渐弱）：
```bash
ffmpeg -y -f lavfi -i "
  sine=f=783.99:d=0.8,adelay=0:all=1[s1];
  sine=f=659.25:d=0.8,adelay=200:all=1[s2];
  sine=f=523.25:d=1.5,adelay=400:all=1[s3];
  [s1][s2][s3]amix=inputs=3:duration=longest,afade=t=in:d=0.05,afade=t=out:st=1.5:d=0.5
" bgm/ending.wav
```

### 音频混合流程

```
1. 下载/确认 BGM 音乐 → bgm/music.mp3
2. 合成开场音 → bgm/intro.wav (2.3s)
3. 合成结尾音 → bgm/ending.wav (1.7s)
4. 使用原始 PCM 口播配音 → video_output/narration.wav（来自 VoxCPM2，跳过 AAC 重编码）
5. 构建完整 BGM 音轨：
   [intro 2.3s] + [gap 0.7s] + [music loop (volume=0.15)] + [gap 0.5s] + [ending 1.7s]
   ↓ bgm_track.wav（含间隙，保证钟声不叠口播）
6. 口播 用 adelay 延后 3s（替代旧方案的 concat 静音垫片，消除拼接噪音）：
   ↓ narration_delayed.wav（与原narration.wav内容相同，仅延后3.0s）
7. 视频延展：冻结首帧 3.0s + 原视频 + 冻结尾帧 2.2s
   ↓ padded_video.mp4
8. 混合音频（normalize=0，duration=longest 以保留BGM结尾）：
   narration_delayed + bgm_track
   ↓ mixed_audio.wav
9. 替换视频音轨 → output_video_bgm.mp4
```

**CRITICAL: 禁止使用 concat 拼静音垫片** — ffmpeg 的 `concat` 滤镜在拼接 anullsrc(静音) 和 narration 时会引入底噪（约 -58 dB）。**必须使用 `adelay` 滤镜**将口播音频延后 3.0s，然后与带开场钟声的 bgm_track 直接混音。静音间隙在 -91 dB（数字静默级别）。详见 `references/narration-delay-approach.md`。

**CRITICAL: amix normalize=0** — ffmpeg 的 `amix` 滤镜默认会做归一化，将每个输入音轨除以输入数量。2 轨输入时，口播掉到 50%、BGM 掉到 50%。必须加 `normalize=0` 参数阻止此行为。|
```

## 注意事项

- 音乐通过 `curl` 下载，超时 30 秒，失败自动回退离线模式
- 离线模式使用 ffmpeg 生成简单旋律做背景（正弦波 + 包络）
- 同时支持通过 `--bgm <path>` 手动指定音乐文件
- 同时支持通过 `--no-bgm` 仅添加开场/结尾音效
- **口播与钟声不重叠**：脚本自动为口播加 3s 前导静音 + 2.2s 尾随静音，视频首尾帧冻结
- amix 使用 `normalize=0` 防止口播被压音量
- BGM 音量已 bake 进 BGM track，混音时用 `amix:normalize=0` 保证口播 100%
- **⚠️ 噪音陷阱**：VoxCPM2 原始输出为 PCM WAV（~27MB），说话时建模底噪约 -25 dB。**关键是不要施加过多音量增益**（volume=3.0 或 loudnorm 都会大幅放大此噪音）。当前最佳实践为 volume=1.5 轻微增益，用户再通过设备音量微调。详见此表上方的"噪音陷阱"章节。
