import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, UnidentifiedImageError, ImageTk
from moviepy import VideoFileClip
import pypandoc
import customtkinter as ctk
import subprocess
import sys
import shutil
from tkinter import ttk
import threading
import webbrowser
from pygame import mixer

# Set appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        messagebox.showerror("Error", "FFmpeg is not installed. Please install FFmpeg manually and add it to PATH.")
        sys.exit(1)

# Ensure FFmpeg is installed
check_ffmpeg()

# Initialize pygame mixer for audio playback
mixer.init()

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal File Converter")
        self.root.geometry("1200x800")  # Make the window wider and taller

        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(root, width=250, height=800)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # File selection button
        self.file_button = ctk.CTkButton(self.sidebar_frame, text="Select File", command=self.select_file)
        self.file_button.grid(row=0, column=0, pady=20, padx=20)

        # Format selection dropdown
        self.format_var = tk.StringVar(value="mp4")
        self.format_menu = ctk.CTkOptionMenu(self.sidebar_frame, variable=self.format_var, values=["mp4", "avi", "mov", "mp3", "wav", "flac", "ogg", "mkv", "jpg", "png", "pdf", "docx", "txt"])
        self.format_menu.grid(row=1, column=0, pady=20, padx=20)

        # Convert button
        self.convert_button = ctk.CTkButton(self.sidebar_frame, text="Convert", command=self.convert_file)
        self.convert_button.grid(row=2, column=0, pady=20, padx=20)

        # File Info and Preview Area
        self.main_frame = ctk.CTkFrame(root, width=900, height=800)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20)

        # File Label
        self.file_label = ctk.CTkLabel(self.main_frame, text="Select a file to convert:", font=("Arial", 14))
        self.file_label.pack(pady=10)

        # Preview label (for images and video/audio playback)
        self.preview_label = ctk.CTkLabel(self.main_frame, text="Preview will appear here", font=("Arial", 12), width=600, height=300)
        self.preview_label.pack(pady=10)

        # Play Button (appears for video/audio)
        self.play_button = ctk.CTkButton(self.main_frame, text="Play", command=self.play_media, state=tk.DISABLED)
        self.play_button.pack(pady=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.main_frame, length=600, mode='indeterminate')
        self.progress_bar.pack(pady=10)

        self.selected_file = None

    def select_file(self):
        self.selected_file = filedialog.askopenfilename()
        if self.selected_file:
            self.file_label.configure(text=f"Selected: {os.path.basename(self.selected_file)}")
            self.preview_file()

    def preview_file(self):
        file_extension = os.path.splitext(self.selected_file)[1].lower()
        if file_extension in [".jpg", ".png", ".gif", ".bmp", ".tiff"]:
            try:
                img = Image.open(self.selected_file)
                img.thumbnail((300, 300))
                img = ImageTk.PhotoImage(img)
                self.preview_label.configure(image=img)
                self.preview_label.image = img
                self.play_button.configure(state=tk.DISABLED)
            except UnidentifiedImageError:
                self.preview_label.configure(text="Unsupported image format.")
                self.play_button.configure(state=tk.DISABLED)
        elif file_extension in [".mp3", ".wav", ".flac", ".ogg"]:
            self.preview_label.configure(text="Audio file preview is not available.")
            self.play_button.configure(state=tk.NORMAL)  # Enable play button for audio
        elif file_extension in [".mp4", ".avi", ".mov", ".mkv", ".mpg", ".webm"]:
            try:
                video = VideoFileClip(self.selected_file)
                self.preview_label.configure(text=f"Video: {video.duration} seconds")
                self.play_button.configure(state=tk.NORMAL)  # Enable play button for video
            except Exception:
                self.preview_label.configure(text="Error loading video preview.")
                self.play_button.configure(state=tk.DISABLED)
        elif file_extension in [".pdf", ".docx", ".txt", ".epub", ".xml", ".html", ".csv", ".pptx", ".doc", ".rtf", ".odt"]:
            self.preview_label.configure(text="Document preview is available.")
            self.play_button.configure(state=tk.DISABLED)
        else:
            self.preview_label.configure(text="Unsupported file format for preview.")
            self.play_button.configure(state=tk.DISABLED)

    def play_media(self):
        if not self.selected_file:
            return

        file_extension = os.path.splitext(self.selected_file)[1].lower()

        if file_extension in [".mp3", ".wav", ".flac", ".ogg"]:
            mixer.music.load(self.selected_file)
            mixer.music.play()
        elif file_extension in [".mp4", ".avi", ".mov", ".mkv", ".webm"]:
            webbrowser.open(self.selected_file)  # Open video in default player (e.g., VLC)

    def convert_file(self):
        if not self.selected_file:
            messagebox.showerror("Error", "No file selected!")
            return

        target_format = self.format_var.get()
        output_file = filedialog.asksaveasfilename(defaultextension=f".{target_format}")

        if output_file:
            threading.Thread(target=self.run_conversion, args=(output_file, target_format)).start()

    def run_conversion(self, output_file, target_format):
        self.progress_bar.start()
        try:
            file_extension = os.path.splitext(self.selected_file)[1].lower()
            if file_extension in [".mp4", ".avi", ".mov", ".mkv", ".flv", ".webm", ".mpg"]:
                self.convert_video(output_file, target_format)
            elif file_extension in [".mp3", ".wav", ".ogg", ".flac"]:
                self.convert_audio(output_file, target_format)
            elif file_extension in [".jpg", ".png", ".gif", ".bmp", ".tiff"]:
                self.convert_image(output_file, target_format)
            elif file_extension in [".pdf", ".docx", ".txt", ".epub", ".xml", ".html", ".csv", ".pptx", ".doc", ".rtf", ".odt"]:
                self.convert_document(output_file, target_format)
            messagebox.showinfo("Success", "File converted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")
        finally:
            self.progress_bar.stop()

    def convert_video(self, output_file, target_format):
        try:
            command = ["ffmpeg", "-i", self.selected_file, "-c:v", "libx264", "-preset", "fast", "-crf", "23", output_file]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception as e:
            raise Exception(f"Video conversion failed: {e}")

    def convert_audio(self, output_file, target_format):
        try:
            command = ["ffmpeg", "-i", self.selected_file, "-q:a", "0", "-map", "a", output_file]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception as e:
            raise Exception(f"Audio conversion failed: {e}")

    def convert_image(self, output_file, target_format):
        try:
            img = Image.open(self.selected_file)
            img.save(output_file, format=target_format.upper())
        except UnidentifiedImageError:
            raise Exception("Unsupported image format!")

    def convert_document(self, output_file, target_format):
        try:
            pypandoc.convert_file(self.selected_file, target_format, outputfile=output_file)
        except Exception as e:
            raise Exception(f"Document conversion failed: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = ConverterApp(root)
    root.mainloop()
