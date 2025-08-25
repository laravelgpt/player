import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
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
        self.conversion_options = {
            "C# to VB.NET": "cs_to_vb",
            "VB.NET to C#": "vb_to_cs",
            "Delphi to C#": "delphi_to_cs",
            "C# to Delphi": "cs_to_delphi",
            "Delphi to VB.NET": "delphi_to_vb",
            "VB.NET to Delphi": "vb_to_delphi"
        }
        for text, value in self.conversion_options.items():
            ctk.CTkRadioButton(self.sidebar, text=text, variable=self.conversion_type, value=value).pack(pady=5, padx=10, anchor="w")

        # Convert button
        self.convert_button = ctk.CTkButton(self.sidebar, text="Convert Files", command=self.start_conversion)
        self.convert_button.pack(pady=10, padx=10)

        # Status bar
        self.status_bar = ctk.CTkLabel(root, text="Ready", anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # File preview area
        self.preview_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
        self.preview_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def browse_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Code Files", "*.cs *.vb *.pas")])
        self.update_selected_files(files)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.endswith((".cs", ".vb", ".pas")):
                        files.append(os.path.join(root, filename))
            self.update_selected_files(files)

    def update_selected_files(self, files):
        self.selected_files_listbox.delete(0, tk.END)
        for file in files:
            self.selected_files_listbox.insert(tk.END, file)

    def clear_selection(self):
        self.selected_files_listbox.delete(0, tk.END)
        self.preview_text.delete(1.0, tk.END)

    def load_file_preview(self, event):
        selected_files = self.selected_files_listbox.curselection()
        if selected_files:
            file_path = self.selected_files_listbox.get(selected_files[0])
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Unable to load file: {str(e)}")

    def start_conversion(self):
        files = self.selected_files_listbox.get(0, tk.END)
        if not files:
            messagebox.showwarning("No Files", "Please select files to convert.")
            return
        
        self.status_bar.configure(text="Converting...")
        Thread(target=self.convert_files, args=(files,)).start()

    def convert_files(self, files):
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    input_code = f.read()
                
                conversion_type = self.conversion_type.get()
                output_code = self.perform_conversion(input_code, conversion_type)
                
                output_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All Files", "*.*")])
                if output_file:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(output_code)
                    messagebox.showinfo("Success", f"Converted file saved: {output_file}")

            except Exception as e:
                messagebox.showerror("Error", f"Error converting {file}: {str(e)}")
        
        self.status_bar.configure(text="Ready")

    def perform_conversion(self, code, conversion_type):
        if conversion_type == "cs_to_vb":
            return re.sub(r"public class (\w+)", r"Public Class \1", code)
        elif conversion_type == "vb_to_cs":
            return re.sub(r"Public Class (\w+)", r"public class \1", code)
        elif conversion_type == "delphi_to_cs":
            return code.replace("begin", "{").replace("end;", "}")
        elif conversion_type == "cs_to_delphi":
            return code.replace("{", "begin").replace("}", "end;")
        elif conversion_type == "delphi_to_vb":
            return code.replace("begin", "Sub Main()").replace("end;", "End Sub")
        elif conversion_type == "vb_to_delphi":
            return code.replace("Sub Main()", "begin").replace("End Sub", "end;")
        else:
            return "Conversion not supported."

if __name__ == "__main__":
    root = ctk.CTk()
    app = CodeConverterApp(root)
    root.mainloop()