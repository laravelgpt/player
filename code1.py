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
        self.root.geometry("1000x800")

        # Set theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Input file selection
        self.file_label = ctk.CTkLabel(root, text="Select Files:")
        self.file_label.pack(pady=5)
        self.file_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=100, height=10)
        self.file_listbox.pack(pady=5)
        self.browse_button = ctk.CTkButton(root, text="Browse Files", command=self.browse_files)
        self.browse_button.pack(pady=5)

        # Conversion options
        self.conversion_type = tk.StringVar(value="cs_to_vb")
        self.cs_to_vb_radio = ctk.CTkRadioButton(root, text="C# to VB.NET", variable=self.conversion_type, value="cs_to_vb")
        self.vb_to_cs_radio = ctk.CTkRadioButton(root, text="VB.NET to C#", variable=self.conversion_type, value="vb_to_cs")
        self.cs_to_py_radio = ctk.CTkRadioButton(root, text="C# to Python", variable=self.conversion_type, value="cs_to_py")
        self.vb_to_py_radio = ctk.CTkRadioButton(root, text="VB.NET to Python", variable=self.conversion_type, value="vb_to_py")
        self.cs_to_vb_radio.pack(pady=5)
        self.vb_to_cs_radio.pack(pady=5)
        self.cs_to_py_radio.pack(pady=5)
        self.vb_to_py_radio.pack(pady=5)

        # Progress bar and percentage
        self.progress_label = ctk.CTkLabel(root, text="Progress:")
        self.progress_label.pack(pady=5)
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=800, mode="determinate")
        self.progress_bar.pack(pady=5)
        self.percentage_label = ctk.CTkLabel(root, text="0%")
        self.percentage_label.pack(pady=5)

        # Preview code area
        self.preview_label = ctk.CTkLabel(root, text="Preview Converted Code:")
        self.preview_label.pack(pady=5)
        self.preview_text = scrolledtext.ScrolledText(root, width=100, height=20, state="disabled")
        self.preview_text.pack(pady=5)

        # Convert button
        self.convert_button = ctk.CTkButton(root, text="Convert Files", command=self.start_conversion)
        self.convert_button.pack(pady=10)

    def browse_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Code Files", "*.cs *.vb *.py")])
        for file in files:
            self.file_listbox.insert(tk.END, file)

    def start_conversion(self):
        files = self.file_listbox.get(0, tk.END)
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
                if conversion_type == "cs_to_vb":
                    output_code = self.convert_cs_to_vb(input_code)
                elif conversion_type == "vb_to_cs":
                    output_code = self.convert_vb_to_cs(input_code)
                elif conversion_type == "cs_to_py":
                    output_code = self.convert_cs_to_py(input_code)
                elif conversion_type == "vb_to_py":
                    output_code = self.convert_vb_to_py(input_code)
                else:
                    output_code = "Unsupported conversion type."

                # Update preview
                self.preview_text.config(state="normal")
                self.preview_text.delete("1.0", tk.END)
                self.preview_text.insert(tk.END, output_code)
                self.preview_text.config(state="disabled")

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

    def convert_cs_to_vb(self, code):
        # Improved C# to VB.NET conversion
        code = re.sub(r"//.*", "'", code)  # Convert single-line comments
        code = re.sub(r"\{", "Begin", code)  # Replace { with Begin
        code = re.sub(r"\}", "End", code)  # Replace } with End
        code = re.sub(r"public class (\w+)", r"Public Class \1", code)  # Convert class declaration
        code = re.sub(r"public void (\w+)\s*\(", r"Public Sub \1(", code)  # Convert method declaration
        code = re.sub(r"public int (\w+)\s*\{", r"Public Property \1 As Integer", code)  # Convert properties
        code = re.sub(r"Console.WriteLine\(", r"Console.WriteLine(", code)  # Convert method calls
        return code

    def convert_vb_to_cs(self, code):
        # Improved VB.NET to C# conversion
        code = re.sub(r"'.*", "//", code)  # Convert single-line comments
        code = re.sub(r"Begin", "{", code)  # Replace Begin with {
        code = re.sub(r"End", "}", code)  # Replace End with }
        code = re.sub(r"Public Class (\w+)", r"public class \1", code)  # Convert class declaration
        code = re.sub(r"Public Sub (\w+)\s*\(", r"public void \1(", code)  # Convert method declaration
        code = re.sub(r"Public Property (\w+) As Integer", r"public int \1 { get; set; }", code)  # Convert properties
        code = re.sub(r"Console.WriteLine\(", r"Console.WriteLine(", code)  # Convert method calls
        return code

    def convert_cs_to_py(self, code):
        # Placeholder for C# to Python conversion logic
        return "C# to Python conversion not implemented yet."

    def convert_vb_to_py(self, code):
        # Placeholder for VB.NET to Python conversion logic
        return "VB.NET to Python conversion not implemented yet."

if __name__ == "__main__":
    root = ctk.CTk()
    app = CodeConverterApp(root)
    root.mainloop()