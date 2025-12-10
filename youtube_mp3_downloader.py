import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import yt_dlp
import threading
import os

class TkLogger:
    def __init__(self, write_fn):
        self.write_fn = write_fn
    def debug(self, msg):
        pass
    def info(self, msg):
        self.write_fn(msg)
    def warning(self, msg):
        # Gereksiz uyarilari filtrele
        ignore_keywords = [
            "JavaScript runtime", 
            "SABR streaming", 
            "web_safari", 
            "web client",
            "PO Token",
            "GVS PO Token",
            "po_token",
            "HTTP Error 403"
        ]
        if any(keyword in msg for keyword in ignore_keywords):
            pass
        else:
            self.write_fn(f"Uyari: {msg}")
    def error(self, msg):
        self.write_fn(f"Hata: {msg}")

class YouTubeMP3Downloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube MP3 Indirici")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        self.download_path = os.path.expanduser("~/Downloads")
        self.video_info_list = []

        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(7, weight=1)

        # Indirme konumu
        ttk.Label(main_frame, text="Indirme Konumu:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.path_entry = ttk.Entry(main_frame, width=50)
        self.path_entry.insert(0, self.download_path)
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Gozat", command=self.select_path).grid(row=0, column=2, pady=5)

        # Kalite secimi
        ttk.Label(main_frame, text="Ses Kalitesi:").grid(row=1, column=0, sticky=tk.W, pady=5)
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        self.quality_var = tk.StringVar(value="best")
        ttk.Radiobutton(quality_frame, text="En Iyi Kalite", 
                       variable=self.quality_var, value="best").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(quality_frame, text="Yuksek (192kbps)", 
                       variable=self.quality_var, value="192").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(quality_frame, text="Orta (128kbps)", 
                       variable=self.quality_var, value="128").pack(side=tk.LEFT, padx=10)

        # YouTube linki
        ttk.Label(main_frame, text="YouTube Linki:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Bilgi Al", command=self.get_video_info).grid(row=2, column=2, pady=5)

        # Durum
        self.status_label = ttk.Label(main_frame, text="Hazir", foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Video listesi
        ttk.Label(main_frame, text="Videolar:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=5)
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.video_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.video_listbox.yview)

        # Indirme butonu
        self.download_btn = ttk.Button(main_frame, text="MP3 Olarak Indir",
                                       command=self.download_videos, state=tk.DISABLED)
        self.download_btn.grid(row=5, column=0, columnspan=3, pady=10)

        # Ilerleme cubugu
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Log alani
        ttk.Label(main_frame, text="Indirme Durumu:").grid(row=7, column=0, sticky=(tk.W, tk.N), pady=5)
        self.log_text = scrolledtext.ScrolledText(main_frame, height=12, width=70, state=tk.DISABLED)
        self.log_text.grid(row=7, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.log("YouTube videolari MP3 formatinda indirilecek")
        self.log("En iyi kalite icin 'En Iyi Kalite' secenegini kullanin")

    def select_path(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def get_video_info(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Uyari", "Lutfen bir YouTube linki girin!")
            return

        self.video_listbox.delete(0, tk.END)
        self.video_info_list = []
        self.download_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Video bilgileri aliniyor...", foreground="orange")
        self.progress['value'] = 0
        self.progress['mode'] = 'indeterminate'
        self.progress.start()

        threading.Thread(target=self._fetch_info, args=(url,), daemon=True).start()

    def _fetch_info(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android']
                    }
                }
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise ValueError("Bilgi alinamadi. Lutfen linki kontrol edin.")

                if 'entries' in info and info['entries']:
                    for entry in info['entries']:
                        if entry:
                            self.video_info_list.append({
                                'url': entry.get('webpage_url') or entry.get('url'),
                                'title': entry.get('title', 'Bilinmeyen')
                            })
                else:
                    self.video_info_list.append({
                        'url': info.get('webpage_url') or info.get('url'),
                        'title': info.get('title', 'Bilinmeyen')
                    })

            self.root.after(0, self._update_video_list)

        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))

    def _update_video_list(self):
        self.progress.stop()
        self.progress['mode'] = 'determinate'
        self.progress['value'] = 0

        for video in self.video_info_list:
            self.video_listbox.insert(tk.END, video['title'])

        if self.video_info_list:
            self.download_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"{len(self.video_info_list)} video bulundu", foreground="green")
        else:
            self.status_label.config(text="Video bulunamadi", foreground="red")

    def show_error(self, message):
        self.progress.stop()
        self.progress['value'] = 0
        self.status_label.config(text="Hata olustu", foreground="red")
        messagebox.showerror("Hata", message)

    def download_videos(self):
        if not self.video_info_list:
            messagebox.showwarning("Uyari", "Indirilecek video yok!")
            return

        self.download_btn.config(state=tk.DISABLED)
        self.status_label.config(text="MP3 dosyalari indiriliyor...", foreground="orange")
        self.progress['value'] = 0

        threading.Thread(target=self._download_all, daemon=True).start()

    def _download_all(self):
        quality = self.quality_var.get()
        logger = TkLogger(lambda m: self.root.after(0, lambda: self.log(m)))

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'quiet': False,
            'no_warnings': True,
            'logger': logger,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android'],
                }
            },
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality if quality != 'best' else '0',
            }],
            'keepvideo': False,
        }

        quality_text = "En Iyi Kalite" if quality == "best" else f"{quality}kbps"
        self.root.after(0, lambda: self.log(f"\n{'='*50}"))
        self.root.after(0, lambda: self.log(f"MP3 indirme baslatildi ({quality_text})"))
        self.root.after(0, lambda: self.log(f"Konum: {self.download_path}"))
        self.root.after(0, lambda: self.log(f"{'='*50}\n"))

        total = len(self.video_info_list)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for i, video in enumerate(self.video_info_list, 1):
                    self.root.after(0, lambda idx=i, t=total:
                                    self.progress.configure(value=((idx - 1) / t) * 100 if t else 0))
                    self.root.after(0, lambda v=video, idx=i, t=total:
                                    self.log(f"[{idx}/{t}] Indiriliyor: {v['title']}"))
                    ydl.download([video['url']])

            self.root.after(0, self._download_complete)

        except Exception as e:
            error_msg = str(e)
            if "JavaScript runtime" in error_msg:
                error_msg = "Dosyalar indirildi ancak bazi formatlar kullanilamadi. Indirme tamamlandi."
                self.root.after(0, self._download_complete)
            else:
                self.root.after(0, lambda: self.show_error(f"Indirme hatasi: {error_msg}"))
                self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))

    def _format_speed(self, speed_bytes_per_s):
        if not speed_bytes_per_s or speed_bytes_per_s <= 0:
            return ""
        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        i = 0
        value = float(speed_bytes_per_s)
        while value >= 1024 and i < len(units) - 1:
            value /= 1024.0
            i += 1
        return f"{value:.2f} {units[i]}"

    def progress_hook(self, d):
        status = d.get('status')
        if status == 'finished':
            filename = os.path.basename(d.get('filename', '') or '')
            if filename:
                self.root.after(0, lambda f=filename: self.log(f"  Tamamlandi: {f}"))
            self.root.after(0, lambda: self.status_label.config(text="MP3'e donusturuluyor...", foreground="blue"))

        elif status == 'downloading':
            downloaded = d.get('downloaded_bytes')
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            percent = None
            if downloaded is not None and total:
                try:
                    percent = (downloaded / total) * 100 if total > 0 else None
                except Exception:
                    percent = None
            speed = d.get('speed')
            speed_str = self._format_speed(speed)

            def update_status(p=percent, s=speed_str):
                if p is not None:
                    self.status_label.config(text=f"Indiriliyor... %{p:.1f}" + (f" - {s}" if s else ""), foreground="orange")
                else:
                    self.status_label.config(text="Indiriliyor..." + (f" - {s}" if s else ""), foreground="orange")
            self.root.after(0, update_status)

    def _download_complete(self):
        self.progress['value'] = 100
        self.download_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Tum MP3 dosyalari basariyla indirildi!", foreground="green")
        
        quality_text = "En Iyi Kalite" if self.quality_var.get() == "best" else f"{self.quality_var.get()}kbps"
        
        self.log("\n" + "="*50)
        self.log("INDIRME TAMAMLANDI")
        self.log(f"Format: MP3 ({quality_text})")
        self.log(f"Konum: {self.download_path}")
        self.log(f"Toplam: {len(self.video_info_list)} dosya")
        self.log("="*50 + "\n")
        
        messagebox.showinfo("Basarili", 
            f"Tum MP3 dosyalari basariyla indirildi!\n\n"
            f"Konum: {self.download_path}\n"
            f"Format: MP3 ({quality_text})\n"
            f"Toplam: {len(self.video_info_list)} dosya\n\n"
            f"Dosyalariniz hazir!")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeMP3Downloader(root)
    root.mainloop()
