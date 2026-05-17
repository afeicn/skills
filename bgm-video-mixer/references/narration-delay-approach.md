# 口播延迟方案（adelay vs concat）

## 问题背景

BGM 混音时需要将口播和 BGM 对齐。时间线如下：

```
0s ─── 2.3s ─── 3.0s ─────────────────── video_dur ── +0.5s ── +2.2s
intro      gap        BGM music播放                   gap     outro
                      口播从此处开始
```

口播需要从 3.0s 开始播放，但原始 narration.wav 是从 0s 开始的。

## ❌ 旧方案：concat + anullsrc（有噪音）

在 narration 前/后拼数字静音垫片：

```
[anullsrc 3.0s] + [narration.wav] + [anullsrc 2.2s]
```

**问题**：ffmpeg `concat` 滤镜在拼接 anullsrc（数字零值 PCM）和真实 PCM WAV 时，
会在拼接处引入约 -58 dB 的底噪。虽然绝对值很低，但人耳可清晰感知为背景噪音。

## ✅ 新方案：adelay（无噪音）

不拼接 narration，而是用 adelay 滤镜将其在混音时延后 3.0s：

```
filter: "[0:a]adelay=3000|3000[nar_delay];[nar_delay]volume=1.5[nar];[1:a]...amix..."
```

**优点**：
- 无拼接操作，静音间隙为 -91 dB（真正的数字静默）
- narration 原文件不做修改，保持缓存有效
- 延迟在混音时实时计算，不产生中间文件

## 效果对比

| 指标 | concat 方案 | adelay 方案 |
|------|------------|------------|
| 静音间隙底噪 | -58 dB（可闻） | -91 dB（不可闻） |
| 中间文件 | narration_padded.wav | 无 |
| 速度 | 需额外 ffmpeg 调用 | 单步混音完成 |
