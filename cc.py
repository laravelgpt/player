import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import os
from threading import Thread
import re
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

        # Browse files button
        self.browse_button = ctk.CTkButton(self.sidebar, text="Browse Files", command=self.browse_files)
        self.browse_button.pack(pady=5, padx=10)

        # Browse folder button
        self.browse_folder_button = ctk.CTkButton(self.sidebar, text="Browse Folder", command=self.browse_folder)
        self.browse_folder_button.pack(pady=5, padx=10)

        # Clear button
        self.clear_button = ctk.CTkButton(self.sidebar, text="Clear", command=self.clear_selection)
        self.clear_button.pack(pady=5, padx=10)

        # Selected files label
        self.selected_files_label = ctk.CTkLabel(self.sidebar, text="Selected Files:")
        self.selected_files_label.pack(pady=5, padx=10, anchor="w")

        # Selected files listbox
        self.selected_files_listbox = tk.Listbox(self.sidebar, selectmode=tk.MULTIPLE, width=25, height=10)
        self.selected_files_listbox.pack(pady=5, padx=10)
        self.selected_files_listbox.bind("<<ListboxSelect>>", self.load_file_preview)

        # Conversion options
        self.conversion_type = tk.StringVar(value="cs_to_vb")
        self.cs_to_vb_radio = ctk.CTkRadioButton(self.sidebar, text="C# to VB.NET", variable=self.conversion_type, value="cs_to_vb")
        self.vb_to_cs_radio = ctk.CTkRadioButton(self.sidebar, text="VB.NET to C#", variable=self.conversion_type, value="vb_to_cs")
        self.cs_to_py_radio = ctk.CTkRadioButton(self.sidebar, text="C# to Python", variable=self.conversion_type, value="cs_to_py")
        self.vb_to_py_radio = ctk.CTkRadioButton(self.sidebar, text="VB.NET to Python", variable=self.conversion_type, value="vb_to_py")
        self.cs_to_vb_radio.pack(pady=5, padx=10, anchor="w")
        self.vb_to_cs_radio.pack(pady=5, padx=10, anchor="w")
        self.cs_to_py_radio.pack(pady=5, padx=10, anchor="w")
        self.vb_to_py_radio.pack(pady=5, padx=10, anchor="w")

        # Language version selection
        self.language_version_label = ctk.CTkLabel(self.sidebar, text="Target Language Version:")
        self.language_version_label.pack(pady=5, padx=10, anchor="w")
        self.language_version = tk.StringVar(value="Python 3.x")
        self.language_version_menu = ctk.CTkOptionMenu(self.sidebar, variable=self.language_version, values=["Python 3.x", "C# 9", "VB.NET 16"])
        self.language_version_menu.pack(pady=5, padx=10)

        # Convert button
        self.convert_button = ctk.CTkButton(self.sidebar, text="Convert Files", command=self.start_conversion)
        self.convert_button.pack(pady=10, padx=10)

        # Main content frame
        self.main_content = ctk.CTkFrame(root, corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)

        # First preview area (Original Code)
        self.original_preview_label = ctk.CTkLabel(self.main_content, text="Original Code Preview:")
        self.original_preview_label.pack(pady=5, padx=10, anchor="w")
        self.original_preview_text = scrolledtext.ScrolledText(self.main_content, width=100, height=15, state="normal")
        self.original_preview_text.pack(pady=5, padx=10, fill="both", expand=True)

        # Second preview area (Converted Code)
        self.converted_preview_label = ctk.CTkLabel(self.main_content, text="Converted Code Preview:")
        self.converted_preview_label.pack(pady=5, padx=10, anchor="w")
        self.converted_preview_text = scrolledtext.ScrolledText(self.main_content, width=100, height=15, state="normal")
        self.converted_preview_text.pack(pady=5, padx=10, fill="both", expand=True)

        # Progress bar and percentage
        self.progress_label = ctk.CTkLabel(self.main_content, text="Progress:")
        self.progress_label.pack(pady=5, padx=10, anchor="w")
        self.progress_bar = ttk.Progressbar(self.main_content, orient="horizontal", length=800, mode="determinate")
        self.progress_bar.pack(pady=5, padx=10, fill="x")
        self.percentage_label = ctk.CTkLabel(self.main_content, text="0%")
        self.percentage_label.pack(pady=5, padx=10, anchor="w")

    def browse_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Code Files", "*.cs *.vb *.py")])
        self.update_selected_files(files)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.endswith((".cs", ".vb", ".py")):
                        files.append(os.path.join(root, filename))
            self.update_selected_files(files)

    def update_selected_files(self, files):
        self.selected_files_listbox.delete(0, tk.END)
        for file in files:
            self.selected_files_listbox.insert(tk.END, file)

    def load_file_preview(self, event):
        selected_files = self.selected_files_listbox.curselection()
        if selected_files:
            file_index = selected_files[0]
            file_path = self.selected_files_listbox.get(file_index)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                self.original_preview_text.config(state="normal")
                self.original_preview_text.delete("1.0", tk.END)
                self.original_preview_text.insert(tk.END, file_content)
                self.original_preview_text.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def clear_selection(self):
        self.selected_files_listbox.delete(0, tk.END)
        self.original_preview_text.config(state="normal")
        self.original_preview_text.delete("1.0", tk.END)
        self.original_preview_text.config(state="disabled")
        self.converted_preview_text.config(state="normal")
        self.converted_preview_text.delete("1.0", tk.END)
        self.converted_preview_text.config(state="disabled")
        self.progress_bar["value"] = 0
        self.percentage_label.configure(text="0%")

    def start_conversion(self):
        files = self.selected_files_listbox.get(0, tk.END)
        if not files:
            messagebox.showwarning("No Files", "Please select files to convert.")
            return

        # Reset progress bar and percentage
        self.progress_bar["value"] = 0
        self.percentage_label.configure(text="0%")

        # Start conversion in a separate thread
        Thread(target=self.convert_files, args=(files,)).start()

    def convert_files(self, files):
        total_files = len(files)
        for i, file in enumerate(files):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    input_code = f.read()

                conversion_type = self.conversion_type.get()
                target_version = self.language_version.get()

                if conversion_type == "cs_to_vb":
                    output_code = self.convert_cs_to_vb(input_code, target_version)
                elif conversion_type == "vb_to_cs":
                    output_code = self.convert_vb_to_cs(input_code, target_version)
                elif conversion_type == "cs_to_py":
                    output_code = self.convert_cs_to_py(input_code, target_version)
                elif conversion_type == "vb_to_py":
                    output_code = self.convert_vb_to_py(input_code, target_version)
                else:
                    output_code = "Unsupported conversion type."

                # Update converted preview
                self.converted_preview_text.config(state="normal")
                self.converted_preview_text.delete("1.0", tk.END)
                self.converted_preview_text.insert(tk.END, output_code)
                self.converted_preview_text.config(state="disabled")

                # Save converted file
                output_file = os.path.splitext(file)[0] + f"_converted.{conversion_type.split('_')[-1]}"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(output_code)

                # Update progress bar and percentage
                progress = (i + 1) / total_files * 100
                self.progress_bar["value"] = progress
                self.percentage_label.configure(text=f"{int(progress)}%")
                self.root.update_idletasks()

            except Exception as e:
                messagebox.showerror("Error", f"Error converting {file}: {str(e)}")

        messagebox.showinfo("Complete", "Conversion completed!")

    def convert_cs_to_vb(self, code, target_version):
        # Improved C# to VB.NET conversion
        code = re.sub(r"//.*", "'", code)  # Convert single-line comments
        code = re.sub(r"\{", "Begin", code)  # Replace { with Begin
        code = re.sub(r"\}", "End", code)  # Replace } with End
        code = re.sub(r"public class (\w+)", r"Public Class \1", code)  # Convert class declaration
        code = re.sub(r"public void (\w+)\s*\(", r"Public Sub \1(", code)  # Convert method declaration
        code = re.sub(r"public int (\w+)\s*\{", r"Public Property \1 As Integer", code)  # Convert properties
        code = re.sub(r"Console.WriteLine\(", r"Console.WriteLine(", code)  # Convert method calls
        return code

    def convert_vb_to_cs(self, code, target_version):
        # Improved VB.NET to C# conversion
        code = re.sub(r"'.*", "//", code)  # Convert single-line comments
        code = re.sub(r"Begin", "{", code)  # Replace Begin with {
        code = re.sub(r"End", "}", code)  # Replace End with }
        code = re.sub(r"Public Class (\w+)", r"public class \1", code)  # Convert class declaration
        code = re.sub(r"Public Sub (\w+)\s*\(", r"public void \1(", code)  # Convert method declaration
        code = re.sub(r"Public Property (\w+) As Integer", r"public int \1 { get; set; }", code)  # Convert properties
        code = re.sub(r"Console.WriteLine\(", r"Console.WriteLine(", code)  # Convert method calls
        return code

    def convert_cs_to_py(self, code, target_version):
        # Improved C# to Python conversion
        code = re.sub(r"//.*", "#", code)  # Convert single-line comments
        code = re.sub(r"\{", ":", code)  # Replace { with :
        code = re.sub(r"\}", "", code)  # Remove }
        code = re.sub(r"public class (\w+)", r"class \1:", code)  # Convert class declaration
        code = re.sub(r"public void (\w+)\s*\(", r"def \1(", code)  # Convert method declaration
        code = re.sub(r"Console.WriteLine\(", r"print(", code)  # Convert method calls
        return code

    def convert_vb_to_py(self, code, target_version):
        # Improved VB.NET to Python conversion
        code = re.sub(r"'.*", "#", code)  # Convert single-line comments
        code = re.sub(r"Begin", ":", code)  # Replace Begin with :
        code = re.sub(r"End", "", code)  # Remove End
        code = re.sub(r"Public Class (\w+)", r"class \1:", code)  # Convert class declaration
        code = re.sub(r"Public Sub (\w+)\s*\(", r"def \1(", code)  # Convert method declaration
        code = re.sub(r"Console.WriteLine\(", r"print(", code)  # Convert method calls
        return code

if __name__ == "__main__":
    root = ctk.CTk()
    app = CodeConverterApp(root)
    root.mainloop()