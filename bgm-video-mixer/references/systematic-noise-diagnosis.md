# 音频噪音定位 — 系统对比法

## 原理

当用户反馈"视频有噪音"时，仅通过 volumedetect 分析无法定位根因。
必须通过**逐步隔离变量**的对比测试来锁定噪音引入环节。

## 标准对比流程

### Step 1: 创建 4 个诊断版本

假设当前工作目录是视频项目目录（含 `video_output/`）：

```bash
# 版本A: 原始 narration.wav 直存 MP4（完全无处理）
# 从视频提取画面 + 原始 PCM 音频
ffmpeg -y -i video_output/output_video.mp4 \
  -i video_output/narration.wav \
  -c:v copy -map 0:v:0 -map 1:a:0 -c:a aac -b:a 160k \
  video_output/diag_A_raw.mp4

# 版本B: 版本A + 仅加 BGM 音轨（无增益、无垫片）
ffmpeg -y -i video_output/diag_A_raw.mp4 \
  -i video_output/bgm/bgm_track.wav \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:normalize=0[aout]" \
  -map 0:v:0 -map "[aout]" -c:v copy -c:a aac -b:a 160k \
  video_output/diag_B_bgm_only.mp4

# 版本C: 版本A + 仅重编码 AAC（无 BGM、无增益）
ffmpeg -y -i video_output/diag_A_raw.mp4 \
  -c:v copy -c:a aac -b:a 160k \
  video_output/diag_C_reencode.mp4

# 版本D: padded_video + 原始 narration + BGM（跳过静音垫片）
ffmpeg -y -i video_output/padded_video.mp4 \
  -i video_output/narration.wav \
  -i video_output/bgm/bgm_track.wav \
  -filter_complex "[1:a][2:a]amix=inputs=2:duration=first:normalize=0[aout]" \
  -map 0:v:0 -map "[aout]" -c:v copy -c:a aac -b:a 160k \
  video_output/diag_D_nopad.mp4
```

### Step 2: 让用户听并反馈

| 版本 | 内容 | 典型结论 |
|------|------|----------|
| A 🟢 | raw narration → MP4 | 有噪音 → VoxCPM2 自身问题 |
| B 🟡 | A + BGM track | 有噪音 → BGM 或 amix 混音问题 |
| C 🟢 | A + AAC re-encode | 有噪音 → AAC 编码器问题 |
| D 🟠 | padded_video + raw narration + BGM | 有噪音 → padded_video 视频 concat 问题 |

### Step 3: 根据结论进一步缩小

**场景 1**: A✅ B✅ C✅ D❌ → **concat 静音垫片问题**
   - 对比: D 用的是原始 narration.wav + BGM（跳过静音垫片）
   - 完整版用的是 narration_padded.wav = [anullsrc] + [narration.wav] + [anullsrc]
   - 修复: 改用 `adelay` 替代 concat 静音垫片

**场景 2**: A✅ B✅ C✅ D✅ 但完整版❌ → **静音垫片 + volume 增益双重问题**
   - 检查 add_bgm.py 中是否设置了 volume>1.0 或 loudnorm
   - 尝试 volume=1.0 原音直出

**场景 3**: A✅ B❌ → **BGM 轨道本身有噪音**
   - 单独检查 bgm_track.wav 各段（intro, gap, music, gap, ending）
   - Mixkit MP3 本身可能有问题 → 换曲目或下载源

**场景 4**: A✅ C❌ → **AAC 编码问题**
   - 试不同 bitrate (128k, 192k, 256k)
   - 试不同 AAC 编码器 (aac_at vs aac)
   - ffmpeg -c:a aac_at (Apple Audio Toolbox) 音质通常更好

### Step 4: 确认修复

修改后，用 volumedetect 验证静音间隙：

```bash
# concat 方案（预期 -58 dB）
ffmpeg -y -i bgm/mixed_audio.wav -af "aselect='between(t,2.5,2.8)',asetpts=N/SR/TB" /tmp/gap.wav
ffmpeg -i /tmp/gap.wav -af "volumedetect" -f null - 2>&1 | grep mean_volume
# → 期望值 ≤ -85 dB（数字静默级别）
```

## 噪音特征对照表

| 特征 | 用户描述 | 大概率根因 |
|------|----------|-----------|
| 说话时的轻微嘶声（句间安静） | "背景有沙沙声" | volume 增益放大了 VoxCPM2 建模噪音 |
| 持续的嘶声（句间也有） | "一直有噪音" | concat 拼静音垫片引入，或 AAC 量化噪音 |
| 喀嗒声/爆音 | "噼啪响" | 音频 chunk 拼接不连续 |
| 低频嗡嗡声 | "有嗡嗡声" | 参考音频 ref.wav 带交流噪音 |
| 金属声/碰撞声 | "声音发脆" | AAC 编码 bitrate 过低 |
