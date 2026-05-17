# ffmpeg amix 滤镜归一化陷阱

## 问题

`amix` 滤镜默认会对所有输入音频做**等权归一化**：

```bash
amix=inputs=2:duration=first
```

等效于每个输入的音量被除以输入数量(÷2)。这意味着：
- 口播从 100% 掉到 50%
- BGM 从 bake 后的音量再被 ÷2，实际只有一半
- **结果**：口播变轻，BGM 几乎听不到，用户感觉"没区别"

## 修复

必须加 `normalize=0`：

```python
run(f'ffmpeg -y '
    f'-i {narration_wav} '
    f'-i {bgm_track} '
    f'-filter_complex "[1:a]aformat=channel_layouts=mono[bgm_mono];'
    f'[bgm_mono]asplit[bgmL][bgmR];'
    f'[bgmL][bgmR]amerge=inputs=2,volume=1.0[bgm_stereo];'
    f'[0:a][bgm_stereo]amix=inputs=2:duration=first:normalize=0[aout]" '
    f'-map "[aout]" -ar 48000 -ac 2 {mixed_audio}')
```

## 验证

```bash
# 原版
ffmpeg -i original.mp4 -vn -t 5 /tmp/s1.wav && ffmpeg -i /tmp/s1.wav -af volumedetect -f null /dev/null 2>&1 | grep mean_volume
# BGM版（normalize=0，音量应比原版高 ~3dB）
ffmpeg -i bgm.mp4 -vn -t 5 /tmp/s2.wav && ffmpeg -i /tmp/s2.wav -af volumedetect -f null /dev/null 2>&1 | grep mean_volume
```

如果 BGM 版音量更低，说明 normalize 没生效。
