import os
import shutil
import sqlite3
from datetime import datetime
from utils.metadata_extractor import extract_metadata
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

MEDIA_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.mp4', '.mov')
DB_PATH = "db/media.db"

def sanitize_filename(filename):
    for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        filename = filename.replace(ch, '')
    return filename[:240]  # Prevent overly long filenames

def organize_file(file_path, date_taken, media_root):
    try:
        year = str(date_taken.year)
        month = f"{date_taken.month:02d}-{date_taken.strftime('%B')}"
        dest_folder = os.path.join(media_root, year, month)
        os.makedirs(dest_folder, exist_ok=True)

        filename = sanitize_filename(os.path.basename(file_path))
        dest_path = os.path.join(dest_folder, filename)

        shutil.copy2(file_path, dest_path)
        return dest_path

    except Exception as e:
        print(f"❌ Error copying '{file_path}': {e}")
        with open("skipped_files.log", "a", encoding="utf-8") as log:
            log.write(f"{file_path} => {e}\n")
        return None

def process_media(folder_path, media_root):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    processed = 0
    skipped = 0

    for root, _, files in os.walk(folder_path):
        for file in tqdm(files, desc=f"Processing in {root}"):
            if not file.lower().endswith(MEDIA_EXTENSIONS):
                continue

            file_path = os.path.join(root, file)
            date_taken = extract_metadata(file_path)

            if not date_taken:
                date_taken = datetime.fromtimestamp(os.path.getmtime(file_path))

            new_path = organize_file(file_path, date_taken, media_root)
            if new_path is None:
                skipped += 1
                continue

            cursor.execute("""
                INSERT INTO media (filename, filepath, media_type, date_taken)
                VALUES (?, ?, ?, ?)
            """, (
                file,
                new_path,
                "video" if file.lower().endswith(('.mp4', '.mov')) else "image",
                date_taken.strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            processed += 1

    conn.close()

    print("\n✅ All media files processed.")
    print(f"✔️ Total processed: {processed}")
    print(f"⚠️ Total skipped: {skipped}")
    if skipped > 0:
        print("📝 See skipped_files.log for details.")
    input("\n🔚 Press Enter to exit...")

if __name__ == "__main__":
    print("\n📂 MEDIA ORGANIZER v1.0 - By Aditya Guha\n")
    media_root = input("📥 Enter the destination folder to save organized media: ").strip('"')
    folder_path = input("📁 Enter the source folder containing media files: ").strip('"')

    if not os.path.isdir(folder_path):
        print("❌ Invalid source folder path.")
    elif not os.path.isdir(media_root):
        print("❌ Invalid destination folder path.")
    else:
        process_media(folder_path, media_root)
