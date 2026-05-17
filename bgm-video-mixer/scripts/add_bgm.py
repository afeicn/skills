#!/usr/bin/env python3
"""
BGM Video Mixer — 为竖版短视频添加背景音乐
1. 个性化开场音（ffmpeg 合成 3 音上行钟声）
2. 背景轻音乐（Mixkit 免费音乐，根据内容自动选曲）
3. 标志性结尾音（ffmpeg 合成下行"叮"声）

用法: python3 add_bgm.py [--mood auto|upbeat|calm|professional|motivating|warm] [--bgm <path>] [--no-bgm]
"""

import os, re, sys, subprocess, argparse

WORKDIR = os.getcwd()
VIDEO_DIR = f"{WORKDIR}/video_output"
BGM_DIR = f"{VIDEO_DIR}/bgm"
INPUT_VIDEO = f"{VIDEO_DIR}/output_video.mp4"
OUTPUT_VIDEO = f"{VIDEO_DIR}/output_video_bgm.mp4"
SCRIPT_MD = f"{WORKDIR}/口播稿.md"

os.makedirs(BGM_DIR, exist_ok=True)

# ─── Music Catalog (Mixkit free, commercial use, no attribution) ───
CATALOG = {
    "upbeat":       {"id": 34,  "name": "Raising Me Higher",  "desc": "活力/科技"},
    "motivating":   {"id": 33,  "name": "Motivating Mornings", "desc": "激励/行动"},
    "professional": {"id": 480, "name": "Curiosity",           "desc": "专业/科普(默认)"},
    "calm":         {"id": 22,  "name": "Piano Reflections",   "desc": "舒缓/反焦虑"},
    "driven":       {"id": 85,  "name": "Break Away",          "desc": "驱动/紧迫"},
    "warm":         {"id": 150, "name": "A Blue Day",          "desc": "温暖/人文"},
    "corporate":    {"id": 479, "name": "The Boss",            "desc": "企业/管理"},
}

DEFAULT_MOOD = "professional"

def run(cmd, check=True):
    """Run shell command, return CompletedProcess."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ⚠️  FAILED: {cmd[:120]}")
        if result.stderr:
            print(f"     {result.stderr.strip()[-300:]}")
    return result


def detect_mood_from_script():
    """Analyze 口播稿.md for mood keywords."""
    if not os.path.exists(SCRIPT_MD):
        return DEFAULT_MOOD

    with open(SCRIPT_MD, "r") as f:
        text = f.read()

    # Keyword scoring
    scores = {}
    mood_keywords = {
        "upbeat":       ["转型", "效率", "落地", "工具", "AI", "数字", "智能", "自动化"],
        "calm":         ["焦虑", "别急", "没关系", "慢慢", "放松", "降温", "冷静"],
        "motivating":   ["建议", "行动", "试试", "开始", "推荐", "去做", "先挑"],
        "professional": ["企业", "战略", "管理", "标准", "架构", "系统"],
        "warm":         ["故事", "经历", "朋友", "真实", "我自己"],
        "corporate":    ["公司", "团队", "组织", "流程", "部门"],
    }

    for mood, keywords in mood_keywords.items():
        scores[mood] = sum(text.count(kw) for kw in keywords)

    # Fall back to default if no strong signal
    if not any(scores.values()):
        return DEFAULT_MOOD

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return DEFAULT_MOOD
    return best


def download_music(mood):
    """Download background music from Mixkit catalog."""
    entry = CATALOG.get(mood, CATALOG[DEFAULT_MOOD])
    track_id = entry["id"]
    music_path = f"{BGM_DIR}/music_{track_id}.mp3"
    url = f"https://assets.mixkit.co/music/{track_id}/{track_id}.mp3"

    if os.path.exists(music_path) and os.path.getsize(music_path) > 1000:
        print(f"  ✅ 使用缓存: {entry['name']} ({entry['desc']})")
        return music_path

    print(f"  📥 下载: {entry['name']} ({entry['desc']})")
    result = run(f'curl -L -o "{music_path}" "{url}" --connect-timeout 10 --max-time 30', check=False)

    if result.returncode == 0 and os.path.exists(music_path) and os.path.getsize(music_path) > 1000:
        print(f"  ✅ 下载完成: {entry['name']}")
        return music_path

    print(f"  ⚠️  下载失败，回退到离线合成模式")
    return None


def generate_sine_wave(freq, duration, output):
    """Generate a sine wave tone using ffmpeg."""
    run(f'ffmpeg -y -f lavfi -i "sine=frequency={freq}:duration={duration}:sample_rate=48000" '
        f'-ac 1 -ar 48000 {output}', check=False)


def generate_intro():
    """Generate intro chime: C-E-G ascending (3-tone brand signature)."""
    intro_path = f"{BGM_DIR}/intro.wav"
    if os.path.exists(intro_path) and os.path.getsize(intro_path) > 1000:
        print(f"  ✅ 开场音 (缓存)")
        return intro_path

    print("  🔔 合成开场音 (C-E-G 上行钟声)...")

    c5 = f"{BGM_DIR}/_c5.wav"
    e5 = f"{BGM_DIR}/_e5.wav"
    g5 = f"{BGM_DIR}/_g5.wav"

    generate_sine_wave(523.25, 0.65, c5)  # C5
    generate_sine_wave(659.25, 0.65, e5)  # E5
    generate_sine_wave(783.99, 1.3, g5)   # G5

    # Compose: C5 at t=0, E5 at t=0.5s, G5 at t=1.0s, with fade in/out
    filter_expr = (
        f"[0:a]adelay=0:all=1,afade=t=in:d=0.08[a0];"
        f"[1:a]adelay=500:all=1,afade=t=in:d=0.08[a1];"
        f"[2:a]adelay=1000:all=1,afade=t=in:d=0.08[a2];"
        f"[a0][a1][a2]amix=inputs=3:duration=longest:weights=1 1 1.2,"
        f"afade=t=out:st=2.1:d=0.4,volume=0.6[aout]"
    )

    run(f'ffmpeg -y -i {c5} -i {e5} -i {g5} '
        f'-filter_complex "{filter_expr}" -map "[aout]" -ar 48000 {intro_path}')

    print(f"  ✅ 开场音合成完成")
    return intro_path


def generate_ending():
    """Generate ending chime: G-E-C descending (gentle ding)."""
    ending_path = f"{BGM_DIR}/ending.wav"
    if os.path.exists(ending_path) and os.path.getsize(ending_path) > 1000:
        print(f"  ✅ 结尾音 (缓存)")
        return ending_path

    print("  🔔 合成结尾音 (G-E-C 下行'叮')...")

    g5 = f"{BGM_DIR}/_g5_end.wav"
    e5 = f"{BGM_DIR}/_e5_end.wav"
    c5 = f"{BGM_DIR}/_c5_end.wav"

    generate_sine_wave(783.99, 0.7, g5)   # G5
    generate_sine_wave(659.25, 0.7, e5)   # E5
    generate_sine_wave(523.25, 1.3, c5)   # C5

    filter_expr = (
        f"[0:a]adelay=0:all=1,afade=t=in:d=0.05[a0];"
        f"[1:a]adelay=200:all=1,afade=t=in:d=0.05[a1];"
        f"[2:a]adelay=400:all=1,afade=t=in:d=0.05[a2];"
        f"[a0][a1][a2]amix=inputs=3:duration=longest:weights=1 1 1.2,"
        f"afade=t=out:st=1.5:d=0.5,volume=0.5[aout]"
    )

    run(f'ffmpeg -y -i {g5} -i {e5} -i {c5} '
        f'-filter_complex "{filter_expr}" -map "[aout]" -ar 48000 {ending_path}')

    print(f"  ✅ 结尾音合成完成")
    return ending_path


def offline_bgm(duration_sec):
    """Generate simple ambient background using ffmpeg (offline fallback)."""
    bgm_path = f"{BGM_DIR}/offline_bgm.wav"
    if os.path.exists(bgm_path) and os.path.getsize(bgm_path) > 1000:
        return bgm_path

    print("  🎹 离线合成背景音乐 (ambient pad)...")

    # Simple chord pad: C major chord with slow envelope
    filter_expr = (
        f"sine=f=261.63:d={duration_sec},volume=0.08[s1];"
        f"sine=f=329.63:d={duration_sec},volume=0.06[s2];"
        f"sine=f=392.00:d={duration_sec},volume=0.05[s3];"
        f"[s1][s2][s3]amix=inputs=3:duration=longest,"
        f"afade=t=in:d=2,afade=t=out:st={duration_sec-2}:d=2[aout]"
    )

    run(f'ffmpeg -y -f lavfi -i "{filter_expr}" '
        f'-map "[aout]" -ar 48000 -ac 1 {bgm_path}')
    return bgm_path


def build_bgm_track(intro_path, music_path, ending_path, video_dur, intro_dur=2.5, ending_dur=2.0):
    """Build complete BGM audio track with silence gaps for clean transitions.
    
    Timeline: [intro] [gap] [=== music loop ===] [gap] [ending]
    No overlap between chime and narration.
    """
    bgm_track = f"{BGM_DIR}/bgm_track.wav"
    INTRO_GAP = 0.7   # silence after intro chime
    ENDING_GAP = 0.5  # silence before ending chime
    
    intro_dur = min(intro_dur, video_dur * 0.1)
    ending_dur = min(ending_dur, video_dur * 0.08)

    # Get actual durations
    intro_info = run(f"ffprobe -v error -show_entries format=duration "
                     f"-of default=noprint_wrappers=1:nokey=1 {intro_path}")
    intro_actual = float(intro_info.stdout.strip() or intro_dur)

    ending_info = run(f"ffprobe -v error -show_entries format=duration "
                      f"-of default=noprint_wrappers=1:nokey=1 {ending_path}")
    ending_actual = float(ending_info.stdout.strip() or ending_dur)

    total_padding = intro_actual + INTRO_GAP + ENDING_GAP + ending_actual
    music_dur = video_dur  # music plays full video duration (narration also padded elsewhere)

    print(f"  📐 视频: {video_dur:.1f}s | 开场: {intro_actual:.1f}s+{INTRO_GAP}s间隙 | BGM: {music_dur:.1f}s | 结尾间隙: {ENDING_GAP}s+{ending_actual:.1f}s")
    print(f"  📐 总 padding: {total_padding:.1f}s → 新视频时长: {video_dur + total_padding:.1f}s")

    # Trim intro and ending
    intro_trimmed = f"{BGM_DIR}/intro_trimmed.wav"
    ending_trimmed = f"{BGM_DIR}/ending_trimmed.wav"
    run(f"ffmpeg -y -i {intro_path} -t {intro_actual} -ar 48000 -ac 1 {intro_trimmed}")
    run(f"ffmpeg -y -i {ending_path} -t {ending_actual} -ar 48000 -ac 1 {ending_trimmed}")

    # Generate silence segments
    silence_gap1 = f"{BGM_DIR}/silence_gap1.wav"
    silence_gap2 = f"{BGM_DIR}/silence_gap2.wav"
    run(f"ffmpeg -y -f lavfi -i anullsrc=r=48000:cl=mono -t {INTRO_GAP} -ar 48000 -ac 1 {silence_gap1}")
    run(f"ffmpeg -y -f lavfi -i anullsrc=r=48000:cl=mono -t {ENDING_GAP} -ar 48000 -ac 1 {silence_gap2}")

    # Prepare music portion
    music_info = run(f"ffprobe -v error -show_entries format=duration "
                     f"-of default=noprint_wrappers=1:nokey=1 {music_path}")
    music_len = float(music_info.stdout.strip() or 60)

    if music_len >= music_dur + 2:
        skip = min(music_len * 0.15, (music_len - music_dur) / 2)
        music_trimmed = f"{BGM_DIR}/music_trimmed.wav"
        run(f"ffmpeg -y -ss {skip:.1f} -i {music_path} -t {music_dur:.1f} "
            f"-ar 48000 -ac 1 {music_trimmed}")
    else:
        loops_needed = int(music_dur / music_len) + 2
        music_trimmed = f"{BGM_DIR}/music_trimmed.wav"
        run(f"ffmpeg -y -stream_loop {loops_needed} -i {music_path} "
            f"-t {music_dur:.1f} -ar 48000 -ac 1 {music_trimmed}")

    # Apply volume + fades to music
    music_vol = f"{BGM_DIR}/music_vol.wav"
    fade_out_start = max(0.5, music_dur - 0.5)
    run(f"ffmpeg -y -i {music_trimmed} "
        f'-af "volume=0.15,afade=t=in:d=0.8,afade=t=out:st={fade_out_start:.1f}:d=1.0" '
        f"-ar 48000 -ac 1 {music_vol}")

    # Concat: intro + gap + music + gap + ending
    concat_file = f"{BGM_DIR}/concat.txt"
    with open(concat_file, "w") as f:
        f.write(f"file '{intro_trimmed}'\n")
        f.write(f"file '{silence_gap1}'\n")
        f.write(f"file '{music_vol}'\n")
        f.write(f"file '{silence_gap2}'\n")
        f.write(f"file '{ending_trimmed}'\n")

    run(f"ffmpeg -y -f concat -safe 0 -i {concat_file} -c copy {bgm_track}")
    return bgm_track, total_padding


def mix_and_output(bgm_track, narration_wav, video_dur, total_padding):
    """Mix BGM track with narration and replace audio in video.
    
    Uses the original PCM narration.wav (from VoxCPM2) directly — skips AAC
    encode/decode cycle that previously introduced quantization noise amplified
    by the 3× volume boost.
    
    Adds silence padding to narration so intro/ending chimes don't overlap with speech.
    Extends video by freezing first/last frames during chime periods.
    """
    print("\n═══ 混合音频 ═══")

    # Calculate padding: intro(2.3s) + gap(0.7s) + ... + gap(0.5s) + ending(1.7s)
    # Use ffprobe to get actual bgm track positions
    INTRO_GAP = 0.7
    ENDING_GAP = 0.5
    intro_actual = 2.3
    ending_actual = 1.7

    pad_start = intro_actual + INTRO_GAP  # silence before narration starts
    pad_end = ENDING_GAP + ending_actual    # silence after narration ends

    # Use original PCM narration.wav directly — skip AAC decode cycle to avoid noise
    narration_raw = f"{BGM_DIR}/narration_raw.wav"
    if not os.path.exists(narration_raw):
        if os.path.exists(narration_wav):
            # Copy original PCM narration (clean, no AAC re-encode)
            run(f"cp {narration_wav} {narration_raw}")
            print(f"  ✅ 使用原始 PCM 口播音频（跳过 AAC 重编码）")
        else:
            # Fallback: extract from video
            run(f"ffmpeg -y -i {INPUT_VIDEO} -vn -acodec pcm_s16le -ar 48000 -ac 2 {narration_raw}")

    # Mix narration + BGM — 使用 adelay 替代 concat 静音垫片
    # 旧方案用 concat 拼 3s 静音 + 口播 + 2.2s 静音，在拼接处引入了噪音
    # 新方案: narration 原位后用 adelay 延后 3s，BGM 自带开场钟声不延迟
    mixed_audio = f"{BGM_DIR}/mixed_audio.wav"
    run(f'ffmpeg -y '
        f'-i {narration_raw} '
        f'-i {bgm_track} '
        f'-filter_complex '
        f'"[0:a]adelay={pad_start*1000:.0f}|{pad_start*1000:.0f}[nar_delay];'
        f'[nar_delay]volume=1.5[nar];'
        f'[1:a]aformat=channel_layouts=mono[bgm_mono];'
        f'[bgm_mono]asplit[bgmL][bgmR];'
        f'[bgmL][bgmR]amerge=inputs=2[bgm_stereo];'
        f'[nar][bgm_stereo]amix=inputs=2:duration=longest:normalize=0[aout]" '
        f'-map "[aout]" -ar 48000 -ac 2 {mixed_audio}')
    print(f"  🔊 VoxCPM2 原音直出 (adelay 替代 concat 垫片, 消除拼接噪音)")

    # ── Extend video: freeze first/last frames ──
    print("\n═══ 视频延展（冻结首尾帧） ═══")
    padded_video = f"{VIDEO_DIR}/padded_video.mp4"

    # Freeze first frame (extract from input video)
    first_frame = f"{BGM_DIR}/first_frame.png"
    run(f"ffmpeg -y -i {INPUT_VIDEO} -vframes 1 -q:v 2 {first_frame}")
    intro_video = f"{BGM_DIR}/intro_freeze.mp4"
    run(f'ffmpeg -y -loop 1 -t {pad_start:.3f} -i {first_frame} '
        f'-c:v libx264 -pix_fmt yuv420p -r 24 -an {intro_video}')

    # Freeze last frame (extract last frame from video)
    last_frame = f"{BGM_DIR}/last_frame.png"
    run(f"ffmpeg -y -sseof -1 -i {INPUT_VIDEO} -vframes 1 -q:v 2 {last_frame}")
    outro_video = f"{BGM_DIR}/outro_freeze.mp4"
    run(f'ffmpeg -y -loop 1 -t {pad_end:.3f} -i {last_frame} '
        f'-c:v libx264 -pix_fmt yuv420p -r 24 -an {outro_video}')

    # Concat video: intro_freeze + original + outro_freeze
    video_concat = f"{BGM_DIR}/video_concat.txt"
    with open(video_concat, "w") as f:
        f.write(f"file '{intro_video}'\n")
        f.write(f"file '{INPUT_VIDEO}'\n")
        f.write(f"file '{outro_video}'\n")
    run(f"ffmpeg -y -f concat -safe 0 -i {video_concat} -c copy {padded_video}")
    print(f"  ✅ 视频延展完成")

    # ── Mux extended video + mixed audio ──
    print(f"\n═══ 合成最终视频 ═══")
    run(f'ffmpeg -y '
        f'-i {padded_video} '
        f'-i {mixed_audio} '
        f'-c:v copy '
        f'-c:a aac -b:a 160k '
        f'-map 0:v:0 -map 1:a:0 '
        f'-shortest '
        f'{OUTPUT_VIDEO}')

    # Verify
    if os.path.exists(OUTPUT_VIDEO):
        info = run(f"ffprobe -v error -show_entries format=duration,size "
                   f"-of default=noprint_wrappers=1:nokey=0 {OUTPUT_VIDEO}")
        lines = info.stdout.strip().split('\n')
        dur = float([l for l in lines if 'duration' in l][0].split('=')[1])
        size = int([l for l in lines if 'size' in l][0].split('=')[1])
        print(f"\n{'='*60}")
        print(f"✅ BGM 混音完成!")
        print(f"   📁 {OUTPUT_VIDEO}")
        print(f"   ⏱  {dur:.1f}s ({dur/60:.1f}min)")
        print(f"   📦 {size/1024/1024:.1f} MB")
        print(f"   🎵 开场钟声 → 停顿 → 口播+BGM → 停顿 → 结尾'叮'")
        print(f"{'='*60}")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="BGM Video Mixer")
    parser.add_argument("--mood", default="auto",
                        choices=["auto", "upbeat", "calm", "professional", "motivating", "warm", "corporate", "driven"],
                        help="音乐情绪 (default: auto 自动检测)")
    parser.add_argument("--bgm", default=None,
                        help="手动指定背景音乐文件路径")
    parser.add_argument("--no-bgm", action="store_true",
                        help="仅添加开场/结尾音效，不加背景音乐")
    args = parser.parse_args()

    print("🎵 BGM Video Mixer")
    print("=" * 60)

    # Check input video
    if not os.path.exists(INPUT_VIDEO):
        print(f"❌ 找不到输入视频: {INPUT_VIDEO}")
        print(f"   请先运行 synthesize.py 生成 output_video.mp4")
        sys.exit(1)

    # Get video duration
    info = run(f"ffprobe -v error -show_entries format=duration "
               f"-of default=noprint_wrappers=1:nokey=1 {INPUT_VIDEO}")
    video_dur = float(info.stdout.strip())
    print(f"📹 输入视频: {video_dur:.1f}s")

    # Determine mood
    if args.mood == "auto":
        mood = detect_mood_from_script()
        entry = CATALOG.get(mood, CATALOG[DEFAULT_MOOD])
        print(f"🧠 自动检测情绪: {mood} → {entry['name']} ({entry['desc']})")
    else:
        mood = args.mood
        entry = CATALOG.get(mood, CATALOG[DEFAULT_MOOD])
        print(f"🎯 手动选择情绪: {mood} → {entry['name']} ({entry['desc']})")

    # Step 1: Generate intro sound
    print("\n═══ Step 1: 开场品牌音 ═══")
    intro_path = generate_intro()

    # Step 2: Get background music
    print("\n═══ Step 2: 背景音乐 ═══")
    if args.no_bgm:
        print("  ⏭️  跳过背景音乐 (--no-bgm)")
        music_path = offline_bgm(video_dur)
    elif args.bgm:
        music_path = args.bgm
        print(f"  📁 手动指定: {music_path}")
    else:
        music_path = download_music(mood)
        if music_path is None:
            # Fallback: use offline synthesis
            music_path = offline_bgm(video_dur)
            print(f"  🔄 离线合成: {music_path}")

    # Step 3: Generate ending sound
    print("\n═══ Step 3: 结尾标志音 ═══")
    ending_path = generate_ending()

    # Step 4: Build complete BGM track
    print("\n═══ Step 4: 构建 BGM 音轨 ═══")
    bgm_track, total_padding = build_bgm_track(intro_path, music_path, ending_path, video_dur)

    # Step 5: Mix and output
    # Use original PCM narration.wav (from VoxCPM2) — skip AAC encode/decode noise
    narration_wav = f"{VIDEO_DIR}/narration.wav"
    if not os.path.exists(narration_wav):
        narration_wav = f"{BGM_DIR}/narration_extracted.wav"  # fallback
    mix_and_output(bgm_track, narration_wav, video_dur, total_padding)


if __name__ == "__main__":
    main()
