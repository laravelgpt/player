import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import time

class CodeConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Converter")
        self.root.geometry("1000x700")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.sidebar_frame = ctk.CTkFrame(root, width=250, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        self.main_frame = ctk.CTkFrame(root, corner_radius=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.processed_files = {}
        self.current_file = None
        self.conversion_type = tk.StringVar(value="VB2PY")  # Default conversion

        self.create_sidebar()
        self.create_main_content()

    def create_sidebar(self):
        title_label = ctk.CTkLabel(self.sidebar_frame, text="Code Converter",
                                 font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 20))

        buttons = [
            ("Select File", self.select_file),
            ("Select Folder", self.select_folder),
            ("Convert All", self.convert_all),
            ("Save Converted", self.save_converted),
            ("Clear", self.clear_text),
            ("Exit", self.root.quit)
        ]

        for btn_text, command in buttons:
            ctk.CTkButton(self.sidebar_frame, text=btn_text, command=command,
                         height=40).pack(pady=5, padx=20, fill="x")

        # Conversion type selection
        conv_frame = ctk.CTkFrame(self.sidebar_frame)
        conv_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(conv_frame, text="Conversion Type:").pack(pady=(0, 5))
        conversions = [
            ("VB.NET to Python", "VB2PY"),
            ("Python to VB.NET", "PY2VB"),
            ("Python to C#", "PY2CS"),
            ("C# to Python", "CS2PY"),
            ("C# to VB.NET", "CS2VB"),
            ("VB.NET to C#", "VB2CS")
        ]
        for text, value in conversions:
            ctk.CTkRadioButton(conv_frame, text=text, variable=self.conversion_type,
                             value=value, command=self.update_preview).pack(pady=2)

        self.file_list_label = ctk.CTkLabel(self.sidebar_frame, text="Loaded Files:")
        self.file_list_label.pack(pady=(20, 5))

        self.file_listbox = tk.Listbox(self.sidebar_frame, height=10)
        self.file_listbox.pack(padx=20, pady=5, fill="x")
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

    def create_main_content(self):
        self.preview_var = tk.BooleanVar(value=True)
        preview_switch = ctk.CTkSwitch(self.main_frame, text="Show Original (ON) / Converted (OFF)",
                                     variable=self.preview_var, command=self.toggle_preview)
        preview_switch.pack(pady=5)

        self.text_label = ctk.CTkLabel(self.main_frame, text="Code Preview:")
        self.text_label.pack(pady=(0, 5))

        self.text_box = ctk.CTkTextbox(self.main_frame, height=300)
        self.text_box.pack(fill="both", expand=True, pady=5)

        self.progress_label = ctk.CTkLabel(self.main_frame, text="Conversion Progress:")
        self.progress_label.pack(pady=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)

        self.log_label = ctk.CTkLabel(self.main_frame, text="Processing Log:")
        self.log_label.pack(pady=(10, 5))

        self.log_text = ctk.CTkTextbox(self.main_frame, height=100)
        self.log_text.pack(fill="x", pady=5)
        self.log_text.configure(state="disabled")

    def add_log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def select_file(self):
        conv_type = self.conversion_type.get()
        if conv_type in ["VB2PY", "VB2CS"]:
            filetypes = [("VB.NET files", "*.vb")]
        elif conv_type in ["PY2VB", "PY2CS"]:
            filetypes = [("Python files", "*.py")]
        else:  # CS2PY, CS2VB
            filetypes = [("C# files", "*.cs")]
        
        file_path = filedialog.askopenfilename(filetypes=filetypes + [("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.processed_files[file_path] = {'original': file.read(), 'converted': None}
                self.update_file_list()
                self.file_listbox.select_set(0)
                self.on_file_select(None)
                self.add_log(f"Loaded single file: {os.path.basename(file_path)}")
            except Exception as e:
                self.add_log(f"Error loading file: {str(e)}")

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            try:
                conv_type = self.conversion_type.get()
                ext = ".vb" if conv_type in ["VB2PY", "VB2CS"] else ".py" if conv_type in ["PY2VB", "PY2CS"] else ".cs"
                files = [f for f in os.listdir(folder_path) if f.endswith(ext)]
                
                if not files:
                    self.add_log(f"No {ext} files found in folder")
                    return

                for file in files:
                    file_path = os.path.join(folder_path, file)
                    with open(file_path, 'r') as f:
                        self.processed_files[file_path] = {'original': f.read(), 'converted': None}

                self.update_file_list()
                self.file_listbox.select_set(0)
                self.on_file_select(None)
                self.add_log(f"Loaded {len(files)} files from folder")
            except Exception as e:
                self.add_log(f"Error processing folder: {str(e)}")

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file_path in self.processed_files.keys():
            self.file_listbox.insert(tk.END, os.path.basename(file_path))

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_file = list(self.processed_files.keys())[index]
            self.toggle_preview()

    def toggle_preview(self):
        if not self.current_file:
            return
        
        self.text_box.delete("1.0", tk.END)
        conv_type = self.conversion_type.get()
        source_lang = "VB.NET" if conv_type.startswith("VB") else "Python" if conv_type.startswith("PY") else "C#"
        target_lang = "Python" if conv_type.endswith("PY") else "VB.NET" if conv_type.endswith("VB") else "C#"
        
        if self.preview_var.get():
            self.text_box.insert("1.0", self.processed_files[self.current_file]['original'])
            self.text_label.configure(text=f"Original {source_lang} Code:")
        else:
            if self.processed_files[self.current_file]['converted']:
                self.text_box.insert("1.0", self.processed_files[self.current_file]['converted'])
            else:
                self.text_box.insert("1.0", "Not converted yet")
            self.text_label.configure(text=f"Converted {target_lang} Code:")

    def update_preview(self):
        self.convert_all()  # Reconvert when changing type
        self.toggle_preview()

    def convert_all(self):
        if not self.processed_files:
            self.add_log("No files to convert")
            return

        total_files = len(self.processed_files)
        self.progress_bar.set(0)
        conv_type = self.conversion_type.get()
        
        for i, (file_path, data) in enumerate(self.processed_files.items()):
            self.add_log(f"Converting: {os.path.basename(file_path)}")
            if conv_type == "VB2PY":
                converted = self.vb_to_python(data['original'])
            elif conv_type == "PY2VB":
                converted = self.python_to_vb(data['original'])
            elif conv_type == "PY2CS":
                converted = self.python_to_cs(data['original'])
            elif conv_type == "CS2PY":
                converted = self.cs_to_python(data['original'])
            elif conv_type == "CS2VB":
                converted = self.cs_to_vb(data['original'])
            else:  # VB2CS
                converted = self.vb_to_cs(data['original'])
            
            self.processed_files[file_path]['converted'] = converted
            progress = (i + 1) / total_files
            self.progress_bar.set(progress)
            self.root.update()
            time.sleep(0.1)

        self.add_log(f"Completed conversion of {total_files} files")
        if self.current_file:
            self.toggle_preview()

    def vb_to_python(self, vb_code):
        code = vb_code
        code = code.replace("Dim ", "")
        code = code.replace("As String", "")
        code = code.replace("As Integer", "")
        code = code.replace("Console.WriteLine", "print")
        code = code.replace("End Sub", "")
        code = code.replace("Sub ", "def ")
        code = code.replace("()", "():")
        code = code.replace("End If", "")
        code = code.replace("If ", "if ")
        code = code.replace(" Then", ":")
        
        lines = code.split('\n')
        indent_level = 0
        return "\n".join(self._format_lines(lines, indent_level, ":"))

    def python_to_vb(self, py_code):
        code = py_code
        code = code.replace("def ", "Sub ")
        code = code.replace("():", "()")
        code = code.replace("print(", "Console.WriteLine(")
        code = code.replace("if ", "If ")
        code = code.replace(":", " Then")
        
        lines = code.split('\n')
        indent_level = 0
        formatted = self._format_lines(lines, indent_level, "Then")
        formatted.append("End Sub")
        return "\n".join(formatted)

    def python_to_cs(self, py_code):
        code = py_code
        code = code.replace("def ", "static void ")
        code = code.replace("():", "() {")
        code = code.replace("print(", "Console.WriteLine(")
        code = code.replace(":", " {")
        
        lines = code.split('\n')
        indent_level = 0
        formatted = self._format_lines(lines, indent_level, "{", closing="}")
        formatted.append("}")
        return "\n".join(formatted)

    def cs_to_python(self, cs_code):
        code = cs_code
        code = code.replace("static void ", "def ")
        code = code.replace("() {", "():")
        code = code.replace("Console.WriteLine", "print")
        code = code.replace(" {", ":")
        code = code.replace("}", "")
        
        lines = code.split('\n')
        indent_level = 0
        return "\n".join(self._format_lines(lines, indent_level, ":"))

    def cs_to_vb(self, cs_code):
        code = cs_code
        code = code.replace("static void ", "Sub ")
        code = code.replace("() {", "()")
        code = code.replace("}", "End Sub")
        code = code.replace(" {", " Then")
        code = code.replace("Console.WriteLine", "Console.WriteLine")
        
        lines = code.split('\n')
        indent_level = 0
        return "\n".join(self._format_lines(lines, indent_level, "Then"))

    def vb_to_cs(self, vb_code):
        code = vb_code
        code = code.replace("Sub ", "static void ")
        code = code.replace("()", "() {")
        code = code.replace("End Sub", "}")
        code = code.replace(" Then", " {")
        code = code.replace("End If", "}")
        
        lines = code.split('\n')
        indent_level = 0
        return "\n".join(self._format_lines(lines, indent_level, "{"))

    def _format_lines(self, lines, indent_level, block_marker, closing=None):
        formatted = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                if block_marker in stripped:
                    formatted.append("    " * indent_level + stripped)
                    indent_level += 1
                elif closing and stripped == closing:
                    indent_level = max(0, indent_level - 1)
                    formatted.append("    " * indent_level + stripped)
                else:
                    formatted.append("    " * indent_level + stripped)
            else:
                formatted.append("")
        return formatted

    def save_converted(self):
        if not self.processed_files:
            self.add_log("No files to save")
            return

        unconverted = [f for f, d in self.processed_files.items() if d['converted'] is None]
        if unconverted:
            self.add_log("Please convert all files before saving")
            return

        save_dir = filedialog.askdirectory(title="Select Folder to Save Converted Files")
        if not save_dir:
            self.add_log("Save operation cancelled")
            return

        try:
            total_files = len(self.processed_files)
            self.progress_bar.set(0)
            conv_type = self.conversion_type.get()
            ext = ".py" if conv_type.endswith("PY") else ".vb" if conv_type.endswith("VB") else ".cs"
            
            for i, (file_path, data) in enumerate(self.processed_files.items()):
                filename = os.path.splitext(os.path.basename(file_path))[0] + ext
                save_path = os.path.join(save_dir, filename)
                
                with open(save_path, 'w') as f:
                    f.write(data['converted'])
                
                self.add_log(f"Saved: {filename}")
                progress = (i + 1) / total_files
                self.progress_bar.set(progress)
                self.root.update()
                time.sleep(0.1)

            self.add_log(f"Saved {total_files} files to {save_dir}")
        except Exception as e:
            self.add_log(f"Error saving files: {str(e)}")

    def clear_text(self):
        self.processed_files.clear()
        self.current_file = None
        self.text_box.delete("1.0", tk.END)
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
        self.file_listbox.delete(0, tk.END)
        self.progress_bar.set(0)
        self.add_log("Cleared all data")

def main():
    root = ctk.CTk()
    app = CodeConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()