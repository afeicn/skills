# Audio Noise Troubleshooting Guide

## 问题三要素

用户反馈"视频有噪音"时，必须确认三件事：

1. **单独的配音文件有没有噪音？**（narration.wav）
2. **单独的 BGM 文件有没有噪音？**（bgm_track.wav）
3. **最终混合视频有没有噪音？**（output_video_bgm.mp4）

## 实测发现的根因

VoxCPM2 说话时会引入约 -25 dB 的**建模噪音**（句间停顿处干净，-49 dB）。这是模型本身的特性，非外部干扰。

**任何形式的音量增益都会放大此噪音**：
- `volume=3.0` (+9.5 dB) → 噪音放大到 -15.5 dB → 明显可闻
- `loudnorm=I=-16` (EBU R128) → 静音段也被抬到 -28 dB → 比固定增益更糟

**最终方案**：`volume=1.0` 原音直出。不施加任何增益，用户通过设备音量自行调节。

## 诊断步骤

### Step 1: 确认是否为增益导致的噪音

```bash
# 分离测试：不用 BGM，只听原始 narration + volume 测试
# 比较以下三个命令的输出
ffmpeg -i narration.wav -t 5 /tmp/raw_voice.wav                    # 原始声
ffmpeg -i narration.wav -af "volume=3.0" -t 5 /tmp/vol3_voice.wav  # 放大后
ffmpeg -i narration.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" -t 5 /tmp/loudnorm_voice.wav  # 标准化后

# 检查原始句间停顿的干净程度（应在 -45 dB 以下）
ffmpeg -y -i narration_chunk_1.wav -af "aselect='between(t,5.59,5.75)',asetpts=N/SR/TB" /tmp/gap.wav
ffmpeg -i /tmp/gap.wav -af "volumedetect" -f null - 2>&1 | grep mean_volume
```

### Step 2: 检查 add_bgm.py 配置

```bash
# 确认口播音量设置
grep "volume=" add_bgm.py | head -1
# 应为 volume=1.0（原音直出）
```

### Step 3: 终极排查 — 三版本对比

让用户对比以下三个文件：

1. **narration_only_video.mp4** — narration.wav 直出，无 BGM、无增益、无处理
2. **mixed_audio.wav** — 混音后 PCM（AAC 编码前）
3. **output_video_bgm.mp4** — 完整 BGM 版

- 1 有噪音 → VoxCPM2 输出本身有问题
- 1 干净、2 有噪音 → 混音过程引入
- 1+2 干净、3 有噪音 → AAC 编码引入
- 1 干净、2+3 有噪音 → **音量增益放大了 VoxCPM2 建模噪音**（最常见）

## 噪音症状对照

| 噪音特征 | 可能原因 | 修复 |
|----------|---------|------|
| 说话时轻微嘶声（句间不响） | VoxCPM2 建模噪音被 volume 放大 | volume=1.0 原音直出 |
| 连续嘶声（句间也有） | AAC 量化噪音 | 用原始 PCM narration.wav |
| 低频嗡嗡声 | 参考音频有噪音 | ref.wav 用 highpass=f=80 滤波 |
| 喀嗒/爆音 | chunk 拼接不连续 | 检查 concat 过程 |
