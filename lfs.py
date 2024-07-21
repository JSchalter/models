import os
import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
import shutil
import stat

class GitLFSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Git LFS Clone and Pull Tool")
        self.working_directory = ""
        self.clone_links = []

        self.setup_ui()

    def setup_ui(self):
        # Directory Selection
        self.dir_label = tk.Label(self.root, text="Working Directory: Not Selected")
        self.dir_label.pack(pady=5)

        self.select_dir_btn = tk.Button(self.root, text="Select Working Directory", command=self.select_directory)
        self.select_dir_btn.pack(pady=5)

        # Clone Links Input
        self.add_link_btn = tk.Button(self.root, text="Add Git Clone Link", command=self.add_clone_link)
        self.add_link_btn.pack(pady=5)

        # Upload Links File
        self.upload_file_btn = tk.Button(self.root, text="Upload Links File", command=self.upload_links_file)
        self.upload_file_btn.pack(pady=5)

        # Repositories List
        self.repo_frame = tk.Frame(self.root)
        self.repo_frame.pack(pady=5)

        self.repo_label = tk.Label(self.repo_frame, text="Cloned Repositories:")
        self.repo_label.pack()

        self.repo_listbox = tk.Listbox(self.repo_frame, selectmode=tk.MULTIPLE)
        self.repo_listbox.pack(pady=5)

        # Git LFS Pull Button
        self.pull_lfs_btn = tk.Button(self.root, text="Pull LFS for Selected", command=self.pull_lfs)
        self.pull_lfs_btn.pack(pady=5)

    def select_directory(self):
        self.working_directory = filedialog.askdirectory()
        if self.working_directory:
            self.dir_label.config(text=f"Working Directory: {self.working_directory}")
            self.update_repo_list()

    def add_clone_link(self):
        while True:
            link = simpledialog.askstring("Input", "Enter git clone link (or Cancel to stop):")
            if not link:
                break
            self.clone_links.append(link)

        if self.clone_links:
            self.clone_repositories()

    def upload_links_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("GIT_LFS_SKIP_SMUDGE=1 git clone"):
                        link = line.split()[-1]
                    else:
                        link = line
                    if link:
                        self.clone_links.append(link)
            self.clone_repositories()

    def clone_repositories(self):
        target_dir = filedialog.askdirectory(title="Select Root Location for Cloning")
        if not target_dir:
            return

        env = os.environ.copy()
        env["GIT_LFS_SKIP_SMUDGE"] = "1"

        for link in self.clone_links:
            repo_name = os.path.basename(link).replace(".git", "")
            clone_path = os.path.join(target_dir, repo_name)
            try:
                subprocess.run(['git', 'clone', link, clone_path], check=True, env=env)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to clone {link}:\n{e}")
        
        self.update_repo_list()

    def update_repo_list(self):
        self.repo_listbox.delete(0, tk.END)
        if self.working_directory:
            for item in os.listdir(self.working_directory):
                item_path = os.path.join(self.working_directory, item)
                if os.path.isdir(item_path):
                    self.repo_listbox.insert(tk.END, item)

    def pull_lfs(self):
        selected_repos = [self.repo_listbox.get(i) for i in self.repo_listbox.curselection()]
        if not selected_repos:
            messagebox.showwarning("Warning", "No repositories selected for LFS pull.")
            return
        
        for repo in selected_repos:
            repo_path = os.path.join(self.working_directory, repo)
            try:
                subprocess.run(['git', '-C', repo_path, 'lfs', 'pull'], check=True)
                self.clean_repo(repo_path)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to pull LFS for {repo}:\n{e}")
        
        messagebox.showinfo("Info", "Git LFS pull and repository cleaning completed for selected repositories.")

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
    app = GitLFSApp(root)
    root.mainloop()
