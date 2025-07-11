from utils.helpers import is_image, is_video, safe_copy
import os
from tqdm import tqdm

def separate_photos_videos(source_folder, dest_folder):
    print(f"\n🎞️ Separating media from {source_folder}")
    all_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            all_files.append(os.path.join(root, file))

    for file_path in tqdm(all_files, desc="Separating"):
        file = os.path.basename(file_path)

        if is_image(file):
            safe_copy(file_path, os.path.join(dest_folder, "Photos"))
        elif is_video(file):
            safe_copy(file_path, os.path.join(dest_folder, "Videos"))
