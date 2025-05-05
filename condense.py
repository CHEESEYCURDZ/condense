import os
import subprocess
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class CondenseApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.geometry("400x270")
        self.configure(bg="#121212")

        self.file_path = None
        self.output_folder = None

        self.make_title_bar()

        self.container = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        self.container.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        self.label = ctk.CTkLabel(self.container, text="Select or drop a video file", text_color="#E0E0E0", font=ctk.CTkFont(size=14))
        self.label.pack(pady=(20, 10))

        self.status = ctk.CTkLabel(self.container, text="", text_color="#E0E0E0", wraplength=380, font=ctk.CTkFont(size=12))
        self.status.pack(pady=(0, 15))

        self.select_video_button = ctk.CTkButton(self.container, text="Select Video", command=self.select_video)
        self.select_video_button.pack(pady=5, fill="x", padx=60)

        self.choose_folder_button = ctk.CTkButton(self.container, text="Choose Output Folder", command=self.choose_output_folder)
        self.choose_folder_button.pack(pady=5, fill="x", padx=60)

        self.compress_button = ctk.CTkButton(self.container, text="Compress Video", command=self.compress_video, state="disabled")
        self.compress_button.pack(pady=5, fill="x", padx=60)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def make_title_bar(self):
        self.title_bar = ctk.CTkFrame(self, height=32, fg_color="#1a1a1a")
        self.title_bar.pack(fill="x", side="top")

        self.title_label = ctk.CTkLabel(self.title_bar, text="Condense", text_color="#ffffff", font=("Segoe UI", 12))
        self.title_label.pack(side="left", padx=10)

        self.close_button = ctk.CTkLabel(self.title_bar, text="✕", text_color="#cccccc", font=("Segoe UI", 12))
        self.close_button.pack(side="right", padx=10)
        self.close_button.bind("<Enter>", lambda e: self.close_button.configure(text_color="#ff4d4d"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.configure(text_color="#cccccc"))
        self.close_button.bind("<Button-1>", lambda e: self.destroy())

        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.winfo_pointerx() - self._x
        y = self.winfo_pointery() - self._y
        self.geometry(f'+{x}+{y}')

    def handle_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isfile(path) and path.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
            self.file_path = path
            self.status.configure(text=f"Selected: {os.path.basename(path)}")
            self.compress_button.configure(state="normal")
        else:
            self.status.configure(text="Invalid file type")

    def select_video(self):
        file_path = filedialog.askopenfilename(title="Select a Video File", filetypes=[("Video files", "*.mp4;*.mov;*.mkv;*.avi")])
        if file_path:
            self.file_path = file_path
            self.status.configure(text=f"Selected: {os.path.basename(file_path)}")
            self.compress_button.configure(state="normal")

    def choose_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            self.status.configure(text=f"Output Folder: {os.path.basename(folder)}")

    def compress_video(self):
        if not self.file_path:
            return
        if not self.output_folder:
            self.status.configure(text="Please choose an output folder.")
            return

        self.compress_button.configure(state="disabled")
        self.status.configure(text="Compressing...")

        output_path = os.path.join(self.output_folder, os.path.splitext(os.path.basename(self.file_path))[0] + "_8mb.mp4")
        ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")

        if not os.path.exists(ffmpeg_path):
            self.status.configure(text="FFmpeg not found!")
            self.compress_button.configure(state="normal")
            return

        cmd = [
            ffmpeg_path, "-i", self.file_path,
            "-vcodec", "libx264", "-crf", "18",
            "-preset", "medium",
            "-r", "60",
            "-b:v", "2000k",
            "-minrate", "1000k",
            "-maxrate", "2500k",
            "-bufsize", "5000k",
            "-x264-params", "keyint=60:min-keyint=60",
            "-acodec", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-movflags", "+faststart",
            "-tune", "film",
            "-profile:v", "high",
            "-level", "4.2",
            "-colorspace", "bt709",
            "-y",
            output_path
        ]

        try:
            subprocess.run(cmd, check=True)
            self.status.configure(text=f"Saved to: {output_path}")
        except subprocess.CalledProcessError:
            self.status.configure(text="Compression failed.")
        finally:
            self.compress_button.configure(state="normal")


if __name__ == "__main__":
    app = CondenseApp()
    app.mainloop()
