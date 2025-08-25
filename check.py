import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
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
import pyautogui
import numpy as np

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

        # File Selection
        self.file_button = ctk.CTkButton(self.sidebar, text="📂 Select File", command=self.select_file)
        self.file_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Format Selection
        self.format_var = tk.StringVar(value="mp4")
        self.format_menu = ctk.CTkOptionMenu(
            self.sidebar, variable=self.format_var, 
            values=["mp4", "avi", "mov", "mp3", "wav", "flac", "mkv", "jpg", "png", "pdf", "docx", "txt"]
        )
        self.format_menu.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Quality Selection
        self.quality_var = tk.StringVar(value="High")
        self.quality_menu = ctk.CTkOptionMenu(
            self.sidebar, variable=self.quality_var, 
            values=["Low", "Medium", "High", "4K", "8K"]
        )
        self.quality_menu.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Convert Button
        self.convert_button = ctk.CTkButton(self.sidebar, text="🔄 Convert", command=self.convert_file)
        self.convert_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # Conversion Progress Bar with Percentage
        self.conversion_progress_var = tk.DoubleVar()
        self.conversion_progress_bar = ctk.CTkProgressBar(self.sidebar, variable=self.conversion_progress_var, width=200)
        self.conversion_progress_bar.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.conversion_percentage_label = ctk.CTkLabel(self.sidebar, text="0%", fg_color="transparent")
        self.conversion_percentage_label.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        # Screen Recorder Controls in Sidebar
        self.recorder_frame = ctk.CTkFrame(self.sidebar, fg_color="#333")
        self.recorder_frame.grid(row=6, column=0, padx=10, pady=10, sticky="ew")

        self.record_button = ctk.CTkButton(self.recorder_frame, text="⏺ Start Recording", command=self.start_recording)
        self.record_button.pack(fill="x", padx=5, pady=5)

        self.pause_resume_button = ctk.CTkButton(self.recorder_frame, text="⏸ Pause", command=self.pause_resume_recording, state=tk.DISABLED)
        self.pause_resume_button.pack(fill="x", padx=5, pady=5)

        self.stop_rec_button = ctk.CTkButton(self.recorder_frame, text="⏹ Stop", command=self.stop_recording, state=tk.DISABLED)
        self.stop_rec_button.pack(fill="x", padx=5, pady=5)

        # Video Recording Quality Selection
        self.recording_quality_var = tk.StringVar(value="High")
        self.recording_quality_menu = ctk.CTkOptionMenu(
            self.recorder_frame, variable=self.recording_quality_var, 
            values=["Low", "Medium", "High", "4K", "8K"]
        )
        self.recording_quality_menu.pack(fill="x", padx=5, pady=5)

        # Snip Tool Button
        self.snip_button = ctk.CTkButton(self.sidebar, text="✂️ Snip Tool", command=self.start_snipping)
        self.snip_button.grid(row=7, column=0, padx=10, pady=10, sticky="ew")

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

        # Auto-Repeat Playback Checkbox in Footer
        self.auto_repeat_var = tk.BooleanVar(value=False)
        self.auto_repeat_checkbox = ctk.CTkCheckBox(self.footer, text="Auto-Repeat Playback", variable=self.auto_repeat_var)
        self.auto_repeat_checkbox.pack(side="right", padx=10)

        # Variables
        self.selected_file = None
        self.cap = None
        self.media_playing = False
        self.media_paused = False
        self.total_frames = 0
        self.current_frame = 0

        # Screen Recorder Variables
        self.recording = False
        self.paused = False
        self.recording_thread = None
        self.output_file = None

        # Snip Tool Variables
        self.snipping = False
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.snip_canvas = None

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
                quality = self.quality_var.get()
                command = ["ffmpeg", "-i", self.selected_file]

                # Add quality settings based on selection
                if quality == "Low":
                    command.extend(["-b:v", "500k", "-b:a", "128k"])
                elif quality == "Medium":
                    command.extend(["-b:v", "1000k", "-b:a", "192k"])
                elif quality == "High":
                    command.extend(["-b:v", "2000k", "-b:a", "256k"])
                elif quality == "4K":
                    command.extend(["-b:v", "8000k", "-b:a", "320k"])
                elif quality == "8K":
                    command.extend(["-b:v", "16000k", "-b:a", "320k"])

                command.append(output_file)
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

                # Thread to monitor conversion progress
                threading.Thread(target=self.monitor_conversion, args=(process,), daemon=True).start()
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
                if self.auto_repeat_var.get():
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
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

    # Screen Recorder Functions
    def start_recording(self):
        self.output_file = filedialog.asksaveasfilename(defaultextension=".mp4")
        if self.output_file:
            self.recording = True
            self.paused = False
            self.record_button.configure(state=tk.DISABLED, fg_color="green")
            self.pause_resume_button.configure(state=tk.NORMAL)
            self.stop_rec_button.configure(state=tk.NORMAL)
            self.recording_thread = threading.Thread(target=self.record_screen, daemon=True)
            self.recording_thread.start()

    def pause_resume_recording(self):
        self.paused = not self.paused
        self.pause_resume_button.configure(text="▶ Resume" if self.paused else "⏸ Pause")

    def stop_recording(self):
        self.recording = False
        self.record_button.configure(state=tk.NORMAL, fg_color="#1f6aa5")
        self.pause_resume_button.configure(state=tk.DISABLED)
        self.stop_rec_button.configure(state=tk.DISABLED)
        messagebox.showinfo("Success", "Recording saved successfully!")

    def record_screen(self):
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(self.output_file, fourcc, 20.0, screen_size)

        while self.recording:
            if not self.paused:
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)
            time.sleep(0.05)

        out.release()

    # Snip Tool Functions
    def start_snipping(self):
        """Activate the snipping tool."""
        self.snipping = True
        self.root.withdraw()  # Hide the main window
        self.snip_canvas = tk.Toplevel(self.root)
        self.snip_canvas.attributes("-fullscreen", True)
        self.snip_canvas.attributes("-alpha", 0.3)
        self.snip_canvas.configure(cursor="cross")

        # Add a Canvas widget for drawing
        self.canvas = tk.Canvas(self.snip_canvas, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        """Record the starting position of the selection."""
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        """Draw the selection rectangle."""
        if self.canvas:
            self.end_x = event.x
            self.end_y = event.y
            self.canvas.delete("rect")
            self.canvas.create_rectangle(
                self.start_x, self.start_y, self.end_x, self.end_y, outline="red", tags="rect"
            )

    def on_button_release(self, event):
        """Capture the selected region and save it."""
        if self.canvas:
            self.end_x = event.x
            self.end_y = event.y
            self.snip_canvas.destroy()
            self.root.deiconify()  # Restore the main window

            # Ensure coordinates are valid
            if self.start_x > self.end_x:
                self.start_x, self.end_x = self.end_x, self.start_x
            if self.start_y > self.end_y:
                self.start_y, self.end_y = self.end_y, self.start_y

            # Capture the selected region
            screenshot = pyautogui.screenshot(region=(self.start_x, self.start_y, self.end_x - self.start_x, self.end_y - self.start_y))
            output_file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if output_file:
                screenshot.save(output_file)
                messagebox.showinfo("Success", f"Screenshot saved to {output_file}")

        self.snipping = False


if __name__ == "__main__":
    root = ctk.CTk()
    app = ConverterApp(root)
    root.mainloop()