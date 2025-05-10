import os
import subprocess
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
import json

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
    "preset": "Custom"
}

PRESETS = {
    "Low (Discord)": {
        "frame_limit": "30",
        "bitrate": "1000k",
        "audio_enabled": True,
        "resolution": "480p",
        "two_pass": False
    },
    "High": {
        "frame_limit": "60",
        "bitrate": "2000k",
        "audio_enabled": True,
        "resolution": "720p",
        "two_pass": False
    },
    "Ultra": {
        "frame_limit": "60",
        "bitrate": "3000k",
        "audio_enabled": True,
        "resolution": "1080p",
        "two_pass": True
    }
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

        self.compress_button = ctk.CTkButton(self.container, text="Compress Video", command=self.compress_video, state="disabled", fg_color=self.settings["theme_color"])
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

    def compress_video(self):
        if not self.file_path:
            return
        output_folder = self.settings.get("output_folder")
        if not output_folder:
            self.status.configure(text="Please set an output folder in settings.")
            return

        self.compress_button.configure(state="disabled")
        self.status.configure(text="Compressing...")

        output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(self.file_path))[0] + "_8mb.mp4")
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
        self.settings_window.geometry("336x385")
        self.settings_window.title("Settings")
        self.settings_window.configure(fg_color="#121212")
        self.settings_window.grab_set()

        ctk.CTkLabel(self.settings_window, text="Settings", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(self.settings_window, text="Preset").grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.preset_menu = ctk.CTkOptionMenu(self.settings_window, values=["Low (Discord)", "High", "Ultra", "Custom"],
                                             variable=ctk.StringVar(value=self.settings.get("preset", "Custom")),
                                             command=self.apply_preset)
        self.preset_menu.grid(row=1, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(self.settings_window, text="Frame Limit").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.frame_limit_menu = ctk.CTkOptionMenu(self.settings_window, values=["None", "30", "60", "120"],
                                                  variable=ctk.StringVar(value=self.settings["frame_limit"]),
                                                  command=lambda v: self.update_setting("frame_limit", v, True))
        self.frame_limit_menu.grid(row=2, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(self.settings_window, text="Bitrate").grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.bitrate_menu = ctk.CTkOptionMenu(self.settings_window, values=["1000k", "2000k", "3000k"],
                                              variable=ctk.StringVar(value=self.settings["bitrate"]),
                                              command=lambda v: self.update_setting("bitrate", v, True))
        self.bitrate_menu.grid(row=3, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(self.settings_window, text="Resolution").grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.resolution_menu = ctk.CTkOptionMenu(self.settings_window, values=["1080p", "720p", "480p"],
                                                 variable=ctk.StringVar(value=self.settings["resolution"]),
                                                 command=lambda v: self.update_setting("resolution", v, True))
        self.resolution_menu.grid(row=4, column=1, padx=20, pady=5, sticky="w")

        self.audio_var = ctk.BooleanVar(value=self.settings["audio_enabled"])
        self.audio_checkbox = ctk.CTkCheckBox(self.settings_window, text="Enable Audio", variable=self.audio_var,
                                              command=lambda: self.update_setting("audio_enabled", self.audio_var.get(), True))
        self.audio_checkbox.grid(row=5, column=0, padx=20, pady=5, sticky="w")

        self.two_pass_var = ctk.BooleanVar(value=self.settings["two_pass"])
        self.pass_checkbox = ctk.CTkCheckBox(self.settings_window, text="2-pass Encoding", variable=self.two_pass_var,
                                             command=lambda: self.update_setting("two_pass", self.two_pass_var.get(), True))
        self.pass_checkbox.grid(row=6, column=0, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(self.settings_window, text="Default Output Folder").grid(row=7, column=0, padx=20, pady=5, sticky="w")
        output_folder_button = ctk.CTkButton(self.settings_window, text="Select Folder", command=self.select_output_folder)
        output_folder_button.grid(row=7, column=1, padx=20, pady=5, sticky="w")

        save_button = ctk.CTkButton(self.settings_window, text="Save", command=self.save_settings)
        save_button.grid(row=8, column=0, columnspan=2, pady=20)

    def apply_preset(self, preset_name):
        if preset_name in PRESETS:
            for key, value in PRESETS[preset_name].items():
                self.settings[key] = value
            self.settings["preset"] = preset_name
            self.open_settings()
        else:
            self.settings["preset"] = "Custom"

    def update_setting(self, setting, value, mark_custom=False):
        self.settings[setting] = value
        if mark_custom:
            self.settings["preset"] = "Custom"
            self.preset_menu.set("Custom")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.settings["output_folder"] = folder_path

    def save_settings(self):
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(self.settings, f)
        self.settings_window.destroy()

    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r') as f:
                return json.load(f)
        return DEFAULT_SETTINGS


if __name__ == "__main__":
    app = CondenseApp()
    app.mainloop()
