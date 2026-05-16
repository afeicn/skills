import { execFileSync } from "child_process";
import { readFileSync, writeFileSync, existsSync, readdirSync, mkdirSync } from "fs";
import { join } from "path";

const root = process.cwd();
const outDir = join(root, "video_output");
if (!existsSync(outDir)) {
  mkdirSync(outDir);
}

const narrationWav = join(outDir, "narration.wav");
const narrationAiff = join(outDir, "narration.aiff");
const rawVideo = join(outDir, "slideshow_raw.mp4");
const concatPath = join(outDir, "concat.txt");
const subtitlesPath = join(outDir, "subtitles.ass");
const finalVideo = join(outDir, "output_video.mp4");

const scriptPath = join(root, "口播稿.md");
if (!existsSync(scriptPath)) {
  console.error("找不到口播稿.md");
  process.exit(1);
}
const text = readFileSync(scriptPath, "utf-8");

const imagesDir = join(root, "images");
if (!existsSync(imagesDir)) {
  console.error("找不到 images 目录，请在当前目录创建 images 文件夹并放入图片");
  process.exit(1);
}
const images = readdirSync(imagesDir)
  .filter((f) => f.match(/\.(jpg|jpeg|png)$/i))
  .sort()
  .map((f) => join(imagesDir, f));

if (images.length === 0) {
  console.error("images 目录下没有找到图片");
  process.exit(1);
}

function run(cmd, args) {
  execFileSync(cmd, args, { stdio: "inherit" });
}

function runQuiet(cmd, args) {
  return execFileSync(cmd, args, { encoding: "utf-8" }).trim();
}

function secondsToAss(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const cs = Math.floor((seconds % 1) * 100);
  return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}.${cs.toString().padStart(2, "0")}`;
}

function formatSubtitles(value, max = 14) {
  let escaped = value.replace(/{/g, "｛").replace(/}/g, "｝");
  
  let visibleCount = 0;
  let inHighlight = false;
  
  const highlightStart = "{\\c&H00D7FF&\\3c&H00D7FF&}"; 
  const highlightEnd = "{\\c&HFFFFFF&\\3c&HFFFFFF&}";
  
  for (let i = 0; i < escaped.length; i++) {
    if (escaped[i] === '*' && escaped[i+1] === '*') {
      const toggle = inHighlight ? highlightEnd : highlightStart;
      escaped = escaped.slice(0, i) + toggle + escaped.slice(i+2);
      inHighlight = !inHighlight;
      i += toggle.length - 1;
      continue;
    }
    
    if (escaped[i] !== '{' && escaped[i] !== '}') {
      visibleCount++;
      if (visibleCount === max && i < escaped.length - 1) {
        escaped = escaped.slice(0, i+1) + "\\N" + escaped.slice(i+1);
        visibleCount = 0;
        i += 2;
      }
    }
  }
  
  const lines = escaped.split("\\N");
  if (lines.length > 1 && lines[lines.length - 1].length <= 2) {
    const last = lines.pop();
    lines[lines.length - 1] += last;
  }
  
  return lines.join("\\N");
}

function getBackgroundShape(lineCount) {
  const H = 20 + lineCount * 52;
  const r = 20;
  const W = 660;
  const left = 30;
  const top = 1180 - H;
  
  const path = `m ${r} 0 l ${W-r} 0 b ${W} 0 ${W} 0 ${W} ${r} l ${W} ${H-r} b ${W} ${H} ${W} ${H} ${W-r} ${H} l ${r} ${H} b 0 ${H} 0 ${H} 0 ${H-r} l 0 ${r} b 0 0 0 0 ${r} 0`;
  
  return `{\\an7\\pos(${left},${top})\\p1}${path}{\\p0}`;
}

function sentenceChunks(value) {
  const pieces = value
    .split(/(?<=[。！？?])/)
    .map((part) => part.trim())
    .filter(Boolean);

  const chunks = [];
  let current = "";
  for (const piece of pieces) {
    if ((current + piece).length <= 42) {
      current += piece;
    } else {
      if (current) chunks.push(current);
      current = piece;
    }
  }
  if (current) chunks.push(current);
  return chunks;
}

function ffprobeDuration(file) {
  const output = runQuiet("ffprobe", [
    "-v",
    "error",
    "-show_entries",
    "format=duration",
    "-of",
    "default=noprint_wrappers=1:nokey=1",
    file,
  ]);
  return Number(output);
}

if (!existsSync(narrationWav)) {
  console.log("Generating narration with VoxCPM2...");
  const tempScriptPath = join(root, "temp_script.txt");
  writeFileSync(tempScriptPath, text.replace(/\*\*/g, ""));

  const venvPath = process.env.VOXCPM_VENV_PATH;
  const refAudio = process.env.VOXCPM_REF_AUDIO;
  
  if (!venvPath || !refAudio) {
    console.error("Please set VOXCPM_VENV_PATH and VOXCPM_REF_AUDIO environment variables.");
    process.exit(1);
  }

  const script = `
export HF_ENDPOINT=https://hf-mirror.com
source "${venvPath}"
export TEXT=$(<"${tempScriptPath}")
voxcpm clone --text "$TEXT" --reference-audio "${refAudio}" --output "${narrationAiff}"
`;
  run("bash", ["-c", script]);

  run("ffmpeg", ["-y", "-i", narrationAiff, "-ar", "48000", "-ac", "2", narrationWav]);
} else {
  console.log("Using cached narration audio...");
}

const audioDuration = ffprobeDuration(narrationWav);
const videoDuration = Math.max(audioDuration + 2.2, 20);

const numImages = images.length;
const sceneDurations = [];
if (numImages === 1) {
  sceneDurations.push(videoDuration);
} else {
  const firstLast = videoDuration * 0.16;
  const middle = (videoDuration - firstLast * 2) / Math.max(1, numImages - 2);
  sceneDurations.push(firstLast);
  for (let i = 0; i < numImages - 2; i++) {
    sceneDurations.push(middle);
  }
  sceneDurations.push(firstLast);
}

if (!existsSync(rawVideo)) {
  console.log("Building scene clips...");
  const sceneClips = images.map((image, index) => {
    const clipPath = join(outDir, "scene_" + (index + 1) + ".mp4");
    const duration = sceneDurations[index];
    const zoom =
      index % 2 === 0
        ? "zoompan=z='min(zoom+0.00025,1.03)':d=1:s=720x1280:fps=24"
        : "zoompan=z='1.03-(on*0.00025)':d=1:s=720x1280:fps=24";

    const filter = [
      "[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=22:3,setsar=1[bg]",
      "[0:v]scale=720:1280:force_original_aspect_ratio=decrease,setsar=1," + zoom + "[fg]",
      "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
    ].join(";");

    run("ffmpeg", [
      "-y",
      "-loop",
      "1",
      "-t",
      String(duration),
      "-i",
      image,
      "-filter_complex",
      filter,
      "-r",
      "24",
      "-an",
      "-c:v",
      "libx264",
      "-pix_fmt",
      "yuv420p",
      clipPath,
    ]);
    return clipPath;
  });

  writeFileSync(
    concatPath,
    sceneClips.map((clip) => "file '" + clip.replace(/'/g, "'\\''") + "'").join("\n") + "\n",
  );

  run("ffmpeg", ["-y", "-f", "concat", "-safe", "0", "-i", concatPath, "-c", "copy", rawVideo]);
} else {
  console.log("Using cached raw video scenes...");
}

console.log("Writing subtitles...");
const chunks = sentenceChunks(text);
const totalChars = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
let cursor = 0.45;
const events = [];
for (const chunk of chunks) {
  const duration = Math.max(2.2, (chunk.length / totalChars) * audioDuration);
  const start = cursor;
  const end = Math.min(start + duration, audioDuration + 0.6);
  const formattedText = formatSubtitles(chunk);
  const lineCount = formattedText.split("\\N").length;
  const shape = getBackgroundShape(lineCount);

  events.push(
    "Dialogue: 0," +
      secondsToAss(start) +
      "," +
      secondsToAss(end) +
      ",Panel,,0,0,0,," +
      shape
  );

  events.push(
    "Dialogue: 1," +
      secondsToAss(start) +
      "," +
      secondsToAss(end) +
      ",Caption,,0,0,0,," +
      formattedText
  );
  cursor = end;
}

writeFileSync(
  subtitlesPath,
  "[Script Info]\n" +
    "ScriptType: v4.00+\n" +
    "PlayResX: 720\n" +
    "PlayResY: 1280\n" +
    "ScaledBorderAndShadow: yes\n\n" +
    "[V4+ Styles]\n" +
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n" +
    "Style: Caption,LXGW WenKai,44,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0.7,0,2,50,50,115,1\n" +
    "Style: Panel,LXGW WenKai,44,&H44000000,&H44000000,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,2,50,50,115,1\n\n" +
    "[Events]\n" +
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" +
    events.join("\n") +
    "\n",
);

console.log("Muxing final video...");
run("ffmpeg", [
  "-y",
  "-i",
  rawVideo,
  "-i",
  narrationWav,
  "-vf",
  "ass=" + subtitlesPath,
  "-c:v",
  "libx264",
  "-c:a",
  "aac",
  "-b:a",
  "160k",
  "-shortest",
  finalVideo,
]);

console.log("Done! Video saved to " + finalVideo);
