import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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
import pyautogui
import numpy as np
import fitz  # PyMuPDF for PDF handling
import pandas as pd  # For CSV and Excel handling
# Import necessary modules for video and audio conversion
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip  # For video subclip extraction

from moviepy.audio.io.AudioFileClip import AudioFileClip  # For audio manipulation
from moviepy import VideoFileClip  # For video and audio conversion
from docx import Document  # For DOCX handling
from pdf2docx import Converter  # For PDF to DOCX conversion

# Set theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Initialize audio mixer with specific settings
mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

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
            values=["mp4", "avi", "mov", "mp3", "wav", "flac", "mkv", "jpg", "png", "gif", "pdf", "docx", "txt", "xls", "csv", "php", "py", "c", "cs", "vb"]
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

        self.conversion_percentage_label = ctk.CTkLabel(self.sidebar, text="0%", fg_color="transparent", text_color="white")
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

        # Video Recording Format Selection
        self.recording_format_var = tk.StringVar(value="mp4")
        self.recording_format_menu = ctk.CTkOptionMenu(
            self.recorder_frame, variable=self.recording_format_var, 
            values=["mp4", "avi", "mov"]
        )
        self.recording_format_menu.pack(fill="x", padx=5, pady=5)

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

        # Volume Slider in Footer
        self.create_volume_slider()

        def create_volume_slider(self):
            self.volume_var = tk.DoubleVar(value=50)  # Default volume set to 50%
            self.volume_slider = ctk.CTkSlider(self.footer, from_=0, to=100, variable=self.volume_var, command=self.set_volume)
            self.volume_slider.pack(side="right", padx=10)
        # Auto-Repeat Playback Checkbox in Footer
        self.auto_repeat_var = tk.BooleanVar(value=False)
        self.auto_repeat_checkbox = ctk.CTkCheckBox(self.footer, text="Auto-Repeat Playback", variable=self.auto_repeat_var, text_color="white")
        self.auto_repeat_checkbox.pack(side="left", padx=10)

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
            self.preview_file()

    def preview_file(self):
        """Preview the selected file in the video player frame."""
        if self.selected_file:
            file_extension = os.path.splitext(self.selected_file)[1].lower()

            if file_extension in [".mp4", ".avi", ".mov", ".mkv", ".webm"]:
                self.play_video()
            elif file_extension in [".jpg", ".png", ".gif"]:
                self.preview_image()
            elif file_extension in [".pdf", ".docx", ".txt", ".xls", ".xlsx", ".csv"]:
                self.preview_document()

    def preview_image(self):
        """Preview an image in the video player frame."""
        img = Image.open(self.selected_file)
        img = img.resize((self.video_label.winfo_width(), self.video_label.winfo_height()))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.configure(image=imgtk)
        self.video_label.image = imgtk

    def preview_document(self):
        """Preview a document in the video player frame."""
        file_extension = os.path.splitext(self.selected_file)[1].lower()

        if file_extension == ".pdf":
            self.preview_pdf()
        elif file_extension in [".docx", ".txt"]:
            self.preview_text()
        elif file_extension in [".xls", ".xlsx", ".csv"]:
            self.preview_spreadsheet()

    def preview_pdf(self):
        """Preview a PDF file in the video player frame."""
        doc = fitz.open(self.selected_file)
        page = doc.load_page(0)  # Load the first page
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = img.resize((self.video_label.winfo_width(), self.video_label.winfo_height()))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.configure(image=imgtk)
        self.video_label.image = imgtk

    def preview_text(self):
        """Preview a text-based document in the video player frame."""
        if self.selected_file.endswith(".docx"):
            doc = Document(self.selected_file)
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            with open(self.selected_file, "r", encoding="utf-8") as file:
                text = file.read()
        self.video_label.configure(text=text, font=("Arial", 12), justify="left")

    def preview_spreadsheet(self):
        """Preview a spreadsheet in the video player frame."""
        if self.selected_file.endswith(".csv"):
            df = pd.read_csv(self.selected_file)
        else:
            df = pd.read_excel(self.selected_file)
        self.video_label.configure(text=df.to_string(), font=("Arial", 12), justify="left")

    def convert_file(self):
        if not self.selected_file:
            messagebox.showerror("Error", "No file selected!")
            return

        target_format = self.format_var.get()
        output_file = filedialog.asksaveasfilename(defaultextension=f".{target_format}")

        if output_file:
            try:
                ext = os.path.splitext(self.selected_file)[1].lower()
                conversion_map = {
                    ".pdf": self.convert_pdf,
                    ".docx": self.convert_docx,
                    ".txt": self.convert_txt,
                    ".jpg": self.convert_image,
                    ".png": self.convert_image,
                    ".gif": self.convert_image,
                    ".mp4": self.convert_video,
                    ".avi": self.convert_video,
                    ".mov": self.convert_video,
                    ".mkv": self.convert_video,
                    ".mp3": self.convert_audio,
                    ".wav": self.convert_audio,
                    ".flac": self.convert_audio,
                    ".php": self.convert_code,
                    ".py": self.convert_code,
                    ".c": self.convert_code,
                    ".cs": self.convert_code,
                    ".vb": self.convert_code
                }

                if ext in conversion_map:
                    conversion_map[ext](target_format, output_file)
                else:
                    messagebox.showerror("Error", "Unsupported file format!")
            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed: {e}")

    def convert_pdf(self, target_format, output_file):
        """Convert PDF to other formats."""
        if target_format == "docx":
            cv = Converter(self.selected_file)
            cv.convert(output_file, start=0, end=None)
            cv.close()
        elif target_format in ["xls", "xlsx"]:
            doc = fitz.open(self.selected_file)
            text = ""
            for page in doc:
                text += page.get_text()
            df = pd.DataFrame([text.split("\n")])
            df.to_excel(output_file, index=False)
        elif target_format in ["jpg", "png"]:
            doc = fitz.open(self.selected_file)
            page = doc.load_page(0)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.save(output_file)
        else:
            messagebox.showerror("Error", "Unsupported target format for PDF!")
        messagebox.showinfo("Success", f"{target_format.upper()} saved successfully!")

    def convert_docx(self, target_format, output_file):
        """Convert DOCX to other formats."""
        if target_format == "pdf":
            doc = Document(self.selected_file)
            doc.save(output_file)
        elif target_format == "txt":
            doc = Document(self.selected_file)
            text = "\n".join([para.text for para in doc.paragraphs])
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(text)
        else:
            messagebox.showerror("Error", "Unsupported target format for DOCX!")
        messagebox.showinfo("Success", f"{target_format.upper()} saved successfully!")

    def convert_txt(self, target_format, output_file):
        """Convert TXT to other formats."""
        if target_format == "docx":
            doc = Document()
            with open(self.selected_file, "r", encoding="utf-8") as file:
                for line in file:
                    doc.add_paragraph(line.strip())
            doc.save(output_file)
        elif target_format in ["xls", "xlsx"]:
            with open(self.selected_file, "r", encoding="utf-8") as file:
                lines = file.readlines()
            df = pd.DataFrame([lines])
            df.to_excel(output_file, index=False)
        elif target_format == "csv":
            with open(self.selected_file, "r", encoding="utf-8") as file:
                lines = file.readlines()
            df = pd.DataFrame([lines])
            df.to_csv(output_file, index=False)
        elif target_format in ["jpg", "png", "gif"]:
            img = Image.new("RGB", (800, 600), color="white")
            with open(self.selected_file, "r", encoding="utf-8") as file:
                text = file.read()
            img.save(output_file)
        else:
            messagebox.showerror("Error", "Unsupported target format for TXT!")
        messagebox.showinfo("Success", f"{target_format.upper()} saved successfully!")

    def convert_image(self, target_format, output_file):
        """Convert image formats."""
        img = Image.open(self.selected_file)
        img.save(output_file)
        messagebox.showinfo("Success", f"{target_format.upper()} saved successfully!")

    def convert_audio(self, target_format, output_file):
        """Convert audio formats."""
        command = [
            "ffmpeg", "-i", self.selected_file,
            "-vn", "-acodec", "copy", output_file
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        threading.Thread(target=self.monitor_conversion, args=(process,), daemon=True).start()

    def convert_code(self, target_format, output_file):
        """Convert code files between different languages."""
        with open(self.selected_file, "r", encoding="utf-8") as file:
            code = file.read()

        if target_format == "py":
            converted_code = self.convert_to_python(code)
        elif target_format == "php":
            converted_code = self.convert_to_php(code)
        elif target_format == "c":
            converted_code = self.convert_to_c(code)
        elif target_format == "cs":
            converted_code = self.convert_to_csharp(code)
        elif target_format == "vb":
            converted_code = self.convert_to_vb(code)
        else:
            messagebox.showerror("Error", "Unsupported target format for code!")
            return

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(converted_code)
        messagebox.showinfo("Success", f"{target_format.upper()} saved successfully!")

    def convert_to_python(self, code):
        """Convert code to Python."""
        # Implement conversion logic here
        # This is a placeholder implementation
        return "# Converted to Python\n" + code

    def convert_to_php(self, code):
        """Convert code to PHP."""
        # Implement conversion logic here
        # This is a placeholder implementation
        return "<?php\n// Converted to PHP\n" + code + "\n?>"

    def convert_to_c(self, code):
        """Convert code to C."""
        # Implement conversion logic here
        # This is a placeholder implementation
        return "/* Converted to C */\n" + code

    def convert_to_csharp(self, code):
        """Convert code to C#."""
        # Implement conversion logic here
        # This is a placeholder implementation
        return "// Converted to C#\n" + code

    def convert_to_vb(self, code):
        """Convert code to VB."""
        # Implement conversion logic here
        # This is a placeholder implementation
        return "' Converted to VB\n" + code

    def convert_video(self, target_format, output_file):
        """Convert video formats."""
        command = [
            "ffmpeg", "-i", self.selected_file,
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",  # High-quality video settings
        "-c:a", "aac", "-b:a", "320k",  # High-quality audio settings
        output_file
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Thread to monitor conversion progress
        threading.Thread(target=self.monitor_conversion, args=(process,), daemon=True).start()

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
            mixer.music.set_volume(1.0)  
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
                    self.media_playing = False
                    self.play_button.configure(state=tk.NORMAL)
                    self.pause_button.configure(state=tk.DISABLED)
                    self.stop_button.configure(state=tk.DISABLED)
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

    def set_volume(self, volume):
        """Set the volume for audio playback."""
        mixer.music.set_volume(volume / 100)

    def create_volume_slider(self):
        """Create a volume slider in the footer."""
        self.volume_var = tk.DoubleVar(value=50)  # Default volume set to 50%
        self.volume_slider = ctk.CTkSlider(self.footer, from_=0, to=100, variable=self.volume_var, command=self.set_volume)
        self.volume_slider.pack(side="right", padx=10)

    # Screen Recorder Functions
    def start_recording(self):
        self.output_file = filedialog.asksaveasfilename(defaultextension=f".{self.recording_format_var.get()}")
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
                self.start_x, self.start_y, self.end_x, self.end_y, outline="red", tags="rect")

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