from utils.helpers import safe_copy
import os
from tqdm import tqdm

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
    for file_path in tqdm(all_files, desc="Organizing"):
        file = os.path.basename(file_path)
        ext = os.path.splitext(file)[1].lower()

        for category, extensions in doc_map.items():
            if ext in extensions:
                dest_dir = os.path.join(dest_folder, category)
                try:
                    safe_copy(file_path, dest_dir)
                except Exception as e:
                    print(f"❌ Failed to copy {file}: {e}")
                break
