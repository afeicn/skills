#!/usr/bin/env python3
"""
Complete video synthesis pipeline:
1. VoxCPM2 chunked audio generation
2. Slideshow from images (proper 9:16 fit)
3. Subtitle overlay via chroma-key (green screen)
4. Final mux
"""
import re, os, subprocess, json, sys

WORKDIR = os.getcwd()
OUTDIR = f"{WORKDIR}/video_output"
IMGDIR = f"{WORKDIR}/images"
os.makedirs(OUTDIR, exist_ok=True)

VOXCPM_BIN = "/Users/liuwei/.local/miniforge3/envs/voxcpm2/bin/voxcpm"
REF_AUDIO = f"{OUTDIR}/ref.wav"
NARRATION_WAV = f"{OUTDIR}/narration.wav"
SLIDESHOW_MP4 = f"{OUTDIR}/slideshow.mp4"
SUBTITLE_MP4 = f"{OUTDIR}/subtitles_chromakey.mp4"
FINAL_MP4 = f"{OUTDIR}/output_video.mp4"

W, H = 720, 1280  # 9:16 vertical

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"FAILED: {cmd[:100]}")
        print(result.stderr[-500:])
        sys.exit(1)
    return result

# ═══════════════════════════════════════════════════
# STEP 1: VoxCPM2 Audio (chunked)
# ═══════════════════════════════════════════════════
print("═══ STEP 1: VoxCPM2 Audio Generation ═══")

with open(f"{WORKDIR}/口播稿.md", "r") as f:
    narration_text = f.read().strip()

# Split into ~120 char chunks for ~30s each
MAX_CHARS = 120
sentences = re.split(r'(?<=[。！？?])\s*', narration_text)
sentences = [s.strip() for s in sentences if s.strip()]

chunks = []
current = ""
for s in sentences:
    if len(s) > MAX_CHARS:
        if current:
            chunks.append(current)
            current = ""
        # Hard split long sentence
        remaining = s
        while len(remaining) > 0:
            cut = min(MAX_CHARS, len(remaining))
            chunks.append(remaining[:cut])
            remaining = remaining[cut:]
        continue
    if len(current + s) <= MAX_CHARS:
        current += s
    else:
        if current:
            chunks.append(current)
        current = s
if current:
    chunks.append(current)

print(f"Split into {len(chunks)} audio chunks")

if not os.path.exists(NARRATION_WAV):
    chunk_wavs = []
    for i, text in enumerate(chunks):
        chunk_aiff = f"{OUTDIR}/narration_chunk_{i+1}.aiff"
        chunk_wav = f"{OUTDIR}/narration_chunk_{i+1}.wav"
        chunk_wavs.append(chunk_wav)
        
        if os.path.exists(chunk_wav):
            print(f"  Chunk {i+1}/{len(chunks)} (cached)")
            continue
        
        print(f"  Generating chunk {i+1}/{len(chunks)} ({len(text)} chars)...")
        
        # Write temp text file (escaping for shell)
        tmp_txt = f"{OUTDIR}/chunk_{i+1}.txt"
        with open(tmp_txt, "w") as f:
            f.write(text)
        
        run(f'export HF_ENDPOINT=https://hf-mirror.com && '
            f'TEXT=$(<"{tmp_txt}") && '
            f'{VOXCPM_BIN} clone --text "$TEXT" --reference-audio "{REF_AUDIO}" --output "{chunk_aiff}"')
        
        run(f'ffmpeg -y -i {chunk_aiff} -ar 48000 -ac 2 {chunk_wav}')
        os.remove(tmp_txt)
    
    # Concat all chunks
    print("Concatenating audio chunks...")
    concat_list = f"{OUTDIR}/concat_audio.txt"
    with open(concat_list, "w") as f:
        for w in chunk_wavs:
            f.write(f"file '{w}'\n")
    run(f"ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {NARRATION_WAV}")
    print("Audio done!")
    
    # ⭐ 口播 1.2 倍速（用户要求）
    NARRATION_ORIG = f"{OUTDIR}/narration_orig.wav"
    run(f"mv {NARRATION_WAV} {NARRATION_ORIG}")
    run(f"ffmpeg -y -i {NARRATION_ORIG} -af 'atempo=1.2' -ar 48000 -ac 2 {NARRATION_WAV}")
    os.remove(NARRATION_ORIG)
    print("🎵 口播 1.2 倍速处理完成")
else:
    print("Using cached narration.wav")

# Get audio duration
result = run(f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {NARRATION_WAV}")
audio_dur = float(result.stdout.strip())
total_dur = audio_dur + 2.2
print(f"Audio: {audio_dur:.1f}s, Total: {total_dur:.1f}s")

# ═══════════════════════════════════════════════════
# STEP 2: Slideshow
# ═══════════════════════════════════════════════════
print("\n═══ STEP 2: Slideshow ═══")

images = sorted([f for f in os.listdir(IMGDIR) if f.endswith(('.png', '.jpg', '.jpeg'))])
print(f"Images: {images}")

n = len(images)
if n == 1:
    scene_durs = [total_dur]
else:
    first_last = total_dur * 0.16
    middle = (total_dur - first_last * 2) / max(1, n - 2)
    scene_durs = [first_last] + [middle] * (n - 2) + [first_last]

scenes = []
for i, (img, dur) in enumerate(zip(images, scene_durs)):
    img_path = f"{IMGDIR}/{img}"
    scene_path = f"{OUTDIR}/scene_{i+1}.mp4"
    
    if os.path.exists(scene_path):
        scenes.append(scene_path)
        continue
    
    print(f"  Scene {i+1}: {img} ({dur:.1f}s)")
    
    # Scale image to fit 720x1280, add blurred background
    # Use filter_complex to create pillarbox with blurred background
    zoom = "zoompan=z='min(zoom+0.0003,1.02)':d=1:s=720x1280:fps=24" if i%2==0 else \
           "zoompan=z='1.02-(on*0.0003)':d=1:s=720x1280:fps=24"
    
    filt = (
        f"[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=22:3,setsar=1[bg];"
        f"[0:v]scale=720:1280:force_original_aspect_ratio=decrease,setsar=1,{zoom}[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p"
    )
    
    run(f'ffmpeg -y -loop 1 -t {dur} -i "{img_path}" '
        f'-filter_complex "{filt}" -r 24 -an '
        f'-c:v libx264 -pix_fmt yuv420p {scene_path}')
    
    scenes.append(scene_path)

# Concat scenes
concat_txt = f"{OUTDIR}/scenes_concat.txt"
with open(concat_txt, "w") as f:
    for s in scenes:
        f.write(f"file '{s}'\n")

if not os.path.exists(SLIDESHOW_MP4):
    run(f"ffmpeg -y -f concat -safe 0 -i {concat_txt} -c copy {SLIDESHOW_MP4}")
    print("Slideshow done!")

# ═══════════════════════════════════════════════════
# STEP 3: Subtitle Overlay (chroma-key green screen)
# ═══════════════════════════════════════════════════
print("\n═══ STEP 3: Subtitle Overlay ═══")

from PIL import Image, ImageDraw, ImageFont

SUBDIR = f"{OUTDIR}/subs2"
os.makedirs(SUBDIR, exist_ok=True)

# Parse narration into subtitle segments (fix: replace \n with space to avoid layout bugs)
narration_clean = narration_text.replace('\n', ' ')
raw_sentences = re.split(r'(?<=[。，！？?：])\s*', narration_clean)
raw_sentences = [s.strip() for s in raw_sentences if s.strip()]

# Merge short sentences
sub_segments = []
current = ""
for s in raw_sentences:
    combined = (current + " " + s).strip() if current else s
    if len(combined) <= 28:
        current = combined
    else:
        if current:
            sub_segments.append(current)
        current = s
if current:
    sub_segments.append(current)

def word_wrap(text, max_chars=14):
    """Wrap Chinese text with proper line-breaking rules.
    禁则处理：标点符号不出现在行首。
    """
    if len(text) <= max_chars:
        return [text]
    
    # 不允许出现在行首的字符（中文禁则）
    LINE_START_BAD = set('。，！？、；：)」』】》）])}）》》')
    
    lines = []
    remaining = text
    while remaining:
        if len(remaining) <= max_chars:
            lines.append(remaining)
            break
        
        # 在 max_chars 范围内找最佳断点
        chunk = remaining[:max_chars]
        best_break = max_chars
        
        for sep in [' ', '，', '、', '；', '。', '！', '？', '：']:
            pos = chunk.rfind(sep)
            if pos > max_chars * 0.35 and pos < best_break:
                best_break = pos + 1  # 断在分隔符之后
        
        # ⭐ 禁则检查：如果断点后的首个字符是标点，往前调整
        if best_break < len(remaining):
            next_char = remaining[best_break]
            if next_char in LINE_START_BAD:
                # 把标点字符合并到当前行
                best_break = best_break + 1
                # 但如果这样导致当前行超长，继续往后找更合适的断点
                if best_break > max_chars + 2:
                    for i in range(best_break - 2, int(max_chars * 0.35) - 1, -1):
                        if remaining[i] in set(' ，、；。！？：'):
                            best_break = i + 1
                            break
        
        lines.append(remaining[:best_break].strip())
        remaining = remaining[best_break:].strip()
    
    return lines[:2]  # Max 2 lines

# ── Keyword Highlights (edit per video) ──
HIGHLIGHTS = sorted([
    "评测集",
    "智能问答",
    "自动评测",
    "人工评测",
    "知识库",
    "标准答案",
    "提示词",
], key=len, reverse=True)

WHITE = (255, 255, 255)
CYAN = (0, 215, 255)
OUTLINE_COLOR = (180, 180, 180)

def tokenize_with_highlights(text):
    """Split text into (text, is_highlight) spans"""
    spans = []
    remaining = text
    while remaining:
        found = False
        for kw in HIGHLIGHTS:
            idx = remaining.find(kw)
            if idx >= 0:
                if idx > 0:
                    spans.append((remaining[:idx], False))
                spans.append((kw, True))
                remaining = remaining[idx + len(kw):]
                found = True
                break
        if not found:
            spans.append((remaining, False))
            break
    return [(t, h) for t, h in spans if t]

# Calculate timing: evenly distribute across audio duration
chars_total = sum(len(s.replace(' ', '')) for s in sub_segments)
subs = []
cursor = 0.3
for seg in sub_segments:
    seg_clean = seg.replace(' ', '')
    dur = max(1.5, (len(seg_clean) / chars_total) * audio_dur)
    end = min(cursor + dur, audio_dur)
    lines = word_wrap(seg)
    subs.append({
        "start": cursor,
        "end": end,
        "lines": lines
    })
    cursor = end

print(f"Subtitle segments: {len(subs)}")

# Render subtitles with LXGW WenKai + keyword highlights + white outline
try:
    font = ImageFont.truetype(os.path.expanduser("~/Library/Fonts/LXGWWenKai-Regular.ttf"), 46)
    print(f"Font: LXGW WenKai 46px")
except:
    try:
        font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 46)
        print(f"Font: STHeiti Medium 46px (fallback)")
    except:
        font = ImageFont.load_default()

GREEN = (0, 255, 0)
DARK_GREEN = (0, 45, 0)
LINE_SPACING = 56
BOTTOM_MARGIN = 300
png_files = []

for i, sub in enumerate(subs):
    img = Image.new("RGB", (W, H), GREEN)
    draw = ImageDraw.Draw(img)
    
    lines = sub["lines"]
    total_h = len(lines) * LINE_SPACING
    y_start = H - BOTTOM_MARGIN - total_h
    
    padding = 20
    draw.rounded_rectangle(
        [30, y_start - padding, W - 30, y_start + total_h + padding],
        radius=14,
        fill=DARK_GREEN
    )
    
    for j, line in enumerate(lines):
        spans = tokenize_with_highlights(line)
        total_w = sum(draw.textbbox((0, 0), t, font=font)[2] - draw.textbbox((0, 0), t, font=font)[0] for t, _ in spans)
        x_start = (W - total_w) // 2
        y = y_start + j * LINE_SPACING
        
        x = x_start
        for text, is_hl in spans:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            text_color = CYAN if is_hl else WHITE
            
            # Outline (4-direction)
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                draw.text((x+dx, y+dy), text, font=font, fill=OUTLINE_COLOR)
            draw.text((x, y), text, font=font, fill=text_color)
            
            x += tw
    
    png_path = f"{SUBDIR}/sub_{i:03d}.png"
    img.save(png_path)
    png_files.append((png_path, sub["start"], sub["end"]))

print(f"Rendered {len(png_files)} subtitle PNGs")

# Create transparent gap filler
gap_img = Image.new("RGB", (W, H), GREEN)
gap_png = f"{SUBDIR}/gap.png"
gap_img.save(gap_png)

# Build subtitle video: concat gaps + subtitle clips at proper timestamps
segments = []
last_end = 0.0
for png, start, end in png_files:
    if start > last_end + 0.05:
        gap_dur = start - last_end
        gap_clip = f"{SUBDIR}/gap_{len(segments):03d}.mp4"
        run(f'ffmpeg -y -loop 1 -t {gap_dur:.3f} -i {gap_png} '
            f'-c:v libx264 -pix_fmt yuv420p -r 24 -an {gap_clip}')
        segments.append(gap_clip)
    
    dur = end - start
    clip = f"{SUBDIR}/clip_{len(segments):03d}.mp4"
    run(f'ffmpeg -y -loop 1 -t {dur:.3f} -i {png} '
        f'-c:v libx264 -pix_fmt yuv420p -r 24 -an {clip}')
    segments.append(clip)
    last_end = end

# Add final gap to match total duration
if total_dur > last_end + 0.05:
    gap_clip = f"{SUBDIR}/gap_final.mp4"
    run(f'ffmpeg -y -loop 1 -t {total_dur - last_end:.3f} -i {gap_png} '
        f'-c:v libx264 -pix_fmt yuv420p -r 24 -an {gap_clip}')
    segments.append(gap_clip)

# Concat all segments
seg_concat = f"{SUBDIR}/seg_concat.txt"
with open(seg_concat, "w") as f:
    for s in segments:
        f.write(f"file '{s}'\n")

run(f"ffmpeg -y -f concat -safe 0 -i {seg_concat} -c copy {SUBTITLE_MP4}")
print("Subtitle video done!")

# ═══════════════════════════════════════════════════
# STEP 4: Final Mux (slideshow + subtitle chroma-key + audio)
# ═══════════════════════════════════════════════════
print("\n═══ STEP 4: Final Mux ═══")

# Chroma key: remove green (#00FF00) from subtitle overlay and place on top of slideshow
# colorkey=0x00FF00:0.1:0.1 means: key out pure green with 10% similarity tolerance
run(f'ffmpeg -y '
    f'-i {SLIDESHOW_MP4} '
    f'-i {SUBTITLE_MP4} '
    f'-i {NARRATION_WAV} '
    f'-filter_complex "[1:v]colorkey=0x00FF00:0.2:0.1[sub];[0:v][sub]overlay=format=auto[outv]" '
    f'-map "[outv]" -map "2:a" '
    f'-c:v libx264 -c:a aac -b:a 160k '
    f'-shortest -pix_fmt yuv420p '
    f'{FINAL_MP4}')

# Verify
result = run(f"ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1:nokey=0 {FINAL_MP4}")
dur = float([l for l in result.stdout.strip().split('\n') if 'duration' in l][0].split('=')[1])
size = int([l for l in result.stdout.strip().split('\n') if 'size' in l][0].split('=')[1])

print(f"\n{'='*50}")
print(f"✅ DONE! Final video: {FINAL_MP4}")
print(f"   Duration: {dur:.1f}s ({dur/60:.1f}min)")
print(f"   Size: {size/1024/1024:.1f} MB")
print(f"   Resolution: {W}x{H} (9:16 vertical)")
print(f"{'='*50}")
