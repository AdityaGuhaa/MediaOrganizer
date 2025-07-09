from PIL import Image
from PIL.ExifTags import TAGS
import datetime
import os

def extract_image_metadata(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if not exif_data:
            return None

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal':
                return datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception:
        return None
    return None

def extract_metadata(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png']:
        return extract_image_metadata(file_path)
    else:
        return None
