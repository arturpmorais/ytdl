import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys
import subprocess

try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "imageio-ffmpeg"])
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

BG      = "#fdf6f0"  
SURFACE = "#f5ede4"  
CARD    = "#ffffff"  
BORDER  = "#e8c8cc"  
ACCENT  = "#d4687c"  
ACCENT2 = "#c45570"  
TEXT    = "#3d2020"  
SUBTEXT = "#a07878"  
SUCCESS = "#7cb97e"  
ERROR   = "#d46868"  

QUALITY_MP4 = {
    "Melhor disponível": "bestvideo+bestaudio/best",
    "1080p":             "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p":              "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p":              "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "360p":              "bestvideo[height<=360]+bestaudio/best[height<=360]",
}

QUALITY_MP3 = {
    "320 kbps": "320",
    "256 kbps": "256",
    "192 kbps": "192",
    "128 kbps": "128",
}

class YTDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("youtube downloader da janinhx <3")
        self.geometry("680x610")
        self.resizable(False, False)
        self.configure(bg=BG)

        icon_png = os.path.join(os.path.dirname(__file__), "assets", "janinhx.png")
        icon_ico = os.path.join(os.path.dirname(__file__), "assets", "janinhx.ico")
        self.logo_image = None

        if os.path.exists(icon_png):
            try:
                img = tk.PhotoImage(file=icon_png)
                max_dim = 28
                scale = max(1, img.height() // max_dim, img.width() // max_dim)
                if scale > 1:
                    img = img.subsample(scale, scale)
                self.logo_image = img
            except Exception:
                self.logo_image = None

        if sys.platform == "win32" and os.path.exists(icon_ico):
            try:
                self.iconbitmap(icon_ico)
            except Exception:
                pass
        elif self.logo_image:
            try:
                self.iconphoto(True, self.logo_image)
            except Exception:
                pass

        self.url_var      = tk.StringVar()
        self.format_var   = tk.StringVar(value="mp4")
        self.quality_var  = tk.StringVar(value="melhor disponível")
        self.folder_var   = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self._downloading = False

        self._build_ui()
        self._on_format_change()

    def _build_ui(self):
        pad = dict(padx=24)

        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(26, 18), **pad)

        if self.logo_image:
            tk.Label(header, image=self.logo_image, bg=BG).pack(side="left")
        else:
            tk.Label(header, text="♪", font=("Helvetica", 22),
                     fg=ACCENT, bg=BG).pack(side="left")

        tk.Label(header, text="  youtube downloader da janinhx <3", font=("Helvetica", 17, "bold"),
                 fg=TEXT, bg=BG).pack(side="left")
        # tk.Label(header, text="powered by yt-dlp", font=("Helvetica", 9),
        #          fg=SUBTEXT, bg=BG).pack(side="left", padx=(10, 0), pady=(6, 0))

        self._section_label("URL do vídeo ou playlist")
        url_frame = tk.Frame(self, bg=CARD, highlightbackground=BORDER,
                             highlightthickness=1)
        url_frame.pack(fill="x", **pad, pady=(4, 0))

        self._url_entry = tk.Entry(url_frame, textvariable=self.url_var,
                                   font=("Consolas", 11), bg=CARD, fg=TEXT,
                                   insertbackground=ACCENT, relief="flat", bd=0)
        self._url_entry.pack(side="left", fill="x", expand=True, padx=12, pady=10)

        tk.Button(url_frame, text="Colar", command=self._paste,
                  font=("Helvetica", 9), bg=SURFACE, fg=TEXT,
                  relief="flat", padx=10, cursor="hand2",
                  activebackground=BORDER, activeforeground=TEXT
                  ).pack(side="right", padx=6, pady=6)

        tk.Button(url_frame, text="✕", command=self._clear_url,
                  font=("Helvetica", 9), bg=SURFACE, fg=SUBTEXT,
                  relief="flat", padx=8, cursor="hand2",
                  activebackground=BORDER, activeforeground=TEXT
                  ).pack(side="right", pady=6)

        self._section_label("Formato", top=16)
        self._fmt_frame = tk.Frame(self, bg=BG)
        self._fmt_frame.pack(fill="x", **pad, pady=(4, 0))

        for fmt in ("mp4", "mp3"):
            rb = tk.Radiobutton(self._fmt_frame, text=fmt,
                                variable=self.format_var, value=fmt,
                                command=self._on_format_change,
                                font=("Helvetica", 11, "bold"),
                                bg=BG, fg=TEXT, selectcolor=BG,
                                activebackground=BG, activeforeground=ACCENT,
                                indicatoron=False, relief="flat",
                                padx=20, pady=8, cursor="hand2",
                                highlightthickness=1)
            rb.pack(side="left", padx=(0, 8))
            self.format_var.trace_add("write",
                lambda *a, b=rb, v=fmt: self._style_rb(b, v))

        self._style_all_rb(self._fmt_frame)

        self._section_label("Qualidade", top=16)
        self._quality_frame = tk.Frame(self, bg=BG)
        self._quality_frame.pack(fill="x", **pad, pady=(4, 0))

        self._section_label("Pasta de destino", top=16)
        folder_frame = tk.Frame(self, bg=CARD, highlightbackground=BORDER,
                                highlightthickness=1)
        folder_frame.pack(fill="x", **pad, pady=(4, 0))

        tk.Label(folder_frame, textvariable=self.folder_var,
                 font=("Consolas", 10), bg=CARD, fg=SUBTEXT,
                 anchor="w").pack(side="left", fill="x", expand=True, padx=12, pady=9)

        tk.Button(folder_frame, text="Escolher…", command=self._choose_folder,
                  font=("Helvetica", 9), bg=SURFACE, fg=TEXT,
                  relief="flat", padx=10, cursor="hand2",
                  activebackground=BORDER, activeforeground=TEXT
                  ).pack(side="right", padx=6, pady=6)

        prog_bg = tk.Frame(self, bg=BORDER, height=5)
        prog_bg.pack(fill="x", padx=24, pady=(20, 0))
        prog_bg.pack_propagate(False)

        self._prog_bar = tk.Frame(prog_bg, bg=ACCENT, height=5)
        self._prog_bar.place(x=0, y=0, relheight=1, relwidth=0)

        self._status_var = tk.StringVar(value="pronto para baixar")
        tk.Label(self, textvariable=self._status_var,
                 font=("Helvetica", 9), fg=SUBTEXT, bg=BG,
                 anchor="w").pack(fill="x", padx=24, pady=(5, 0))

        log_frame = tk.Frame(self, bg=SURFACE, highlightbackground=BORDER,
                             highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=24, pady=(8, 0))

        self._log = tk.Text(log_frame, height=6, bg=SURFACE, fg=SUBTEXT,
                            font=("Consolas", 9), relief="flat",
                            bd=0, state="disabled", wrap="word",
                            insertbackground=TEXT)
        scrollbar = tk.Scrollbar(log_frame, command=self._log.yview,
                                 bg=SURFACE, troughcolor=SURFACE, width=8)
        self._log.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._log.pack(fill="both", expand=True, padx=8, pady=6)

        self._btn_dl = tk.Button(self, text="⬇  baixar",
                                 command=self._start_download,
                                 font=("Helvetica", 12, "bold"),
                                 bg=ACCENT, fg="white", relief="flat",
                                 padx=0, pady=14, cursor="hand2",
                                 activebackground=ACCENT2, activeforeground="white")
        self._btn_dl.pack(fill="x", padx=24, pady=16)

    def _section_label(self, text, top=0):
        tk.Label(self, text=text.upper(),
                 font=("Helvetica", 8, "bold"), fg=SUBTEXT, bg=BG,
                 anchor="w").pack(fill="x", padx=24, pady=(top, 0))

    def _style_rb(self, btn, val):
        selected = self.format_var.get() == val
        btn.configure(
            bg=ACCENT if selected else CARD,
            fg=ACCENT2 if selected else TEXT,
            highlightbackground=ACCENT if selected else BORDER,
        )

    def _style_all_rb(self, frame):
        for w in frame.winfo_children():
            if isinstance(w, tk.Radiobutton):
                self._style_rb(w, w.cget("value"))

    def _on_format_change(self):
        for w in self._quality_frame.winfo_children():
            w.destroy()

        fmt = self.format_var.get()
        options = list(QUALITY_MP4 if fmt == "MP4" else QUALITY_MP3)
        self.quality_var.set(options[0])

        for opt in options:
            rb = tk.Radiobutton(self._quality_frame, text=opt,
                                variable=self.quality_var, value=opt,
                                font=("Helvetica", 10), bg=BG, fg=TEXT,
                                selectcolor=ACCENT, activebackground=BG,
                                activeforeground=ACCENT, cursor="hand2",
                                highlightthickness=0)
            rb.pack(side="left", padx=(0, 14))

    def _paste(self):
        try:
            self.url_var.set(self.clipboard_get())
        except Exception:
            pass

    def _clear_url(self):
        self.url_var.set("")

    def _choose_folder(self):
        path = filedialog.askdirectory(initialdir=self.folder_var.get())
        if path:
            self.folder_var.set(path)

    def _log_write(self, msg, color=None):
        self._log.configure(state="normal")
        tag = f"tag_{(color or SUBTEXT).replace('#', '')}"
        self._log.tag_configure(tag, foreground=color or SUBTEXT)
        self._log.insert("end", msg + "\n", tag)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _set_progress(self, pct):
        self._prog_bar.place(relwidth=pct / 100)

    def _set_status(self, msg):
        self._status_var.set(msg)

    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("URL vazia", "Cole a URL do vídeo antes de baixar.")
            return
        if self._downloading:
            return

        fmt  = self.format_var.get()
        qual = self.quality_var.get()

        self._downloading = True
        self._btn_dl.configure(state="disabled", text="Baixando…", bg=BORDER)
        self._set_progress(0)

        self._log_write(f"{'─' * 58}", BORDER)
        self._log_write(f"→ Formato:   {fmt} · {qual}", TEXT)
        self._log_write(f"→ URL:       {url}", TEXT)

        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        url    = self.url_var.get().strip()
        fmt    = self.format_var.get()
        qual   = self.quality_var.get()
        folder = self.folder_var.get()

        def progress_hook(d):
            if d["status"] == "downloading":
                pct_str = d.get("_percent_str", "0%").strip().replace("%", "")
                try:
                    pct = float(pct_str)
                except ValueError:
                    pct = 0
                speed = d.get("_speed_str", "").strip()
                eta   = d.get("_eta_str", "").strip()
                fname = os.path.basename(d.get("filename", ""))
                self.after(0, self._set_progress, pct)
                self.after(0, self._set_status,
                           f"{fname}  —  {pct:.0f}%  |  {speed}  |  ETA {eta}")
            elif d["status"] == "finished":
                self.after(0, self._set_progress, 100)
                self.after(0, self._log_write,
                           f"✔ Arquivo pronto: {os.path.basename(d.get('filename', ''))}",
                           SUCCESS)

        if fmt == "MP4":
            opts = {
                "format":              QUALITY_MP4[qual],
                "outtmpl":             os.path.join(folder, "%(title)s.%(ext)s"),
                "progress_hooks":      [progress_hook],
                "merge_output_format": "mp4",
                "ffmpeg_location":     FFMPEG_PATH,
                "quiet":               True,
                "no_warnings":         True,
            }
        else:
            opts = {
                "format":          "bestaudio/best",
                "outtmpl":         os.path.join(folder, "%(title)s.%(ext)s"),
                "progress_hooks":  [progress_hook],
                "ffmpeg_location": FFMPEG_PATH,
                "postprocessors":  [{
                    "key":              "FFmpegExtractAudio",
                    "preferredcodec":   "mp3",
                    "preferredquality": QUALITY_MP3[qual],
                }],
                "quiet":           True,
                "no_warnings":     True,
            }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info  = ydl.extract_info(url, download=False)
                title = info.get("title", url)
                self.after(0, self._log_write, f"📄 {title}", TEXT)
                ydl.download([url])
            self.after(0, self._set_status, "✿ Download finalizado com sucesso!")
            self.after(0, self._log_write, f"📁 Salvo em: {folder}", SUCCESS)
        except Exception as e:
            self.after(0, self._log_write, f"✖ Erro: {e}", ERROR)
            self.after(0, self._set_status, "Erro durante o download.")
        finally:
            self._downloading = False
            self.after(0, self._btn_dl.configure,
                       {"state": "normal", "text": "⬇  BAIXAR", "bg": ACCENT})

if __name__ == "__main__":
    app = YTDownloader()
    app.mainloop()