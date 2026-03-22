import os
import shutil

base_dir = "/Users/basilsuhail/folders/Wolfram Resources/blackboard_downloads/Introduction to Programming"

# Define the mapping from old names to new ordered names
renames = {
    "PX5007 (2025-26)_ Introduction to Programming": "01_PX5007 (2025-26)_ Introduction to Programming",
    "Welcome to the Degree": "02_Welcome to the Degree",
    "Welcome in different languages": "03_Welcome in different languages",
    "Welcome MSc.mp4": "04_Welcome MSc.mp4",
    "Module 1 _ Introduction": "05_Module 1 _ Introduction",
    "Module 2_ Syntax and Evaluation": "06_Module 2_ Syntax and Evaluation",
    "Programming in the Wolfram Language": "07_Programming in the Wolfram Language",
    "Visualisation and Interactivity": "08_Visualisation and Interactivity",
    "Maths And Statistics": "09_Maths And Statistics",
    "Getting Data and Exploratory Analysis": "10_Getting Data and Exploratory Analysis",
    "Curve fitting": "11_Curve fitting",
    "Laura's Wolfram Support": "12_Laura's Wolfram Support",
    "Timothy's Computer Corner": "13_Timothy's Computer Corner",
    "Ethics": "14_Ethics",
    "Wednesday Workshop": "15_Wednesday Workshop"
}

# Iterate over items in the directory and rename based on the map
for old_name, new_name in renames.items():
    old_path = os.path.join(base_dir, old_name)
    new_path = os.path.join(base_dir, new_name)
    
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"Renamed: '{old_name}' -> '{new_name}'")
    else:
        print(f"Warning: '{old_name}' not found!")

print("\nDone organizing folders!")
