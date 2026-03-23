import os
import re
import shutil

target_dir = "/Users/basilsuhail/folders/Wolfram Resources/blackboard_downloads/Introduction to Data Science"

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

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# 1. Collect all files in the directory recursively
all_files = []
for root, sorted_dirs, files in os.walk(target_dir):
    for filename in files:
        if filename.startswith('.'): continue
        all_files.append((os.path.join(root, filename), filename))

# 2. Map files to folders
for full_path, filename in all_files:
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
        if "docker" in file_lower or "world.sql" in file_lower:
            target = "03_Lectures on SQL"
        elif "tutorial" in file_lower:
            target = "02_Tutorials"
        elif "lec" in file_lower:
            target = "01_Course Content"
            
    folders[target].append((full_path, filename))

# Move special ones
def move_special(items_list, filename_matcher, new_target):
    for idx, (p, f) in enumerate(items_list):
        if filename_matcher in f.lower():
            folders[new_target].append((p, f))
            items_list.pop(idx)
            return

move_special(folders["02_Tutorials"], "docker", "03_Lectures on SQL")
move_special(folders["08_Extra material"], "em-updating", "04_Syntax, string patterns, special characters, pure functions and applying transformations")
move_special(folders["08_Extra material"], "functions.nb", "04_Syntax, string patterns, special characters, pure functions and applying transformations")
move_special(folders["08_Extra material"], "wolframconnectivity", "04_Syntax, string patterns, special characters, pure functions and applying transformations")


# 3. Create the top level folders
for f_name in folders.keys():
    os.makedirs(os.path.join(target_dir, f_name), exist_ok=True)

# 4. Move files to the root level folders
for folder_name, items in folders.items():
    if not items: continue
    
    folder_path = os.path.join(target_dir, folder_name)
    sorted_items = sorted(items, key=lambda x: natural_sort_key(x[1]))
    
    if folder_name == "01_Course Content":
        glossary = [x for x in sorted_items if "glossary" in x[1].lower()]
        others = [x for x in sorted_items if "glossary" not in x[1].lower()]
        sorted_items = glossary + others
        
    for idx, (old_path, filename) in enumerate(sorted_items):
        clean_name = re.sub(r'^\d{2}_', '', filename)
        new_name = f"{idx+1:02d}_{clean_name}"
        new_path = os.path.join(folder_path, new_name)
        
        # Don't overwrite if it's literally the same exact path
        if old_path != new_path:
            shutil.move(old_path, new_path)

# 5. Clean up old empty subfolders like "Lecture notebooks", etc.
for root, dirs, files in os.walk(target_dir, topdown=False):
    for d in dirs:
        dir_path = os.path.join(root, d)
        if not re.match(r'^0\d_', d): # don't delete our numbered folders
            try:
                os.rmdir(dir_path)
            except OSError:
                pass # not empty
