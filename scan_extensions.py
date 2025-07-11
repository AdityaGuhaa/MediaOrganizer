import os
from collections import Counter

folder = r"D:\Airbnb Data"  # ⬅️ Replace with your actual input folder
ext_counter = Counter()

for root, _, files in os.walk(folder):
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        ext_counter[ext] += 1

print("📊 File extension counts:")
for ext, count in ext_counter.most_common():
    print(f"{ext}: {count}")
