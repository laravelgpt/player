import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, UnidentifiedImageError
import cv2
import customtkinter as ctk
import threading
import time
import subprocess
import sys
from pygame import mixer

# Set theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Check FFmpeg
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        messagebox.showerror("Error", "FFmpeg is not installed. Please install FFmpeg and add it to PATH.")
        sys.exit(1)

check_ffmpeg()
mixer.init()  # Initialize audio mixer

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Converter & Player")
        self.root.geometry("1200x800")
        self.root.configure(bg="black")

        # Grid Configuration
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Sidebar (Full Height)
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

        self.convert_button = ctk.CTkButton(self.sidebar, text="🔄 Convert", command=self.convert_file)
        self.convert_button.pack(pady=10)

        # Main Player Frame (Auto-Resize)
        self.main_frame = ctk.CTkFrame(root, fg_color="black")
        self.main_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.video_label = tk.Label(self.main_frame, text="Video Player", bg="black", fg="white")
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Controls
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.pack(fill="x", pady=5)

        self.play_button = ctk.CTkButton(self.control_frame, text="▶ Play", command=self.play_media, state=tk.DISABLED)
        self.play_button.pack(side="left", padx=5)

        self.pause_button = ctk.CTkButton(self.control_frame, text="⏸ Pause", command=self.pause_media, state=tk.DISABLED)
        self.pause_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(self.control_frame, text="⏹ Stop", command=self.stop_media, state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=5)

        self.backward_button = ctk.CTkButton(self.control_frame, text="⏪ -10s", command=self.backward_video, state=tk.DISABLED)
        self.backward_button.pack(side="left", padx=5)

        self.forward_button = ctk.CTkButton(self.control_frame, text="⏩ +10s", command=self.forward_video, state=tk.DISABLED)
        self.forward_button.pack(side="left", padx=5)

        self.fullscreen_button = ctk.CTkButton(self.control_frame, text="🔳 Full Screen", command=self.full_screen, state=tk.DISABLED)
        self.fullscreen_button.pack(side="left", padx=5)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, variable=self.progress_var, width=800)
        self.progress_bar.pack(fill="x", pady=5)

        # Variables
        self.selected_file = None
        self.cap = None
        self.media_playing = False
        self.media_paused = False
        self.total_frames = 0
        self.current_frame = 0

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
                command = ["ffmpeg", "-i", self.selected_file, output_file]
                subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                messagebox.showinfo("Success", "File converted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed: {e}")

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
            self.progress_var.set(self.current_frame / self.total_frames)

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
        self.progress_var.set(0)

    def forward_video(self):
        if self.cap:
            self.current_frame += 300  # Forward by 10 seconds (300 frames approx)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

    def backward_video(self):
        if self.cap:
            self.current_frame -= 300  # Backward by 10 seconds (300 frames approx)
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
