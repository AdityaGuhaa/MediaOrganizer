import os
from tqdm import tqdm
from utils.helpers import safe_copy

def get_size_category(size_bytes):
    if size_bytes < 100 * 1024 * 1024:
        return "Below_100MB"
    elif size_bytes < 300 * 1024 * 1024:
        return "100–300MB"
    elif size_bytes < 500 * 1024 * 1024:
        return "300–500MB"
    elif size_bytes < 1024 * 1024 * 1024:
        return "500MB–1GB"
    elif size_bytes < 2 * 1024 * 1024 * 1024:
        return "1–2GB"
    elif size_bytes < 5 * 1024 * 1024 * 1024:
        return "2–5GB"
    else:
        return "5GB+"

def sort_by_size(source_folder, dest_folder):
    print(f"\n📏 Sorting by file size in: {source_folder}")
    all_files = []

    for root, _, files in os.walk(source_folder):
        for file in files:
            all_files.append(os.path.join(root, file))

    for file_path in tqdm(all_files, desc="Sorting by size"):
        try:
            size = os.path.getsize(file_path)
            category = get_size_category(size)
            size_folder = os.path.join(dest_folder, category)
            safe_copy(file_path, size_folder)
        except Exception as e:
            print(f"❌ Failed to process {file_path}: {e}")
