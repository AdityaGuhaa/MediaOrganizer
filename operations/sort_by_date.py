from utils.helpers import is_image, is_video, get_exif_date, get_video_date, safe_copy
import os
import datetime
from tqdm import tqdm

def organize_by_date(source_folder, output_folder):
    print(f"\n📂 Organizing from {source_folder}")
    all_files = []
    stats = {
        "processed": 0,
        "skipped": 0,
        "skipped_files": [],
        "total_bytes": 0
    }

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
            except Exception as e:
                stats["skipped"] += 1
                stats["skipped_files"].append((file_path, f"Failed to get date: {e}"))
                continue

        year = str(date_taken.year)
        month = f"{date_taken.strftime('%m')}-{date_taken.strftime('%B')}"
        day = f"{date_taken.strftime('%d')}-{date_taken.strftime('%A')}"
        dest_dir = os.path.join(output_folder, year, month, day)

        try:
            safe_copy(file_path, dest_dir)
            stats["processed"] += 1
            stats["total_bytes"] += os.path.getsize(file_path)
        except Exception as e:
            stats["skipped"] += 1
            stats["skipped_files"].append((file_path, f"Copy failed: {e}"))

    # Save summary logs
    summary_path = os.path.join(output_folder, "summary.log")
    skipped_path = os.path.join(output_folder, "skipped_files.log")

    with open(summary_path, "w", encoding="utf-8") as s:
        s.write(f"✅ Total files processed: {stats['processed']}\n")
        s.write(f"📦 Total size moved: {round(stats['total_bytes'] / (1024 * 1024), 2)} MB\n")
        s.write(f"❌ Total files skipped: {stats['skipped']}\n")

    if stats["skipped_files"]:
        with open(skipped_path, "w", encoding="utf-8") as skip_log:
            for path, reason in stats["skipped_files"]:
                skip_log.write(f"{path} - {reason}\n")

    print(f"\n📋 Summary:")
    print(f"✅ Files processed: {stats['processed']}")
    print(f"📦 Total size moved: {round(stats['total_bytes'] / (1024 * 1024), 2)} MB")
    print(f"❌ Skipped files: {stats['skipped']}")
    print(f"📝 Summary saved to: {summary_path}")
