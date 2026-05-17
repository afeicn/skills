# 音频噪音诊断流程（实测经验）

## 已知根因

**VoxCPM2 说话段的建模噪音**：VoxCPM2 在生成语音时会引入约 -25 dB（RMS）的背景建模噪音。句间停顿处底噪仅为 -49 ~ -53 dB（干净），但**说话期间**的建模噪音不可消除。

**触发条件**：任何形式的音量增益（volume=3.0 / loudnorm）都会将此 -25 dB 的建模噪音同步放大到 -15 ~ -18 dB，用户明显可闻。

**最终解决方案**：`volume=1.0` 原音直出，不施加任何增益。用户通过设备音量自行调节。

## 快速排查流程

### 1. 确认是否是增益导致的噪音

创建三个对比版本让用户听：

```
版本1: narration.wav 直出MP4（无BGM、无增益、无处理）
版本2: mixed_audio.wav（混音后PCM，无AAC编码）
版本3: output_video_bgm.mp4（完整BGM版）
```

- 版本1 有噪音 → VoxCPM2 输出本身有噪音（少见）
- 版本1 干净、版本2 有噪音 → 混音过程引入
- 版本1+2 干净、版本3 有噪音 → AAC 编码引入
- 版本1 干净、版本2+3 有噪音 → **典型 = 音量增益放大了 VoxCPM2 建模噪音**

### 2. 诊断命令

```bash
# 查看音量分布
ffmpeg -i <file> -af "volumedetect" -f null - 2>&1 | grep -E "mean_volume|max_volume"

# 检测句间静音段（确认是否干净）
ffmpeg -i narration.wav -af "silencedetect=noise=-50dB:d=0.1" -f null - 2>&1 | head -10

# 提取句间静音段测底噪
ffmpeg -y -i narration_chunk_1.wav -af "aselect='between(t,5.59,5.75)',asetpts=N/SR/TB" gap_sample.wav
ffmpeg -i gap_sample.wav -af "volumedetect" -f null - 2>&1 | grep mean_volume
# 正常值应 ≥ -45 dB

# 检查说话段底噪（识别建模噪音）
ffmpeg -y -i narration.wav -af "aselect='between(t,30,35)',asetpts=N/SR/TB" speech_sample.wav
ffmpeg -i speech_sample.wav -af "volumedetect" -f null - 2>&1 | grep mean_volume
# 典型 VoxCPM2 值: -25 ~ -21 dB（这就是建模噪音）
```

### 3. 验证 fix 是否生效

```bash
# 检查 add_bgm.py 中 narration 的 volume 参数
grep "volume=" add_bgm.py
# 必须显示 volume=1.0
```

## 曾经踩过的坑

| 方案 | 结果 | 原因 |
|------|------|------|
| `volume=3.0` | ❌ 噪音明显 | 建模噪音 -25 dB → 放大到 -15.5 dB |
| `loudnorm=I=-16` (EBU R128) | ❌ 更糟 | 把静音段当"需提升音量"抬到 -28 dB |
| `volume=1.0` + 原始 PCM | ✅ 干净 | 不放大，建模噪音保留在 -25 dB 不可闻 |
