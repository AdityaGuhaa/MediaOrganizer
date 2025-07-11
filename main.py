import os
import shutil
import hashlib
import datetime
import subprocess
from tqdm import tqdm
from PIL import Image
from PIL.ExifTags import TAGS

# --------------------------------------
# Utility Functions
# --------------------------------------

def is_image(file):
    return file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.heic'))

def is_video(file):
    return file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.3gp'))

def is_document(file):
    return file.lower().endswith((
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.txt', '.csv', '.odt', '.ods', '.odp'
    ))

def get_exif_date(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data is not None:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal':
                    return datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None

def get_video_date(file_path):
    try:
        command = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_entries', 'format_tags=creation_time',
            file_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        import json
        data = json.loads(result.stdout)
        date_str = data.get('format', {}).get('tags', {}).get('creation_time', '')
        if date_str:
            return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except Exception:
        pass
    return None

def safe_copy(src, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    base = os.path.basename(src)
    dest = os.path.join(dest_dir, base)
    count = 1
    while os.path.exists(dest):
        name, ext = os.path.splitext(base)
        dest = os.path.join(dest_dir, f"{name}_{count}{ext}")
        count += 1
    shutil.copy2(src, dest)

# --------------------------------------
# Option 1: Organize by Date
# --------------------------------------

def organize_by_date(source_folder, output_folder):
    print(f"\n📂 Organizing from {source_folder}")
    all_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            all_files.append(os.path.join(root, file))

    for file_path in tqdm(all_files, desc="Organizing"):
        file = os.path.basename(file_path)

        # Get creation date
        date_taken = None
        if is_image(file):
            date_taken = get_exif_date(file_path)
        elif is_video(file):
            date_taken = get_video_date(file_path)

        if date_taken is None:
            try:
                date_taken = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            except Exception:
                continue

        # Organize into Year/Month
        year = str(date_taken.year)
        month = f"{date_taken.strftime('%m')}-{date_taken.strftime('%B')}"
        dest_dir = os.path.join(output_folder, year, month)
        safe_copy(file_path, dest_dir)

# --------------------------------------
# Option 2: Find Duplicate Images & Videos
# --------------------------------------

def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def find_duplicates(source_folder):
    print(f"\n🔍 Scanning for duplicates in {source_folder}")
    hash_dict = {}
    duplicates = []

    for root, _, files in os.walk(source_folder):
        for file in tqdm(files, desc=f"Scanning in {root}"):
            file_path = os.path.join(root, file)
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov')):
                file_hash = get_file_hash(file_path)
                if file_hash:
                    if file_hash in hash_dict:
                        duplicates.append((file_path, hash_dict[file_hash]))
                    else:
                        hash_dict[file_hash] = file_path

    if not duplicates:
        print("✅ No duplicates found.")
        return

    print(f"\n✅ Found {len(duplicates)} duplicate file(s):")
    dest_folder = input("📥 Enter folder to copy duplicate files into: ").strip('"')
    os.makedirs(dest_folder, exist_ok=True)

    for dup, original in duplicates:
        print(f"🟨 Duplicate: {dup}")
        print(f"   Original: {original}")
        try:
            safe_copy(dup, dest_folder)
        except Exception as e:
            print(f"❌ Failed to copy {dup}: {e}")


# --------------------------------------
# Option 3: Separate Images and Videos
# --------------------------------------

def separate_media(source_folder, dest_folder):
    image_folder = os.path.join(dest_folder, 'Photos')
    video_folder = os.path.join(dest_folder, 'Videos')
    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(video_folder, exist_ok=True)

    image_count = 0
    video_count = 0
    skipped = 0

    all_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            all_files.append(os.path.join(root, file))

    print(f"\nSorting in {source_folder}:")
    for file_path in tqdm(all_files):
        file = os.path.basename(file_path)
        try:
            if is_image(file):
                shutil.copy2(file_path, os.path.join(image_folder, file))
                image_count += 1
            elif is_video(file):
                shutil.copy2(file_path, os.path.join(video_folder, file))
                video_count += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"❌ Failed to copy: {file_path} — {e}")
            skipped += 1

    print(f"\n📷 Images copied: {image_count}")
    print(f"🎞️  Videos copied: {video_count}")
    print(f"🚫 Files skipped: {skipped}")

# --------------------------------------
# Option 4: Organize Document Files
# --------------------------------------

def organize_documents(source_folder, dest_folder):
    doc_map = {
        'PDF': ['.pdf'],
        'Word': ['.doc', '.docx', '.odt'],
        'Excel': ['.xls', '.xlsx', '.ods'],
        'PowerPoint': ['.ppt', '.pptx', '.odp'],
        'Text': ['.txt', '.csv']
    }

    all_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            all_files.append(os.path.join(root, file))

    print(f"\n📑 Organizing documents in {source_folder}:")
    count = 0
    for file_path in tqdm(all_files):
        file = os.path.basename(file_path)
        ext = os.path.splitext(file)[1].lower()

        for category, extensions in doc_map.items():
            if ext in extensions:
                dest_dir = os.path.join(dest_folder, category)
                try:
                    safe_copy(file_path, dest_dir)
                    count += 1
                except Exception as e:
                    print(f"❌ Failed to copy {file}: {e}")
                break

    print(f"\n✅ Documents sorted: {count}")

# --------------------------------------
# Main Menu
# --------------------------------------

def main():
    while True:
        print("\n📂 MEDIA ORGANIZER MENU")
        print("1. Organize by Date (Photos/Videos)")
        print("2. Find Duplicate Images")
        print("3. Separate Photos and Videos")
        print("4. Organize Document Files")
        print("5. Exit")

        option = input("\nChoose an option (1–5): ").strip()

        if option == "1":
            source = input("📁 Enter source folder: ").strip('"')
            dest = input("📥 Enter destination folder: ").strip('"')
            organize_by_date(source, dest)

        elif option == "2":
            source = input("📁 Enter folder to check for duplicates: ").strip('"')
            find_duplicates(source)

        elif option == "3":
            source = input("📁 Enter source media folder path: ").strip('"')
            dest = input("📥 Enter destination folder path: ").strip('"')
            separate_media(source, dest)

        elif option == "4":
            source = input("📁 Enter source folder with documents: ").strip('"')
            dest = input("📥 Enter destination folder to save organized documents: ").strip('"')
            organize_documents(source, dest)


        elif option == "5":
            print("👋 Exiting. Goodbye!")
            break

        else:
            print("⚠️ Invalid option. Try again.")

# --------------------------------------
# Entry Point
# --------------------------------------

if __name__ == "__main__":
    main()
