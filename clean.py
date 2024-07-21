import os
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import stat

class GitCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Cleaner Tool")

        self.setup_ui()

    def setup_ui(self):
        # Directory Selection
        self.dir_label = tk.Label(self.root, text="Select a directory to clean:")
        self.dir_label.pack(pady=5)

        self.select_dir_btn = tk.Button(self.root, text="Select Directory", command=self.select_directory)
        self.select_dir_btn.pack(pady=5)

        self.clean_dir_btn = tk.Button(self.root, text="Clean Directory", command=self.clean_selected_directory)
        self.clean_dir_btn.pack(pady=5)

    def select_directory(self):
        self.selected_directory = filedialog.askdirectory()
        if self.selected_directory:
            self.dir_label.config(text=f"Selected Directory: {self.selected_directory}")
        else:
            self.dir_label.config(text="Select a directory to clean:")

    def clean_selected_directory(self):
        if not hasattr(self, 'selected_directory') or not self.selected_directory:
            messagebox.showwarning("Warning", "No directory selected. Please select a directory to clean.")
            return

        self.clean_repo(self.selected_directory)
        messagebox.showinfo("Info", "Directory cleaning completed.")

    def clean_repo(self, repo_path):
        # Remove .git directory
        git_dir = os.path.join(repo_path, '.git')
        if os.path.exists(git_dir):
            shutil.rmtree(git_dir, onerror=self.remove_readonly)

        # Remove .gitattributes file
        gitattributes_file = os.path.join(repo_path, '.gitattributes')
        if os.path.exists(gitattributes_file):
            os.remove(gitattributes_file)

        # Remove any other Git-related files or directories
        for root, dirs, files in os.walk(repo_path):
            for name in dirs:
                if name.lower() == '.git':
                    shutil.rmtree(os.path.join(root, name), onerror=self.remove_readonly)
            for name in files:
                if name.lower() == '.gitattributes':
                    os.remove(os.path.join(root, name))

    def remove_readonly(self, func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitCleanerApp(root)
    root.mainloop()
