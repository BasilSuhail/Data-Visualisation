import os
import re
import shutil

src_dir = "/Users/basilsuhail/folders/Wolfram Resources/blackboard_downloads/Introduction to Data Science"
dst_dir = "/Users/basilsuhail/folders/Wolfram Resources/Introduction to Data Science"

folders = {
    "01_Course Content": [],
    "02_Tutorials": [],
    "03_Lectures on SQL": [],
    "04_Syntax, string patterns, special characters, pure functions and applying transformations": [],
    "05_Assessments and Grading": [],
    "06_Data sets": [],
    "07_Examples of thesis": [],
    "08_Extra material": []
}

# Naturally sort helper
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# 1. Collect and Map files
for root, dirs, files in os.walk(src_dir):
    for filename in files:
        if filename.startswith('.'): continue
            
        full_path = os.path.join(root, filename)
        path_lower = full_path.lower()
        file_lower = filename.lower()
        
        target = "08_Extra material"
        
        if "lecture notebooks" in path_lower:
            if "lecture 10" in path_lower or "lecture 11" in path_lower or "docker" in file_lower or "world.sql" in file_lower:
                target = "03_Lectures on SQL"
            else:
                target = "01_Course Content"
                
        elif "practicals_tutorials" in path_lower or "tutorial" in file_lower:
            if "tutorial 10" in path_lower or "lecture 10" in path_lower:
                target = "03_Lectures on SQL"
            else:
                target = "02_Tutorials"
                
        elif "datasets" in path_lower:
            target = "06_Data sets"
            
        elif "syntax" in path_lower:
            target = "04_Syntax, string patterns, special characters, pure functions and applying transformations"
            
        elif "assessment" in path_lower:
            target = "05_Assessments and Grading"
            
        elif "articles and thesis" in path_lower or "thesis" in file_lower or "report" in file_lower:
            target = "07_Examples of thesis"
            
        else:
            # Fallbacks based on filenames if folders missed
            if "docker" in file_lower or "world.sql" in file_lower:
                target = "03_Lectures on SQL"
            elif "tutorial" in file_lower:
                target = "02_Tutorials"
            elif "lec" in file_lower:
                target = "01_Course Content"
                
        folders[target].append((full_path, filename))

# 2. Create destination and move
if os.path.exists(dst_dir):
    shutil.rmtree(dst_dir)
os.makedirs(dst_dir, exist_ok=True)

for folder_name, items in folders.items():
    if not items: continue
    
    folder_path = os.path.join(dst_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # Sort files naturally so Lec1 is before Lec10
    sorted_items = sorted(items, key=lambda x: natural_sort_key(x[1]))
    
    # Optional: Put Glossary first in Course Content
    if folder_name == "01_Course Content":
        glossary = [x for x in sorted_items if "glossary" in x[1].lower()]
        others = [x for x in sorted_items if "glossary" not in x[1].lower()]
        sorted_items = glossary + others
        
    for idx, (old_path, filename) in enumerate(sorted_items):
        # Clean any existing numeric prefix the file might inherently have to avoid 01_01_Lec.nb
        clean_name = re.sub(r'^\d{2}_', '', filename)
        new_name = f"{idx+1:02d}_{clean_name}"
        new_path = os.path.join(folder_path, new_name)
        
        shutil.copy2(old_path, new_path)
        print(f"[{folder_name}] {filename} -> {new_name}")

print("\nSuccessfully organized all files as requested.")
