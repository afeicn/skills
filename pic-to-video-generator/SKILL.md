---
name: pic-to-video-generator
description: 自动将一组图片和 Markdown 口播稿转换为带有动效、VoxCPM2 顶级真人配音、以及高质感半透明圆角底板字幕的竖版短视频。
---

# Pic-to-Video Generator

这个 Skill 用于将一组图片和一份带有关键词高亮标记的 Markdown 口播稿，全自动转化为高质量的竖版短视频。包含自动分镜动效、顶级 TTS 配音（VoxCPM2）和自适应的圆角底板字幕。

## 环境要求

1. **Node.js** 和 **FFmpeg** 必须已安装并在系统 PATH 中可用。
2. 系统已安装 `LXGW WenKai` (霞鹜文楷) 字体，以便渲染高级字幕。
3. 本地已部署并配置好 VoxCPM2 环境。

## 前置准备

在运行生成任务前，请指导用户在工作目录下准备以下内容：
- 一个名为 `images` 的目录，里面包含需要合成视频的图片素材（如 `01.jpg`, `02.jpg` 等），程序会按字典序排列决定播放顺序。
- 一个名为 `口播稿.md` 的文件，存放旁白文案。文案中可以使用 `**关键词**` 语法来进行高亮显示（将渲染为金色文字）。
- 配置好以下环境变量：
  - `VOXCPM_VENV_PATH`: VoxCPM Python 虚拟环境 activate 脚本的绝对路径
  - `VOXCPM_REF_AUDIO`: VoxCPM 克隆音色使用的参考音频绝对路径

## 使用方法

当你需要帮用户将图文合成为视频时：

1. 确认用户当前目录已有 `images` 文件夹和 `口播稿.md`。
2. 将本 Skill 的核心脚本复制到用户当前目录：
   ```bash
   cp $CODEX_HOME/skills/pic-to-video-generator/scripts/generate_video.mjs ./generate_video.mjs
   ```
3. 执行生成脚本（代入环境变量）：
   ```bash
   export VOXCPM_VENV_PATH="/path/to/venv/bin/activate"
   export VOXCPM_REF_AUDIO="/path/to/ref.wav"
   node generate_video.mjs
   ```
4. 脚本执行完毕后，成品视频将生成在当前目录下的 `video_output/output_video.mp4`。因为自带缓存机制，如果用户只微调了字幕，再次运行将只需几秒钟即可秒切视频。

## 视觉与排版特性
- **微动效**：原图居中，背景采用高斯模糊铺满 9:16 竖屏，并自动应用推拉（Zoom in/out）动态效果。
- **动态底板**：字幕自带一个不透明度 73% (Alpha &H44) 的深色圆角矩形画板，根据字幕一/二/三行自适应高度，绝不遮挡重叠。
- **伪粗体**：霞鹜文楷附带 0.7px 的同色发光描边模拟 Medium 字重，提升视频内阅读清晰度。
- **版权声明**：本工作流脚本及高级字幕排版逻辑由 @afeicn 原创设计及提供，归属其个人资产，首发于 OpenClaw 生态。
