from utils.helpers import is_image, is_video, safe_copy
import os
import hashlib
from tqdm import tqdm

def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def find_duplicates(source_folder, dest_folder):
    print(f"\n🔍 Scanning for duplicates in {source_folder}")
    hash_dict = {}
    duplicates = []

    for root, _, files in os.walk(source_folder):
        for file in files:
            if is_image(file) or is_video(file):
                path = os.path.join(root, file)
                file_hash = get_file_hash(path)
                if file_hash:
                    if file_hash in hash_dict:
                        duplicates.append((path, hash_dict[file_hash]))
                    else:
                        hash_dict[file_hash] = path

    if not duplicates:
        print("✅ No duplicates found.")
        return

    print(f"\n✅ Found {len(duplicates)} duplicate file(s).")
    os.makedirs(dest_folder, exist_ok=True)

    for dup, _ in tqdm(duplicates, desc="Copying duplicates"):
        try:
            safe_copy(dup, dest_folder)
        except Exception as e:
            print(f"❌ Failed to copy {dup}: {e}")
