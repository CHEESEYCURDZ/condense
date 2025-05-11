import os
import subprocess
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
import json
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "condense_settings.json")

DEFAULT_SETTINGS = {
    "frame_limit": "60",
    "bitrate": "2000k",
    "audio_enabled": True,
    "resolution": "1080p",
    "two_pass": False,
    "output_folder": "",
    "theme_color": "#1f6aa5",
    "compression_level": "Balanced",
    "preset": "Medium",
} 

PRESET_PROFILES = {
    "Ultra": {
        "bitrate": "8000k",
        "frame_limit": "60",
        "resolution": "1080p",
        "compression_level": "High Quality",
        "two_pass": True,
        "audio_enabled": True,
    },
    "High": {
        "bitrate": "5000k",
        "frame_limit": "60",
        "resolution": "1080p",
        "compression_level": "Balanced",
        "two_pass": False,
        "audio_enabled": True,
    },
    "Medium": {
        "bitrate": "2500k",
        "frame_limit": "30",
        "resolution": "720p",
        "compression_level": "Balanced",
        "two_pass": False,
        "audio_enabled": True,
    },
    "Low": {
        "bitrate": "1000k",
        "frame_limit": "30",
        "resolution": "480p",
        "compression_level": "Fast",
        "two_pass": False,
        "audio_enabled": False,
    },
}

class CondenseApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.settings = self.load_settings()
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.geometry("360x240")
        self.configure(bg="#121212")

        self.file_path = None

        self.make_title_bar()

        self.container = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self.label = ctk.CTkLabel(self.container, text="Select or drop a video file", text_color="#E0E0E0", font=ctk.CTkFont(size=14))
        self.label.pack(pady=(20, 10))

        self.status = ctk.CTkLabel(self.container, text="", text_color="#E0E0E0", wraplength=300, font=ctk.CTkFont(size=12))
        self.status.pack(pady=(0, 10))

        self.select_video_button = ctk.CTkButton(self.container, text="Select Video", command=self.select_video, fg_color=self.settings["theme_color"])
        self.select_video_button.pack(pady=5, fill="x", padx=60)

        self.compress_button = ctk.CTkButton(self.container, text="Compress Video", command=self.start_compression, state="disabled", fg_color=self.settings["theme_color"])
        self.compress_button.pack(pady=5, fill="x", padx=60)

        self.footer = ctk.CTkLabel(self.container, text="(C) TheCondenseTeam", font=ctk.CTkFont(size=10), text_color="#555555")
        self.footer.pack(side="bottom", pady=(0, 5))

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def make_title_bar(self):
        self.title_bar = ctk.CTkFrame(self, height=32, fg_color="#1a1a1a")
        self.title_bar.pack(fill="x", side="top")

        self.title_label = ctk.CTkLabel(self.title_bar, text="Condense", text_color="#ffffff", font=("Segoe UI", 12))
        self.title_label.pack(side="left", padx=10)

        self.settings_button = ctk.CTkLabel(self.title_bar, text="⚙", text_color="#cccccc", font=("Segoe UI", 13))
        self.settings_button.pack(side="right", padx=(0, 10))
        self.settings_button.bind("<Enter>", lambda e: self.settings_button.configure(text_color="#66ccff"))
        self.settings_button.bind("<Leave>", lambda e: self.settings_button.configure(text_color="#cccccc"))
        self.settings_button.bind("<Button-1>", lambda e: self.open_settings())

        self.close_button = ctk.CTkLabel(self.title_bar, text="✕", text_color="#cccccc", font=("Segoe UI", 12))
        self.close_button.pack(side="right", padx=5)
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

    def start_compression(self):
        if not self.file_path:
            return
        output_folder = self.settings.get("output_folder")
        if not output_folder:
            self.status.configure(text="Please set an output folder in settings.")
            return

        compression_thread = threading.Thread(target=self.compress_video)
        compression_thread.start()

    def compress_video(self):
        self.compress_button.configure(state="disabled")
        self.status.configure(text="Compressing...")

        output_folder = self.settings.get("output_folder")
        output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(self.file_path))[0] + "_compressed.mp4")
        ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")

        if not os.path.exists(ffmpeg_path):
            self.status.configure(text="FFmpeg not found!")
            self.compress_button.configure(state="normal")
            return

        cmd = [ffmpeg_path, "-i", self.file_path]

        if self.settings["resolution"] == "720p":
            cmd += ["-vf", "scale=-2:720"]
        elif self.settings["resolution"] == "480p":
            cmd += ["-vf", "scale=-2:480"]

        if self.settings["frame_limit"] != "None":
            cmd += ["-r", self.settings["frame_limit"]]

        cmd += ["-vcodec", "libx264", "-preset", "medium", "-b:v", self.settings["bitrate"]]

        if self.settings["two_pass"]:
            cmd += ["-pass", "1"]

        if self.settings["audio_enabled"]:
            cmd += ["-acodec", "aac", "-b:a", "192k", "-ar", "44100"]
        else:
            cmd += ["-an"]

        cmd += ["-movflags", "+faststart", "-y", output_path]

        try:
            subprocess.run(cmd, check=True)
            original_size = os.path.getsize(self.file_path)
            compressed_size = os.path.getsize(output_path)
            original_mb = round(original_size / (1024 * 1024), 2)
            compressed_mb = round(compressed_size / (1024 * 1024), 2)
            self.status.configure(text=f"Compressed to: {compressed_mb}MB from: {original_mb}MB")
        except subprocess.CalledProcessError:
            self.status.configure(text="Compression failed.")
        finally:
            self.compress_button.configure(state="normal")

    def open_settings(self):
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return

        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.geometry("328x395")
        self.settings_window.title("Settings")
        self.settings_window.configure(fg_color="#121212")
        self.settings_window.grab_set()

        ctk.CTkLabel(self.settings_window, text="Settings", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(10, 5), padx=20, columnspan=2)

        ctk.CTkLabel(self.settings_window, text="Output Folder").grid(row=1, column=0, padx=20, pady=5, sticky="w")
        ctk.CTkButton(self.settings_window, text="Select Folder", command=self.select_output_folder).grid(row=1, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(self.settings_window, text="Preset").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.preset_menu = ctk.CTkOptionMenu(self.settings_window, values=list(PRESET_PROFILES.keys()),
                                             variable=ctk.StringVar(value=self.settings["preset"]),
                                             command=lambda v: self.update_setting("preset", v))
        self.preset_menu.grid(row=2, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(self.settings_window, text="Resolution").grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.resolution_menu = ctk.CTkOptionMenu(self.settings_window, values=["1080p", "720p", "480p"],
                                                 variable=ctk.StringVar(value=self.settings["resolution"]),
                                                 command=lambda v: self.update_setting("resolution", v))
        self.resolution_menu.grid(row=3, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(self.settings_window, text="Frame Limit").grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.frame_limit_menu = ctk.CTkOptionMenu(self.settings_window, values=["None", "30", "60"],
                                                  variable=ctk.StringVar(value=self.settings["frame_limit"]),
                                                  command=lambda v: self.update_setting("frame_limit", v))
        self.frame_limit_menu.grid(row=4, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(self.settings_window, text="Bitrate").grid(row=5, column=0, padx=20, pady=5, sticky="w")
        self.bitrate_entry = ctk.CTkEntry(self.settings_window)
        self.bitrate_entry.insert(0, self.settings["bitrate"])
        self.bitrate_entry.grid(row=5, column=1, padx=20, pady=5, sticky="w")

        self.two_pass_check = ctk.CTkCheckBox(self.settings_window, text="Enable 2-Pass", variable=ctk.BooleanVar(value=self.settings["two_pass"]))
        self.two_pass_check.grid(row=6, column=0, padx=20, pady=5, sticky="w", columnspan=2)

        self.audio_check = ctk.CTkCheckBox(self.settings_window, text="Enable Audio", variable=ctk.BooleanVar(value=self.settings["audio_enabled"]))
        self.audio_check.grid(row=7, column=0, padx=20, pady=5, sticky="w", columnspan=2)

        ctk.CTkLabel(self.settings_window, text="Compression Level").grid(row=8, column=0, padx=20, pady=5, sticky="w")
        self.compression_menu = ctk.CTkOptionMenu(self.settings_window, values=["Fast", "Balanced", "High Quality"],
                                                  variable=ctk.StringVar(value=self.settings["compression_level"]),
                                                  command=lambda v: self.update_setting("compression_level", v))
        self.compression_menu.grid(row=8, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkButton(self.settings_window, text="Save Settings", command=self.save_settings).grid(row=9, column=0, columnspan=2, padx=20, pady=10)

    def update_setting(self, key, value):
        self.settings[key] = value
        if key == "preset" and value in PRESET_PROFILES:
            self.apply_preset(PRESET_PROFILES[value])

    def apply_preset(self, preset_values):
        self.settings.update(preset_values)
        self.bitrate_entry.delete(0, "end")
        self.bitrate_entry.insert(0, self.settings["bitrate"])
        self.resolution_menu.set(self.settings["resolution"])
        self.frame_limit_menu.set(self.settings["frame_limit"])
        self.compression_menu.set(self.settings["compression_level"])

        if self.settings["two_pass"]:
            self.two_pass_check.select()
        else:
            self.two_pass_check.deselect()

        if self.settings["audio_enabled"]:
            self.audio_check.select()
        else:
            self.audio_check.deselect()

    def save_settings(self):
        self.settings["bitrate"] = self.bitrate_entry.get()
        self.settings["two_pass"] = self.two_pass_check.get()
        self.settings["audio_enabled"] = self.audio_check.get()
        with open(SETTINGS_PATH, "w") as f:
            json.dump(self.settings, f, indent=4)
        self.settings_window.destroy()

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.settings["output_folder"] = folder_path

    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                return json.load(f)
        return DEFAULT_SETTINGS.copy()

if __name__ == "__main__":
    app = CondenseApp()
    app.mainloop()
