import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
import datetime
import cv2

# --- Helpers ---

def is_image(file):
    return file.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.webp', '.tiff', '.bmp'))

def is_video(file):
    return file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.3gp', '.wmv'))

def safe_copy(src, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    filename = os.path.basename(src)
    dest = os.path.join(dest_folder, filename)
    
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest):
        dest = os.path.join(dest_folder, f"{base}_{counter}{ext}")
        counter += 1

    shutil.copy2(src, dest)

def get_exif_date(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag)
                if tag_name == 'DateTimeOriginal':
                    return datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None

def get_video_date(file_path):
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.datetime.fromtimestamp(timestamp)
    except Exception:
        return None
