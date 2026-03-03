import sys
import os
import shutil
import yt_dlp
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QComboBox, QLabel,
                             QMessageBox, QProgressBar, QFileDialog, QGroupBox)
from PyQt6.QtCore import QThread, pyqtSignal


def get_common_opts():
    opts = {'nocheckcertificate': True}
    node_path = shutil.which('node')
    if node_path:
        opts['js_runtimes'] = {'node': {'path': node_path}}
        opts['remote_components'] = ['ejs:github']
    return opts


class DownloadThread(QThread):
    done = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, url, format_id, cookie_file):
        super().__init__()
        self.url = url
        self.format_id = format_id
        self.cookie_file = cookie_file

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                self.progress.emit(int(downloaded / total * 100))

    def run(self):
        try:
            ffmpeg_path = shutil.which('ffmpeg')

            ydl_opts = {
                **get_common_opts(),
                # ✅ 优先选 m4a（AAC）音频，Windows 媒体播放器原生支持
                'format': f'{self.format_id}+bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'merge_output_format': 'mp4',
                'ffmpeg_location': ffmpeg_path,
                'fragment_retries': 10,
                'retries': 10,
                'progress_hooks': [self.progress_hook],
            }
            if self.cookie_file:
                ydl_opts['cookiefile'] = self.cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.progress.emit(100)
            self.done.emit("下载成功！文件已保存在程序运行目录。")
        except Exception as e:
            self.error.emit(str(e))


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.cookie_file_path = ''
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Pro Downloader')
        self.setFixedWidth(560)
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Node.js 状态
        node_path = shutil.which('node')
        if node_path:
            node_label = QLabel(f"✅ Node.js 已就绪：{node_path}")
            node_label.setStyleSheet(
                "background:#d4edda;color:#155724;padding:6px;border-radius:4px;font-size:11px;")
        else:
            node_label = QLabel("⚠️ 未检测到 Node.js！请安装：https://nodejs.org 安装后重启程序")
            node_label.setStyleSheet(
                "background:#f8d7da;color:#721c24;padding:6px;border-radius:4px;font-size:11px;")
        node_label.setWordWrap(True)
        layout.addWidget(node_label)

        # ffmpeg 状态
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            ff_label = QLabel(f"✅ ffmpeg 已就绪：{ffmpeg_path}")
            ff_label.setStyleSheet(
                "background:#d4edda;color:#155724;padding:6px;border-radius:4px;font-size:11px;")
        else:
            ff_label = QLabel("⚠️ 未检测到 ffmpeg！音视频无法合并，请确认已加入 PATH 并重启")
            ff_label.setStyleSheet(
                "background:#f8d7da;color:#721c24;padding:6px;border-radius:4px;font-size:11px;")
        ff_label.setWordWrap(True)
        layout.addWidget(ff_label)

        # URL 输入
        layout.addWidget(QLabel("视频链接:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('粘贴 YouTube 链接...')
        layout.addWidget(self.url_input)

        self.btn_analyze = QPushButton('解析视频信息')
        self.btn_analyze.clicked.connect(self.analyze_video)
        layout.addWidget(self.btn_analyze)

        # 分辨率
        layout.addWidget(QLabel("选择分辨率/格式:"))
        self.res_combo = QComboBox()
        layout.addWidget(self.res_combo)

        # Cookie
        cookie_group = QGroupBox("Cookie 设置（下载需要，必须选择）")
        cookie_layout = QVBoxLayout()
        cookie_layout.setSpacing(6)

        file_row = QHBoxLayout()
        self.btn_pick_cookie = QPushButton("选择 Cookie 文件 (.txt)")
        self.btn_pick_cookie.clicked.connect(self.pick_cookie_file)
        file_row.addWidget(self.btn_pick_cookie)
        self.cookie_path_label = QLabel("未选择")
        self.cookie_path_label.setStyleSheet("color:gray;font-size:11px;")
        file_row.addWidget(self.cookie_path_label)
        self.btn_clear_cookie = QPushButton("清除")
        self.btn_clear_cookie.setFixedWidth(50)
        self.btn_clear_cookie.clicked.connect(self.clear_cookie)
        file_row.addWidget(self.btn_clear_cookie)
        cookie_layout.addLayout(file_row)

        hint = QLabel(
            "导出方法：Chrome/Edge 安装扩展 \"Get cookies.txt LOCALLY\"，\n"
            "打开 YouTube 后点击扩展图标 → 导出当前站点 → 保存 .txt，然后在此选择。"
        )
        hint.setStyleSheet("color:gray;font-size:10px;")
        hint.setWordWrap(True)
        cookie_layout.addWidget(hint)
        cookie_group.setLayout(cookie_layout)
        layout.addWidget(cookie_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 下载按钮
        self.btn_download = QPushButton('开始下载')
        self.btn_download.setEnabled(False)
        self.btn_download.clicked.connect(self.start_download)
        layout.addWidget(self.btn_download)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size:11px;color:#555;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def pick_cookie_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Cookie 文件", "", "Cookie Files (*.txt);;All Files (*)")
        if path:
            self.cookie_file_path = path
            self.cookie_path_label.setText(os.path.basename(path))
            self.cookie_path_label.setStyleSheet("color:green;font-size:11px;")

    def clear_cookie(self):
        self.cookie_file_path = ''
        self.cookie_path_label.setText("未选择")
        self.cookie_path_label.setStyleSheet("color:gray;font-size:11px;")

    def analyze_video(self):
        url = self.url_input.text().strip()
        if not url:
            return
        self.btn_analyze.setText("解析中...")
        self.btn_analyze.setEnabled(False)
        self.status_label.setText("正在获取视频信息...")
        try:
            ydl_opts = {**get_common_opts(), 'quiet': True, 'no_warnings': True}
            if self.cookie_file_path:
                ydl_opts['cookiefile'] = self.cookie_file_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            formats = info.get('formats', [])
            self.res_combo.clear()
            seen_res = set()
            video_formats = sorted(
                [f for f in formats
                 if f.get('height')
                 and f.get('vcodec') != 'none'
                 and f.get('protocol') not in ('m3u8', 'm3u8_native')],
                key=lambda x: (x.get('height', 0), x.get('fps') or 0),
                reverse=True
            )
            for f in video_formats:
                res = f.get('height')
                if res in seen_res:
                    continue
                seen_res.add(res)
                fps = f.get('fps', '')
                fps_str = f"@{int(fps)}fps" if fps else ""
                ext = f.get('ext', '')
                note = f.get('format_note') or f.get('quality_label') or 'N/A'
                vbr = f.get('vbr')
                vbr_str = f" ~{int(vbr)}kbps" if vbr else ""
                self.res_combo.addItem(
                    f"{res}p{fps_str} - {ext}{vbr_str} ({note})",
                    f.get('format_id')
                )

            if self.res_combo.count() > 0:
                self.btn_download.setEnabled(True)
                title = info.get('title', '')[:50]
                self.status_label.setText(
                    f"解析成功：{title}\n共 {self.res_combo.count()} 个分辨率可选")
            else:
                QMessageBox.warning(self, "警告", "未找到可用视频格式。")
        except Exception as e:
            QMessageBox.critical(self, "解析错误", str(e))
            self.status_label.setText("")
        finally:
            self.btn_analyze.setText("解析视频信息")
            self.btn_analyze.setEnabled(True)

    def start_download(self):
        if not self.cookie_file_path:
            ret = QMessageBox.question(
                self, "未选择 Cookie",
                "未选择 Cookie 文件，可能导致下载失败。\n是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if ret == QMessageBox.StandardButton.No:
                return

        url = self.url_input.text().strip()
        format_id = self.res_combo.currentData()
        self.btn_download.setEnabled(False)
        self.btn_download.setText("正在下载...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("下载中（会先下载视频和音频，最后自动合并为 mp4）…")

        self.thread = DownloadThread(url, format_id, self.cookie_file_path)
        self.thread.done.connect(self.on_success)
        self.thread.error.connect(self.on_error)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.start()

    def on_success(self, msg):
        QMessageBox.information(self, "完成", msg)
        self.status_label.setText("✅ " + msg)
        self.reset_ui()

    def on_error(self, msg):
        tips = "建议：\n"
        if 'ffmpeg' in msg.lower():
            tips += "• ffmpeg 未找到，请确认已安装并加入系统 PATH，然后重启程序\n"
        elif '403' in msg or 'forbidden' in msg.lower():
            tips += "• Cookie 已过期，请重新从浏览器导出后重试\n"
        elif 'format' in msg.lower():
            tips += "• 请重新点击「解析视频信息」后再下载\n"
        tips += "• 确认视频链接可以正常访问"
        QMessageBox.critical(self, "下载失败", msg + "\n\n" + tips)
        self.status_label.setText("❌ 下载失败")
        self.reset_ui()

    def reset_ui(self):
        self.btn_download.setEnabled(True)
        self.btn_download.setText("开始下载")
        self.progress_bar.setVisible(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())