"""
YouTube Downloader Pro v2.0 - Fixed Width + Scrolling
Author: 3Bhussein
GitHub: https://github.com/3Bhussein/YouTube-Downloader-Pro
"""

import sys
import os
import threading
from pathlib import Path
import subprocess

try:
    import yt_dlp
except ImportError:
    print("ERROR: yt-dlp not installed! Run: pip install yt-dlp")
    input("Press Enter to exit...")
    sys.exit(1)

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    print("ERROR: tkinter not found!")
    input("Press Enter to exit...")
    sys.exit(1)

class YouTubeDownloaderPro:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro v2.0 - By 3Bhussein")
        self.root.geometry("800x650")
        self.root.configure(bg="#0f0f0f")
        self.root.minsize(750, 600)
        
        self.center_window()
        
        # Variables
        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.format_var = tk.StringVar(value="mp4")
        self.quality_var = tk.StringVar(value="1080p")
        self.video_info = None
        self.available_formats = []
        
        # Colors
        self.colors = {
            'bg_dark': '#0f0f0f', 'bg_card': '#1a1a1a', 'bg_input': '#2a2a2a',
            'accent': '#ff0000', 'accent_hover': '#cc0000', 'success': '#00c853',
            'warning': '#ff9800', 'text_primary': '#ffffff', 'text_secondary': '#b3b3b3',
            'border': '#3a3a3a',
        }
        
        self.setup_ui()
        self.check_dependencies()
    
    def center_window(self):
        self.root.update_idletasks()
        width = 800
        height = 650
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def check_dependencies(self):
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            self.ffmpeg_available = True
            self.status_label.config(text="✅ FFmpeg detected - Full quality available", fg=self.colors['success'])
        except:
            self.ffmpeg_available = False
            self.status_label.config(text="⚠️ FFmpeg not installed - 1080p+ requires FFmpeg", fg=self.colors['warning'])
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill="both", expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=770)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build content
        self.build_content(self.scrollable_frame)
    
    def build_content(self, parent):
        # Padding
        content_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        header_frame = tk.Frame(content_frame, bg=self.colors['bg_card'], height=110)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎬 YouTube Downloader Pro", 
                              font=("Segoe UI", 24, "bold"), fg=self.colors['text_primary'], bg=self.colors['bg_card'])
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(header_frame, text="Download videos & audio with real-time progress | By 3Bhussein",
                                 font=("Segoe UI", 9), fg=self.colors['text_secondary'], bg=self.colors['bg_card'])
        subtitle_label.pack()
        
        # URL Card
        url_card = self.create_card(content_frame, "📹 Video URL")
        url_card.pack(fill="x", pady=(0, 12))
        
        url_input_frame = tk.Frame(url_card, bg=self.colors['bg_card'])
        url_input_frame.pack(fill="x", padx=12, pady=8)
        
        self.url_entry = tk.Entry(url_input_frame, font=("Segoe UI", 10), bg=self.colors['bg_input'],
                                 fg=self.colors['text_primary'], insertbackground=self.colors['text_primary'],
                                 relief="flat", bd=0)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=")
        self.url_entry.bind('<FocusIn>', lambda e: self.url_entry.delete(0, tk.END) if self.url_entry.get() == "https://www.youtube.com/watch?v=" else None)
        self.url_entry.bind('<Return>', lambda e: self.start_download())
        
        self.fetch_info_btn = self.create_styled_button(url_input_frame, "🔍 Get Info", self.fetch_video_info, '#9c27b0')
        self.fetch_info_btn.pack(side="right")
        
        # Video Info Card
        self.info_card = self.create_card(content_frame, "ℹ️ Video Information")
        self.info_card.pack(fill="x", pady=(0, 12))
        
        self.info_frame = tk.Frame(self.info_card, bg=self.colors['bg_card'], height=90)
        self.info_frame.pack(fill="x", padx=12, pady=8)
        self.info_frame.pack_propagate(False)
        
        self.info_label = tk.Label(self.info_frame, text="Enter a YouTube URL and click 'Get Info'",
                                  font=("Segoe UI", 9), fg=self.colors['text_secondary'], bg=self.colors['bg_card'])
        self.info_label.pack(expand=True)
        
        # Format Card
        format_card = self.create_card(content_frame, "🎯 Format & Quality")
        format_card.pack(fill="x", pady=(0, 12))
        
        buttons_frame = tk.Frame(format_card, bg=self.colors['bg_card'])
        buttons_frame.pack(fill="x", padx=12, pady=8)
        
        self.video_btn = self.create_toggle_button(buttons_frame, "🎥 Video (MP4)", 'video')
        self.video_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.audio_btn = self.create_toggle_button(buttons_frame, "🎵 Audio (MP3)", 'audio')
        self.audio_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        self.set_button_active(self.video_btn)
        
        # Quality selection
        quality_frame = tk.Frame(format_card, bg=self.colors['bg_card'])
        quality_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        quality_label = tk.Label(quality_frame, text="Quality:", font=("Segoe UI", 9, "bold"),
                                fg=self.colors['text_primary'], bg=self.colors['bg_card'])
        quality_label.pack(side="left", padx=(0, 8))
        
        self.quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var,
                                         values=["2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p"],
                                         state="readonly", width=22)
        self.quality_combo.pack(side="left")
        
        self.quality_info = tk.Label(format_card, text="💡 Click 'Get Info' first to see available qualities",
                                    font=("Segoe UI", 8), fg=self.colors['warning'], bg=self.colors['bg_card'])
        self.quality_info.pack(pady=(0, 8))
        
        # Save Card
        save_card = self.create_card(content_frame, "💾 Save Location")
        save_card.pack(fill="x", pady=(0, 12))
        
        path_frame = tk.Frame(save_card, bg=self.colors['bg_card'])
        path_frame.pack(fill="x", padx=12, pady=8)
        
        self.path_entry = tk.Entry(path_frame, textvariable=self.download_path, font=("Segoe UI", 9),
                                  bg=self.colors['bg_input'], fg=self.colors['text_primary'], relief="flat")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        browse_btn = self.create_styled_button(path_frame, "📁 Browse", self.browse_folder, '#3498db')
        browse_btn.pack(side="right")
        
        # Progress Card
        progress_card = self.create_card(content_frame, "📊 Download Progress")
        progress_card.pack(fill="x", pady=(0, 12))
        
        self.percentage_label = tk.Label(progress_card, text="0%", font=("Segoe UI", 24, "bold"),
                                        fg=self.colors['accent'], bg=self.colors['bg_card'])
        self.percentage_label.pack(pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(progress_card, mode='determinate')
        self.progress_bar.pack(fill="x", padx=15, pady=8)
        
        details_frame = tk.Frame(progress_card, bg=self.colors['bg_card'])
        details_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        self.speed_label = tk.Label(details_frame, text="Speed: -- MB/s", font=("Segoe UI", 8),
                                   fg=self.colors['text_secondary'], bg=self.colors['bg_card'])
        self.speed_label.pack(side="left")
        
        self.eta_label = tk.Label(details_frame, text="ETA: --", font=("Segoe UI", 8),
                                 fg=self.colors['text_secondary'], bg=self.colors['bg_card'])
        self.eta_label.pack(side="right")
        
        self.size_label = tk.Label(progress_card, text="File size: -- MB", font=("Segoe UI", 8),
                                  fg=self.colors['text_secondary'], bg=self.colors['bg_card'])
        self.size_label.pack(pady=(0, 5))
        
        self.status_label = tk.Label(progress_card, text="✅ Ready to download", font=("Segoe UI", 9),
                                    fg=self.colors['success'], bg=self.colors['bg_card'])
        self.status_label.pack(pady=(0, 10))
        
        # DOWNLOAD BUTTON
        download_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        download_frame.pack(fill="x", pady=(5, 10))
        
        self.download_btn = tk.Button(download_frame, 
                                     text="⬇️ START DOWNLOAD ⬇️", 
                                     command=self.start_download,
                                     bg=self.colors['accent'], 
                                     fg="white",
                                     font=("Segoe UI", 14, "bold"),
                                     relief="raised", 
                                     cursor="hand2", 
                                     height=1,
                                     bd=2)
        self.download_btn.pack(fill="x", padx=5)
        
        # Footer
        footer_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        footer_frame.pack(fill="x", pady=(5, 0))
        
        footer_label = tk.Label(footer_frame, text="Made with ❤️ by 3Bhussein | Open Source | Free to use",
                               font=("Segoe UI", 7), fg=self.colors['text_secondary'], bg=self.colors['bg_dark'])
        footer_label.pack()
    
    def create_card(self, parent, title):
        card = tk.LabelFrame(parent, text=title, font=("Segoe UI", 9, "bold"),
                            fg=self.colors['accent'], bg=self.colors['bg_card'],
                            relief="flat", bd=1, highlightthickness=1,
                            highlightcolor=self.colors['border'], highlightbackground=self.colors['border'])
        return card
    
    def create_toggle_button(self, parent, text, btn_type):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 9, "bold"),
                       bg=self.colors['bg_input'], fg=self.colors['text_secondary'],
                       relief="flat", cursor="hand2", command=lambda: self.toggle_format(btn_type))
        return btn
    
    def set_button_active(self, button):
        button.configure(bg=self.colors['accent'], fg=self.colors['text_primary'])
    
    def set_button_inactive(self, button):
        button.configure(bg=self.colors['bg_input'], fg=self.colors['text_secondary'])
    
    def create_styled_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 8, "bold"),
                       bg=color, fg="white", relief="flat", cursor="hand2", padx=12, pady=4, command=command)
        
        def on_enter(e): btn.configure(bg=self.lighten_color(color))
        def on_leave(e): btn.configure(bg=color)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn
    
    def lighten_color(self, color):
        colors = {'#3498db': '#5dade2', '#9c27b0': '#b84dcc', '#ff0000': '#ff3333'}
        return colors.get(color, color)
    
    def toggle_format(self, format_type):
        if format_type == 'video':
            self.format_var.set("mp4")
            self.set_button_active(self.video_btn)
            self.set_button_inactive(self.audio_btn)
            if self.available_formats:
                qualities = [f"{f['height']}p ({f['filesize_mb']:.1f} MB)" if f['filesize_mb'] > 0 else f"{f['height']}p" 
                           for f in self.available_formats]
                self.quality_combo.config(values=qualities)
            else:
                self.quality_combo.config(values=["2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p"])
            self.quality_info.config(text="💡 Higher quality = larger file size")
        else:
            self.format_var.set("mp3")
            self.set_button_active(self.audio_btn)
            self.set_button_inactive(self.video_btn)
            self.quality_combo.config(values=["320kbps", "192kbps", "128kbps", "64kbps"])
            self.quality_var.set("192kbps")
            self.quality_info.config(text="💡 Higher bitrate = better audio quality")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)
    
    def fetch_video_info(self):
        url = self.url_entry.get().strip()
        
        if not url or url == "https://www.youtube.com/watch?v=":
            messagebox.showwarning("No URL", "Please enter a YouTube URL")
            return
        
        self.fetch_info_btn.config(state="disabled", text="⏳ Loading...")
        self.status_label.config(text="🔍 Fetching video information...", fg="#3498db")
        
        thread = threading.Thread(target=self.get_video_info, args=(url,))
        thread.daemon = True
        thread.start()
    
    def get_video_info(self, url):
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.video_info = info
                
                formats = []
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' and f.get('height'):
                        height = f.get('height', 0)
                        if height > 0:
                            filesize_mb = f.get('filesize', 0) / 1024 / 1024 if f.get('filesize') else 0
                            formats.append({'height': height, 'filesize_mb': filesize_mb})
                
                unique_qualities = {}
                for f in formats:
                    if f['height'] not in unique_qualities:
                        unique_qualities[f['height']] = f
                
                self.available_formats = sorted(unique_qualities.values(), key=lambda x: x['height'], reverse=True)
                
                qualities = [f"{f['height']}p ({f['filesize_mb']:.1f} MB)" if f['filesize_mb'] > 0 else f"{f['height']}p" 
                           for f in self.available_formats]
                
                self.root.after(0, self.update_video_info, info, qualities)
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get video info:\n{str(e)}"))
            self.root.after(0, self.reset_info_button)
    
    def update_video_info(self, info, qualities):
        title = info.get('title', 'Unknown')[:55]
        duration = info.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"
        channel = info.get('channel', 'Unknown')
        
        info_text = f"📹 {title}\n\n⏱️ Duration: {duration_str} | 📺 Channel: {channel}\n\n📊 Available: {', '.join([q.split(' ')[0] for q in qualities[:4]])}"
        
        self.info_label.config(text=info_text, justify="left", anchor="nw")
        self.info_frame.config(height=100)
        
        if qualities:
            self.quality_combo.config(values=qualities)
            self.quality_var.set(qualities[0])
            self.quality_info.config(text=f"✅ Found {len(qualities)} qualities!", fg=self.colors['success'])
        
        self.reset_info_button()
    
    def reset_info_button(self):
        self.fetch_info_btn.config(state="normal", text="🔍 Get Info")
        self.status_label.config(text="✅ Ready to download", fg=self.colors['success'])
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.root.after(0, self.update_progress, percent, d)
    
    def update_progress(self, percent, d):
        self.percentage_label.config(text=f"{percent:.1f}%")
        self.progress_bar['value'] = percent
        
        if d.get('speed'):
            speed_mb = d['speed'] / 1024 / 1024
            self.speed_label.config(text=f"Speed: {speed_mb:.1f} MB/s")
        
        if d.get('eta'):
            eta = d['eta']
            if eta < 60:
                eta_text = f"ETA: {eta}s"
            else:
                eta_text = f"ETA: {eta // 60}m {eta % 60}s"
            self.eta_label.config(text=eta_text)
        
        if d.get('total_bytes'):
            downloaded_mb = d['downloaded_bytes'] / 1024 / 1024
            total_mb = d['total_bytes'] / 1024 / 1024
            self.size_label.config(text=f"{downloaded_mb:.1f} / {total_mb:.1f} MB")
        
        self.status_label.config(text=f"📥 Downloading... {percent:.1f}%")
    
    def start_download(self):
        url = self.url_entry.get().strip()
        
        if not url or url == "https://www.youtube.com/watch?v=":
            messagebox.showwarning("No URL", "Please enter a valid YouTube URL")
            return
        
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showwarning("Invalid URL", "Please enter a valid YouTube URL")
            return
        
        self.progress_bar['value'] = 0
        self.percentage_label.config(text="0%")
        self.speed_label.config(text="Speed: -- MB/s")
        self.eta_label.config(text="ETA: --")
        self.size_label.config(text="File size: -- MB")
        
        self.download_btn.config(state="disabled", text="⏳ DOWNLOADING... ⏳", bg="#666666")
        self.status_label.config(text="Preparing download...", fg="#3498db")
        
        thread = threading.Thread(target=self.download_video, 
                                 args=(url, self.download_path.get(), 
                                       self.format_var.get(), self.quality_var.get()),
                                 daemon=True)
        thread.start()
    
    def download_video(self, url, save_path, format_type, quality):
        try:
            quality_clean = quality.split()[0] if ' ' in quality else quality
            quality_clean = quality_clean.replace("p", "").replace("kbps", "")
            
            if format_type == "mp3":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': quality_clean if quality_clean.isdigit() else '192',
                    }],
                    'progress_hooks': [self.progress_hook],
                    'quiet': True,
                }
            else:
                selected_height = int(quality_clean) if quality_clean.isdigit() else 1080
                
                if self.ffmpeg_available:
                    format_spec = f'bestvideo[height<={selected_height}]+bestaudio/best[height<={selected_height}]'
                else:
                    format_spec = f'best[height<={selected_height}]'
                
                ydl_opts = {
                    'format': format_spec,
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4',
                    'progress_hooks': [self.progress_hook],
                    'quiet': True,
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Video')
            
            self.root.after(0, lambda: messagebox.showinfo("Success!", 
                                f"✅ Download completed!\n\n📹 {title}\n🎯 Quality: {quality}\n📁 Location: {save_path}"))
            self.root.after(0, self.reset_ui)
            
        except Exception as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower():
                self.root.after(0, lambda: messagebox.showerror("FFmpeg Required", 
                    "FFmpeg is required for this quality!\n\nInstall FFmpeg from ffmpeg.org"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed:\n{error_msg[:300]}"))
            self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        self.download_btn.config(state="normal", text="⬇️ START DOWNLOAD ⬇️", bg=self.colors['accent'])
        self.status_label.config(text="✅ Ready to download", fg=self.colors['success'])

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderPro(root)
    root.mainloop()