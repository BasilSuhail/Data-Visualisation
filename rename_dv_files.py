import os
import re

base_dir = "/Users/basilsuhail/folders/Wolfram Resources/blackboard_downloads/Data Visualisation"
folders_to_process = ["Notebooks", "Notebooks_Problem sheets"]

# Rename files in the folders
for folder in folders_to_process:
    folder_path = os.path.join(base_dir, folder)
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.startswith('.'):
                continue
                
            # Find the primary number in the filename to use as sort key
            # e.g. "Lecture10" -> 10, "Answers1" -> 1
            match = re.search(r'\d+', filename)
            if match:
                num = int(match.group())
                # Only prepend if it doesn't already have one
                if not re.match(r'^\d{2}_', filename):
                    new_name = f"{num:02d}_{filename}"
                    old_path = os.path.join(folder_path, filename)
                    new_path = os.path.join(folder_path, new_name)
                    os.rename(old_path, new_path)
                    print(f"Renamed: '{filename}' -> '{new_name}'")

# Rename the main folders to put them at the top
renames = {
    "Notebooks": "01_Notebooks",
    "Notebooks_Problem sheets": "02_Notebooks_Problem sheets"
}

for old_name, new_name in renames.items():
    old_path = os.path.join(base_dir, old_name)
    new_path = os.path.join(base_dir, new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"Renamed folder: '{old_name}' -> '{new_name}'")

print("\nDone organizing Data Visualisation files!")
