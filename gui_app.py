import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from threading import Thread
from operations.sort_by_date import organize_by_date
from operations.duplicate_finder import find_duplicates
from operations.separate_media import separate_photos_videos
from operations.organize_documents import organize_documents
from operations.sort_by_size import sort_by_size

# --- GUI App ---
class MediaOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📦 Media Organizer")
        self.root.geometry("650x450")

        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="📂 Source Folder").pack(pady=(10, 0))
        tk.Entry(self.root, textvariable=self.source_folder, width=60).pack()
        tk.Button(self.root, text="Browse", command=self.browse_source).pack(pady=(0, 10))

        tk.Label(self.root, text="📁 Destination Folder").pack()
        tk.Entry(self.root, textvariable=self.dest_folder, width=60).pack()
        tk.Button(self.root, text="Browse", command=self.browse_dest).pack(pady=(0, 10))

        # Buttons for operations
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="📅 Sort by Date", width=18, command=lambda: self.run_task(organize_by_date)).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="🧾 Find Duplicates", width=18, command=lambda: self.run_task(find_duplicates)).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="🖼️ Separate Media", width=18, command=lambda: self.run_task(separate_photos_videos)).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="📑 Organize Docs", width=18, command=lambda: self.run_task(organize_documents)).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="📏 Sort by Size", width=18, command=lambda: self.run_task(sort_by_size)).grid(row=2, column=0, padx=5, pady=5)

        # Console Output Box
        tk.Label(self.root, text="📜 Output Log:").pack()
        self.output_box = scrolledtext.ScrolledText(self.root, height=10, width=80)
        self.output_box.pack(pady=5)

    def browse_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_folder.set(folder)

    def run_task(self, task_func):
        src = self.source_folder.get().strip('"')
        dst = self.dest_folder.get().strip('"')

        if not src or not dst:
            messagebox.showerror("Missing Paths", "Please select both source and destination folders.")
            return

        def task():
            self.output_box.insert(tk.END, f"🔄 Running {task_func.__name__}...\n")
            self.output_box.see(tk.END)
            try:
                task_func(src, dst)
                self.output_box.insert(tk.END, f"✅ Done: {task_func.__name__}\n\n")
            except Exception as e:
                self.output_box.insert(tk.END, f"❌ Error: {e}\n\n")

            self.output_box.see(tk.END)

        Thread(target=task).start()


# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = MediaOrganizerApp(root)
    root.mainloop()
