import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import customtkinter as ctk
import threading
import time
import subprocess
import sys
import shutil
import requests
import zipfile
from pygame import mixer
import re

# Set theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Initialize audio mixer
mixer.init()

def install_ffmpeg():
    """Install FFmpeg automatically if it's not already installed."""
    try:
        # Check if FFmpeg is installed
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("FFmpeg is already installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg not found. Installing FFmpeg...")
        try:
            if sys.platform == "win32":
                # Download FFmpeg for Windows
                ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
                ffmpeg_zip = "ffmpeg.zip"
                ffmpeg_dir = "ffmpeg"

                # Download FFmpeg
                print("Downloading FFmpeg...")
                response = requests.get(ffmpeg_url, stream=True)
                with open(ffmpeg_zip, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Extract FFmpeg
                print("Extracting FFmpeg...")
                with zipfile.ZipFile(ffmpeg_zip, "r") as zip_ref:
                    zip_ref.extractall(ffmpeg_dir)

                # Move FFmpeg executable to the current directory
                for root, dirs, files in os.walk(ffmpeg_dir):
                    if "ffmpeg.exe" in files:
                        ffmpeg_path = os.path.join(root, "ffmpeg.exe")
                        shutil.move(ffmpeg_path, ".")
                        break

                # Clean up
                os.remove(ffmpeg_zip)
                shutil.rmtree(ffmpeg_dir)

                print("FFmpeg installed successfully.")
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["brew", "install", "ffmpeg"], check=True)
            elif sys.platform == "linux":  # Linux
                subprocess.run(["sudo", "apt-get", "install", "ffmpeg", "-y"], check=True)
            else:
                raise Exception("Unsupported operating system.")
        except Exception as e:
            print(f"Failed to install FFmpeg: {e}")
            messagebox.showerror("Error", "Failed to install FFmpeg. Please install it manually.")

# Install FFmpeg if not already installed
install_ffmpeg()

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Converter & Player")
        self.root.geometry("1200x800")
        self.root.configure(bg="black")

        # Grid Configuration
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Sidebar (Conversion Options)
        self.sidebar = ctk.CTkFrame(root, width=250, fg_color="#333")
        self.sidebar.grid(row=0, column=0, padx=5, pady=5, sticky="nsw")

        self.file_button = ctk.CTkButton(self.sidebar, text="📂 Select File", command=self.select_file)
        self.file_button.pack(pady=10)

        self.format_var = tk.StringVar(value="mp4")
        self.format_menu = ctk.CTkOptionMenu(
            self.sidebar, variable=self.format_var, 
            values=["mp4", "avi", "mov", "mp3", "wav", "flac", "mkv", "jpg", "png", "pdf", "docx", "txt"]
        )
        self.format_menu.pack(pady=10)

        # Video Quality Selection
        self.quality_var = tk.StringVar(value="720p")
        self.quality_menu = ctk.CTkOptionMenu(
            self.sidebar, variable=self.quality_var, 
            values=["480p", "720p", "1080p"]
        )
        self.quality_menu.pack(pady=10)

        self.convert_button = ctk.CTkButton(self.sidebar, text="🔄 Convert", command=self.convert_file)
        self.convert_button.pack(pady=10)

        # Conversion Progress Bar with Percentage
        self.conversion_progress_var = tk.DoubleVar()
        self.conversion_progress_bar = ctk.CTkProgressBar(self.sidebar, variable=self.conversion_progress_var, width=200)
        self.conversion_progress_bar.pack(pady=5)

        self.conversion_percentage_label = ctk.CTkLabel(self.sidebar, text="0%", fg_color="transparent", text_color="white")
        self.conversion_percentage_label.pack(pady=5)

        # Main Player Frame (Auto-Resize)
        self.main_frame = ctk.CTkFrame(root, fg_color="black")
        self.main_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.video_label = tk.Label(self.main_frame, text="Video Player", bg="black", fg="white")
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Footer (Fixed at the bottom)
        self.footer = ctk.CTkFrame(root, fg_color="#333")
        self.footer.grid(row=1, column=0, columnspan=2, sticky="sew", padx=5, pady=5)

        # Video Progress Bar at Top of Footer
        self.video_progress_var = tk.DoubleVar()
        self.video_progress_bar = ctk.CTkProgressBar(self.footer, variable=self.video_progress_var, width=800)
        self.video_progress_bar.pack(fill="x", pady=5, side="top")

        # Bind click event to progress bar for seeking
        self.video_progress_bar.bind("<Button-1>", self.seek_video)

        # Control Buttons (Centered)
        self.button_frame = ctk.CTkFrame(self.footer, fg_color="#333")
        self.button_frame.pack(expand=True)

        self.play_button = ctk.CTkButton(self.button_frame, text="▶ Play", command=self.play_media, state=tk.DISABLED)
        self.play_button.pack(side="left", padx=5)

        self.pause_button = ctk.CTkButton(self.button_frame, text="⏸ Pause", command=self.pause_media, state=tk.DISABLED)
        self.pause_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(self.button_frame, text="⏹ Stop", command=self.stop_media, state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=5)

        self.backward_button = ctk.CTkButton(self.button_frame, text="⏪ -10s", command=self.backward_video, state=tk.DISABLED)
        self.backward_button.pack(side="left", padx=5)

        self.forward_button = ctk.CTkButton(self.button_frame, text="⏩ +10s", command=self.forward_video, state=tk.DISABLED)
        self.forward_button.pack(side="left", padx=5)

        self.fullscreen_button = ctk.CTkButton(self.button_frame, text="🔳 Full Screen", command=self.full_screen, state=tk.DISABLED)
        self.fullscreen_button.pack(side="left", padx=5)

        # Variables
        self.selected_file = None
        self.cap = None
        self.media_playing = False
        self.media_paused = False
        self.total_frames = 0
        self.current_frame = 0
        self.conversion_process = None

    def select_file(self):
        self.selected_file = filedialog.askopenfilename()
        if self.selected_file:
            self.play_button.configure(state=tk.NORMAL)
            self.fullscreen_button.configure(state=tk.NORMAL)
            self.file_button.configure(text=f"Selected: {os.path.basename(self.selected_file)}")

    def convert_file(self):
        if not self.selected_file:
            messagebox.showerror("Error", "No file selected!")
            return

        target_format = self.format_var.get()
        output_file = filedialog.asksaveasfilename(defaultextension=f".{target_format}")

        if output_file:
            try:
                # Get selected quality
                quality = self.quality_var.get()
                if quality == "480p":
                    resolution = "854x480"
                elif quality == "720p":
                    resolution = "1280x720"
                elif quality == "1080p":
                    resolution = "1920x1080"
                else:
                    resolution = "1280x720"  # Default to 720p

                command = ["ffmpeg", "-i", self.selected_file, "-vf", f"scale={resolution}", output_file]
                self.conversion_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

                # Thread to monitor conversion progress
                threading.Thread(target=self.monitor_conversion, args=(self.conversion_process,), daemon=True).start()
            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed: {e}")

    def monitor_conversion(self, process):
        """Monitor FFmpeg conversion progress and update the progress bar."""
        duration = 0
        for line in process.stderr:
            if "Duration" in line:
                match = re.search(r"Duration: (\d+):(\d+):(\d+).\d+", line)
                if match:
                    duration = int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3))
            if "time=" in line:
                match = re.search(r"time=(\d+):(\d+):(\d+).\d+", line)
                if match and duration > 0:
                    current_time = int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3))
                    progress = current_time / duration
                    self.conversion_progress_var.set(progress)
                    self.conversion_percentage_label.configure(text=f"{int(progress * 100)}%")
                    self.root.update_idletasks()

        process.wait()
        if process.returncode == 0:
            messagebox.showinfo("Success", "File converted successfully!")
        else:
            messagebox.showerror("Error", "Conversion failed.")

    def play_media(self):
        if not self.selected_file:
            return

        file_extension = os.path.splitext(self.selected_file)[1].lower()

        if file_extension in [".mp4", ".avi", ".mov", ".mkv", ".webm"]:
            self.media_playing = True
            self.media_paused = False
            self.play_button.configure(state=tk.DISABLED)
            self.pause_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.NORMAL)
            self.forward_button.configure(state=tk.NORMAL)
            self.backward_button.configure(state=tk.NORMAL)

            threading.Thread(target=self.play_video, daemon=True).start()

        elif file_extension in [".mp3", ".wav", ".flac"]:
            mixer.music.load(self.selected_file)
            mixer.music.play()
            self.media_playing = True
            self.play_button.configure(state=tk.DISABLED)
            self.pause_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.NORMAL)

    def play_video(self):
        self.cap = cv2.VideoCapture(self.selected_file)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while self.cap.isOpened() and self.media_playing:
            if self.media_paused:
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if not ret:
                break  

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            width, height = self.video_label.winfo_width(), self.video_label.winfo_height()
            frame = cv2.resize(frame, (width, height))

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk

            self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.video_progress_var.set(self.current_frame / self.total_frames)

            self.root.update_idletasks()
            self.root.update()

        self.cap.release()

    def pause_media(self):
        self.media_paused = not self.media_paused
        self.pause_button.configure(text="▶ Resume" if self.media_paused else "⏸ Pause")

    def stop_media(self):
        self.media_playing = False
        self.play_button.configure(state=tk.NORMAL)
        self.pause_button.configure(state=tk.DISABLED, text="⏸ Pause")
        self.stop_button.configure(state=tk.DISABLED)
        self.video_progress_var.set(0)

    def forward_video(self):
        if self.cap:
            self.current_frame += 300  # Forward by 10 seconds (300 frames approx)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

    def backward_video(self):
        if self.cap:
            self.current_frame -= 300  # Backward by 10 seconds (300 frames approx)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

    def seek_video(self, event):
        """Seek to a specific position in the video based on progress bar click."""
        if self.cap:
            progress = event.x / self.video_progress_bar.winfo_width()
            self.current_frame = int(progress * self.total_frames)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

    def full_screen(self):
        self.root.attributes("-fullscreen", True)
        self.fullscreen_button.configure(text="🔲 Exit Full Screen", command=self.exit_fullscreen)

    def exit_fullscreen(self):
        self.root.attributes("-fullscreen", False)
        self.fullscreen_button.configure(text="🔳 Full Screen", command=self.full_screen)


if __name__ == "__main__":
    root = ctk.CTk()
    app = ConverterApp(root)
    root.mainloop()