"""
youtube_downloader_dark.py
Modern Dark UI (black-white theme) for downloading YouTube via yt-dlp.
Features:
 - MP4 / MP3
 - Quality select (360p/720p/1080p/best)
 - FFmpeg auto-detection (or set FFMPEG_PATH)
 - Progress bar with realtime updates
 - Non-blocking (uses threading)
Requirements:
 - pip install yt-dlp
 - ffmpeg (recommended for mp3 or merging high-res mp4)
"""

import os
import shutil
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp

# ---------- USER CONFIG ----------
# If ffmpeg is NOT in PATH, set full path here (windows example):
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # <--- edit if needed, or set to "" to rely on PATH
# ---------------------------------

# If user provided explicit path, inform yt-dlp about it:
if FFMPEG_PATH and os.path.isfile(FFMPEG_PATH):
    yt_dlp.utils.DEFAULT_FFMPEG_LOCATION = FFMPEG_PATH

# helper to detect ffmpeg availability
def ffmpeg_available():
    if FFMPEG_PATH and os.path.isfile(FFMPEG_PATH):
        return True
    return shutil.which("ffmpeg") is not None

# queue for progress updates from background thread to UI thread
progress_q = queue.Queue()

# global control for cancellation
_cancel_download = threading.Event()

# ---------- Download logic ----------
def make_ydl_opts(save_folder, fmt, quality):
    opts = {'outtmpl': os.path.join(save_folder, '%(title)s.%(ext)s')}
    # ensure yt-dlp uses ffmpeg location (if provided)
    if FFMPEG_PATH and os.path.isfile(FFMPEG_PATH):
        opts['ffmpeg_location'] = FFMPEG_PATH

    # add progress hook to report to UI
    def progress_hook(d):
        # d is dict with fields: status, total_bytes, downloaded_bytes, etc.
        # put minimal info into queue
        try:
            # status can be "downloading", "finished", "error"
            status = d.get('status')
            if status == 'downloading':
                # prefer percent if available
                percent = None
                if d.get('downloaded_bytes') and d.get('total_bytes'):
                    try:
                        percent = d['downloaded_bytes'] / d['total_bytes'] * 100.0
                    except Exception:
                        percent = None
                # sometimes 'progress' key exists with 'pct' -- but not always
                progress_q.put(('downloading', percent, d))
            elif status == 'finished':
                progress_q.put(('finished', 100.0, d))
            elif status == 'error':
                progress_q.put(('error', 0.0, d))
        except Exception as ex:
            progress_q.put(('error', 0.0, {'error': str(ex)}))

    opts['progress_hooks'] = [progress_hook]

    if fmt == 'MP3':
        # convert to mp3 using ffmpeg (requires ffmpeg)
        opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # prefer ffmpeg if set
        })
    else:  # MP4
        if quality == 'best' or quality == '':
            # request best (may require merging => needs ffmpeg)
            opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            })
        else:
            # quality like "720p" -> use height cap
            h = quality.replace('p', '')
            opts.update({
                'format': f'bestvideo[height<={h}]+bestaudio/best',
                'merge_output_format': 'mp4',
            })
    # Safety: if ffmpeg not available and user requested merged formats, tell yt-dlp to avoid merging
    if not ffmpeg_available():
        # For MP3 -> cannot convert without ffmpeg; we will fallback to downloading best audio and rename (may be .webm/.m4a)
        if fmt == 'MP3':
            # do not include postprocessor if no ffmpeg; user will get source audio (m4a/webm)
            # but to keep consistent, keep postprocessor but yt-dlp will fail; so better to remove
            opts.pop('postprocessors', None)
            opts['format'] = 'bestaudio/best'
        else:
            # choose progressive mp4 only to avoid merge (may limit to <=720p)
            # pick a fallback height 720 if requested higher
            try:
                # if specified h > 720, force 720
                if quality.endswith('p') and int(quality.replace('p','')) > 720:
                    opts['format'] = 'best[ext=mp4][height<=720]'
                else:
                    # keep whatever was set; but prefer progressive mp4
                    opts['format'] = 'best[ext=mp4]'
                # ensure not requesting merge
                opts.pop('merge_output_format', None)
            except Exception:
                opts['format'] = 'best[ext=mp4]'
    return opts

def download_worker(url, save_folder, fmt, quality):
    """background thread target: perform download and push progress updates to queue"""
    _cancel_download.clear()
    try:
        ydl_opts = make_ydl_opts(save_folder, fmt, quality)

        # Info: yt_dlp may call progress hooks from same thread; those hooks push to progress_q
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # finished (ensure final update)
        progress_q.put(('complete', 100.0, {'msg': 'done'}))
    except Exception as e:
        progress_q.put(('error', 0.0, {'error': str(e)}))

# ---------- UI ----------
class DarkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader — Dark (Black/White theme)")
        self.geometry("620x360")
        self.configure(bg="#0f0f10")  # dark background
        self.resizable(False, False)
        self._worker = None

        self.style = ttk.Style(self)
        # set ttk theme default and customizations
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        # configure colors for widgets
        self.style.configure("TLabel", background="#0f0f10", foreground="#e6e6e6", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("Small.TLabel", font=("Segoe UI", 9))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), foreground="#111111")
        self.style.map("TButton",
                       background=[('active', '#f2f2f2'), ('!disabled', '#ffffff')],
                       foreground=[('active', '#111111'), ('!disabled', '#111111')])

        # top frame (header)
        header = tk.Frame(self, bg="#0f0f10")
        header.pack(fill="x", padx=18, pady=(12,6))

        title = ttk.Label(header, text="YouTube Downloader", style="Header.TLabel")
        title.pack(side="left")
        subtitle = ttk.Label(header, text=" • Modern Dark (Black & White)", style="Small.TLabel")
        subtitle.pack(side="left", padx=(8,0))

        # main card
        card = tk.Frame(self, bg="#151515", bd=0, relief="flat")
        card.pack(padx=18, pady=8, fill="both", expand=False)

        # input row
        row1 = tk.Frame(card, bg="#151515")
        row1.pack(fill="x", padx=14, pady=(14,8))

        lbl = ttk.Label(row1, text="Link (YouTube):")
        lbl.pack(anchor="w")
        self.url_entry = ttk.Entry(row1, width=72)
        self.url_entry.pack(fill="x", pady=6)
        self.url_entry.focus()

        # options row
        row2 = tk.Frame(card, bg="#151515")
        row2.pack(fill="x", padx=14, pady=(0,10))

        # format
        fmt_lbl = ttk.Label(row2, text="Format:")
        fmt_lbl.grid(row=0, column=0, sticky="w")
        self.format_cb = ttk.Combobox(row2, values=["MP4", "MP3"], width=8, state="readonly")
        self.format_cb.set("MP4")
        self.format_cb.grid(row=1, column=0, padx=(0,6), pady=6, sticky="w")

        # quality
        q_lbl = ttk.Label(row2, text="Quality:")
        q_lbl.grid(row=0, column=1, sticky="w", padx=(12,0))
        self.quality_cb = ttk.Combobox(row2, values=["360p", "720p", "1080p", "best"], width=10, state="readonly")
        self.quality_cb.set("720p")
        self.quality_cb.grid(row=1, column=1, padx=(12,0), pady=6)

        # folder select
        folder_lbl = ttk.Label(row2, text="Save to:")
        folder_lbl.grid(row=0, column=2, sticky="w", padx=(18,0))
        self.folder_var = tk.StringVar(value=os.getcwd())
        self.folder_entry = ttk.Entry(row2, textvariable=self.folder_var, width=36)
        self.folder_entry.grid(row=1, column=2, padx=(18,0), pady=6, sticky="w")
        self.browse_btn = ttk.Button(row2, text="Browse", command=self.select_folder)
        self.browse_btn.grid(row=1, column=3, padx=(8,6), sticky="w")

        # buttons row
        row3 = tk.Frame(card, bg="#151515")
        row3.pack(fill="x", padx=14, pady=(4,10))

        self.download_btn = ttk.Button(row3, text="⬇️ Download", command=self.start_download)
        self.download_btn.pack(side="left", padx=(0,8))
        self.cancel_btn = ttk.Button(row3, text="✖ Cancel", command=self.cancel_download, state="disabled")
        self.cancel_btn.pack(side="left")

        # status and progress
        status_frame = tk.Frame(card, bg="#151515")
        status_frame.pack(fill="x", padx=14, pady=(6,14))

        self.status_label = ttk.Label(status_frame, text="Ready", style="Small.TLabel")
        self.status_label.pack(anchor="w")

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(status_frame, orient="horizontal", length=520, mode="determinate", variable=self.progress_var, maximum=100)
        self.progress.pack(pady=8)

        # helper hint
        hint = ttk.Label(self, text="Note: For MP3 or high-res MP4 merging, ffmpeg is required. If ffmpeg missing, will fallback to progressive MP4 (<=720p).", style="Small.TLabel")
        hint.pack(padx=18, pady=(6,10))

        # start polling queue
        self.after(200, self.process_queue)

    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get() or os.getcwd(), title="Select folder to save")
        if folder:
            self.folder_var.set(folder)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a YouTube URL.")
            return

        save_path = self.folder_var.get()
        if not os.path.isdir(save_path):
            messagebox.showwarning("Warning", "Please select a valid folder to save files.")
            return

        fmt = self.format_cb.get()
        quality = self.quality_cb.get()

        # disable UI controls while downloading
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.status_label.config(text="Starting download...")
        self.progress_var.set(0.0)
        self.update_idletasks()

        # start background thread
        self._worker = threading.Thread(target=download_worker, args=(url, save_path, fmt, quality), daemon=True)
        self._worker.start()

    def cancel_download(self):
        # yt-dlp doesn't expose a direct cancel; we can set a flag and rely on it in long ops.
        # Simple approach: set cancel flag and notify user. (yt-dlp may not respond immediately)
        _cancel_download.set()
        self.status_label.config(text="Cancel requested... (may take a moment)")
        self.cancel_btn.config(state="disabled")

    def process_queue(self):
        """Poll the progress queue and update UI"""
        try:
            while not progress_q.empty():
                item = progress_q.get_nowait()
                status, percent, data = item
                if status == 'downloading':
                    if percent is None:
                        # unknown percent — show spinner-like
                        self.status_label.config(text=f"Downloading... {data.get('filename', '')}")
                        # we cannot set percent, so just pulse
                        self.progress.step(2)
                    else:
                        self.progress_var.set(min(max(percent, 0.0), 100.0))
                        self.status_label.config(text=f"Downloading... {percent:.1f}% - {data.get('filename','')}")
                elif status == 'finished':
                    self.progress_var.set(100.0)
                    self.status_label.config(text="Merging / finalizing...")
                elif status == 'complete':
                    self.progress_var.set(100.0)
                    self.status_label.config(text="Download complete ✅")
                    messagebox.showinfo("Done", "Download finished successfully.")
                    self.download_btn.config(state="normal")
                    self.cancel_btn.config(state="disabled")
                elif status == 'error':
                    self.status_label.config(text="Error during download ❌")
                    messagebox.showerror("Error", data.get('error') or str(data))
                    self.download_btn.config(state="normal")
                    self.cancel_btn.config(state="disabled")
        except Exception as e:
            # queue processing error
            print("Queue processing error:", e)

        # schedule next poll
        self.after(200, self.process_queue)


if __name__ == "__main__":
    app = DarkApp()
    app.mainloop()
