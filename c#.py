import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import os
from threading import Thread
import re
import shutil
import customtkinter as ctk

class CodeConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Converter")
        self.root.geometry("1200x800")

        # Set theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Create sidebar frame
        self.sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Sidebar widgets
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="Options", font=("Arial", 14))
        self.sidebar_label.pack(pady=10, padx=10)

        # Browse project button
        self.browse_project_button = ctk.CTkButton(self.sidebar, text="Browse Project", command=self.browse_project)
        self.browse_project_button.pack(pady=5, padx=10)

        # Clear button
        self.clear_button = ctk.CTkButton(self.sidebar, text="Clear", command=self.clear_selection)
        self.clear_button.pack(pady=5, padx=10)

        # Conversion options
        self.conversion_type = tk.StringVar(value="cs_to_vb")
        self.cs_to_vb_radio = ctk.CTkRadioButton(self.sidebar, text="C# to VB.NET", variable=self.conversion_type, value="cs_to_vb")
        self.vb_to_cs_radio = ctk.CTkRadioButton(self.sidebar, text="VB.NET to C#", variable=self.conversion_type, value="vb_to_cs")
        self.cs_to_vb_radio.pack(pady=5, padx=10, anchor="w")
        self.vb_to_cs_radio.pack(pady=5, padx=10, anchor="w")

        # Convert button
        self.convert_button = ctk.CTkButton(self.sidebar, text="Convert Project", command=self.start_conversion)
        self.convert_button.pack(pady=10, padx=10)

        # Main content frame
        self.main_content = ctk.CTkFrame(root, corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)

        # Preview code area
        self.preview_label = ctk.CTkLabel(self.main_content, text="Preview Code:")
        self.preview_label.pack(pady=5, padx=10, anchor="w")
        self.preview_text = scrolledtext.ScrolledText(self.main_content, width=100, height=20, state="normal")
        self.preview_text.pack(pady=5, padx=10, fill="both", expand=True)

        # Progress bar and percentage
        self.progress_label = ctk.CTkLabel(self.main_content, text="Progress:")
        self.progress_label.pack(pady=5, padx=10, anchor="w")
        self.progress_bar = ttk.Progressbar(self.main_content, orient="horizontal", length=800, mode="determinate")
        self.progress_bar.pack(pady=5, padx=10, fill="x")
        self.percentage_label = ctk.CTkLabel(self.main_content, text="0%")
        self.percentage_label.pack(pady=5, padx=10, anchor="w")

    def browse_project(self):
        project_folder = filedialog.askdirectory()
        if project_folder:
            self.project_folder = project_folder
            self.update_preview(f"Project loaded: {project_folder}")

    def clear_selection(self):
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state="disabled")
        self.progress_bar["value"] = 0
        self.percentage_label.configure(text="0%")

    def start_conversion(self):
        if not hasattr(self, "project_folder"):
            messagebox.showwarning("No Project", "Please select a project folder.")
            return

        # Reset progress bar and percentage
        self.progress_bar["value"] = 0
        self.percentage_label.configure(text="0%")

        # Start conversion in a separate thread
        Thread(target=self.convert_project, args=(self.project_folder,)).start()

    def convert_project(self, project_folder):
        try:
            conversion_type = self.conversion_type.get()
            if conversion_type == "cs_to_vb":
                self.convert_cs_project_to_vb(project_folder)
            elif conversion_type == "vb_to_cs":
                self.convert_vb_project_to_cs(project_folder)
            else:
                messagebox.showerror("Error", "Unsupported conversion type.")
        except Exception as e:
            messagebox.showerror("Error", f"Error converting project: {str(e)}")

    def convert_cs_project_to_vb(self, project_folder):
        # Ask user to select a destination folder
        save_folder = filedialog.askdirectory(title="Select Destination Folder for Converted Project")
        if not save_folder:
            return  # User canceled

        # Copy the project folder to the destination
        converted_folder = os.path.join(save_folder, os.path.basename(project_folder) + "_VB")
        shutil.copytree(project_folder, converted_folder)

        # Convert all .cs files to .vb
        for root, _, files in os.walk(converted_folder):
            for file in files:
                if file.endswith(".cs"):
                    cs_file_path = os.path.join(root, file)
                    vb_file_path = os.path.join(root, file.replace(".cs", ".vb"))

                    with open(cs_file_path, "r", encoding="utf-8") as f:
                        cs_code = f.read()

                    vb_code = self.convert_cs_to_vb(cs_code)

                    with open(vb_file_path, "w", encoding="utf-8") as f:
                        f.write(vb_code)

                    # Remove the original .cs file
                    os.remove(cs_file_path)

        self.update_preview(f"C# to VB.NET conversion completed. Saved to: {converted_folder}")

    def convert_vb_project_to_cs(self, project_folder):
        # Ask user to select a destination folder
        save_folder = filedialog.askdirectory(title="Select Destination Folder for Converted Project")
        if not save_folder:
            return  # User canceled

        # Copy the project folder to the destination
        converted_folder = os.path.join(save_folder, os.path.basename(project_folder) + "_CS")
        shutil.copytree(project_folder, converted_folder)

        # Convert all .vb files to .cs
        for root, _, files in os.walk(converted_folder):
            for file in files:
                if file.endswith(".vb"):
                    vb_file_path = os.path.join(root, file)
                    cs_file_path = os.path.join(root, file.replace(".vb", ".cs"))

                    with open(vb_file_path, "r", encoding="utf-8") as f:
                        vb_code = f.read()

                    cs_code = self.convert_vb_to_cs(vb_code)

                    with open(cs_file_path, "w", encoding="utf-8") as f:
                        f.write(cs_code)

                    # Remove the original .vb file
                    os.remove(vb_file_path)

        self.update_preview(f"VB.NET to C# conversion completed. Saved to: {converted_folder}")

    def convert_cs_to_vb(self, code):
        # Advanced C# to VB.NET conversion logic
        code = re.sub(r"//.*", "'", code)  # Convert single-line comments
        code = re.sub(r"\{", "Begin", code)  # Replace { with Begin
        code = re.sub(r"\}", "End", code)  # Replace } with End
        code = re.sub(r"public class (\w+)", r"Public Class \1", code)  # Convert class declaration
        code = re.sub(r"public void (\w+)\s*\(", r"Public Sub \1(", code)  # Convert method declaration
        code = re.sub(r"public int (\w+)\s*\{", r"Public Property \1 As Integer", code)  # Convert properties
        code = re.sub(r"Console.WriteLine\(", r"Console.WriteLine(", code)  # Convert method calls
        return code

    def convert_vb_to_cs(self, code):
        # Advanced VB.NET to C# conversion logic
        code = re.sub(r"'.*", "//", code)  # Convert single-line comments
        code = re.sub(r"Begin", "{", code)  # Replace Begin with {
        code = re.sub(r"End", "}", code)  # Replace End with }
        code = re.sub(r"Public Class (\w+)", r"public class \1", code)  # Convert class declaration
        code = re.sub(r"Public Sub (\w+)\s*\(", r"public void \1(", code)  # Convert method declaration
        code = re.sub(r"Public Property (\w+) As Integer", r"public int \1 { get; set; }", code)  # Convert properties
        code = re.sub(r"Console.WriteLine\(", r"Console.WriteLine(", code)  # Convert method calls
        return code

    def update_preview(self, message):
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, message)
        self.preview_text.config(state="disabled")

if __name__ == "__main__":
    root = ctk.CTk()
    app = CodeConverterApp(root)
    root.mainloop()