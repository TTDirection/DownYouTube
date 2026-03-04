# YouTube Pro Downloader

一个基于 Python + PyQt6 的 YouTube 视频下载工具，支持选择分辨率、自动合并音视频、兼容 Windows 媒体播放器。

---

## 功能特性

- 解析视频可用分辨率，自由选择画质
- 自动下载视频流 + 音频流，由 ffmpeg 合并为 mp4
- 音频优先使用 m4a（AAC）格式，Windows 媒体播放器原生支持
- 支持 Cookie 文件，可下载需要登录的视频
- 实时显示下载进度
- 异步下载，界面不卡顿

---

## 环境要求

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 任意 LTS 版本 | [nodejs.org](https://nodejs.org)，yt-dlp 解析 YouTube 需要 |
| ffmpeg | 任意版本 | [ffmpeg.org](https://ffmpeg.org/download.html)，合并音视频需要 |

---

## 安装步骤

### 1. 安装 Python

从 [python.org](https://www.python.org/downloads/) 下载并安装 Python 3.10+。

> ⚠️ 安装时勾选 **"Add Python to PATH"**

### 2. 安装 Node.js

从 [nodejs.org](https://nodejs.org) 下载 LTS 版本安装。

安装完成后验证：
```bash
node -v
```

### 3. 安装 ffmpeg

1. 从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载 Windows 版本（推荐 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 的 `ffmpeg-release-essentials.zip`）
2. 解压到任意目录，例如 `C:\ffmpeg`
3. 将 `C:\ffmpeg\bin` 添加到系统环境变量 `PATH`

添加完成后验证：
```bash
ffmpeg -version
```

### 4. 克隆项目

```bash
git clone https://github.com/your-username/yt-downloader.git
cd yt-downloader
```

### 5. 安装 Python 依赖

推荐使用 [uv](https://github.com/astral-sh/uv) 管理依赖（更快）：

```bash
# 安装 uv（如果还没装）
pip install uv

# 创建虚拟环境并安装依赖
uv venv
uv add yt-dlp PyQt6
```

或使用 pip：

```bash
pip install yt-dlp PyQt6
```

---

## 运行

```bash
# 使用 uv
uv run python yt_downloader.py

# 或直接使用 python
python yt_downloader.py
```

---

## 使用方法

### 基本下载

1. 粘贴 YouTube 视频链接
2. 点击「解析视频信息」
3. 从下拉菜单选择分辨率
4. 点击「开始下载」

文件默认保存在**程序运行目录**。

### Cookie 设置（解决 403 / 下载失败）

YouTube 目前对下载工具有限制，需要提供浏览器 Cookie 才能正常下载。

**导出步骤：**

1. 在 Chrome 或 Edge 安装扩展：[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. 打开 [youtube.com](https://youtube.com) 并登录账号
3. 点击扩展图标 → 选择「导出当前站点」→ 保存为 `.txt` 文件
4. 在程序中点击「选择 Cookie 文件」，选择刚才保存的文件

> ⚠️ Cookie 有有效期，若下载再次出现 403 错误，请重新导出。

---

## 常见问题

**Q：提示 `Node.js 未检测到`**  
A：安装 Node.js 后重启终端和程序，确保 `node` 命令在 PATH 中。

**Q：提示 `ffmpeg 未检测到`**  
A：确认已将 ffmpeg 的 `bin` 目录加入系统 PATH，重启终端后再试。

**Q：下载失败，提示 HTTP 403**  
A：需要 Cookie 文件。按上方「Cookie 设置」步骤导出后重试。

**Q：视频有画面但没有声音**  
A：确认 ffmpeg 已正确安装，程序依赖 ffmpeg 合并音视频流。

**Q：首次下载很慢**  
A：首次运行时程序会从 GitHub 下载 EJS 挑战解析脚本（约几百 KB），下载后会缓存到本地，后续不再重复下载。

---

## 技术栈

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — 视频下载核心
- [PyQt6](https://pypi.org/project/PyQt6/) — GUI 界面
- [ffmpeg](https://ffmpeg.org/) — 音视频合并
- [Node.js](https://nodejs.org) — yt-dlp JS 挑战解析运行时

---

## License

MIT