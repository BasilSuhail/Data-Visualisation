import os
import re
import shutil

base_dir = "/Users/basilsuhail/folders/Wolfram Resources/Introduction to Data Science"

folders = {
    "01_Course Content": [
        "Glossary-functions2026.nb",
        "Lec0.overview_of_course-2026_Jan(1).nb",
        "Lec1.Conceptual-Introduction-to-Data-Science-2026_Jan.nb",
        "Lec2.Data-Types-and-Databases-2026_Jan(1).nb",
        "Lec3.conceptual-pre-processing-data-2026_Jan(1).nb",
        "Lec4.Wolfram-DataStructure-2026_Jan(1).nb",
        "Lec5.TS-sound-audio-image-video2026_Jan.nb",
        "Lec6.datacollection-storage2026_Jan.nb",
        "Lec7.preprocessing2026_Jan(1).nb",
        "Lec8.techniques2026_Jan(1).nb",
        "Lec9.intro-machine-learning2026_Jan.nb"
    ],
    "02_Tutorials": [
        "Tutorial.Lec1-ConceptualIntroductions2026_Jan.nb",
        "Tutorial.Lec1-solutions-2026_Jan.nb",
        "Tutorial.Lec2-DataStructures-2026_Jan.nb",
        "Tutorial.Lec2-solutions-2026_Jan(1).nb",
        "Tutorial.Lec3-Pre-processing-2026_Jan.nb",
        "Tutorial.Lec4-Associations-Datasets-solutions2026_Jan.nb",
        "Tutorial.Lec4-Associations-Datasets-2026_Jan.nb",
        "Tutorial.Lec6-presidential-approval-rate-TS_2026_Jan.nb",
        "Tutorial.Lec9-ML-for-medicine-solutions-2026_Jan.nb",
        "Tutorial.Lec9-ML-for-medicine-2025b_Jan.nb"
    ],
    "03_Lectures on SQL": [
        "Lec10.RDB-Wolfram2026_Jan.nb",
        "Lec11.NRDB-Wolfram2026_Jan.nb",
        "Tutorial.Lec10-CreateMySQL-2026_Jan.nb",
        "Docker-Desktop.nb",
        "world.sql"
    ],
    "04_Data sets": [
        "UNICEF-CME_DF_2021_WQ-1.0.csv",
        "stockhighlowclose(1)(1).tsv",
        "Base_MUNIC_2021.xlsx",
        "B2020(1).csv",
        "B2025.csv"
    ],
    "05_Syntax and Wolfram Features": [
        "Functions(1)(1).nb",
        "WolframConnectivity(1)(1).nb",
        "EM-updating-values-AND-grouping-data-in-list-association-dataset(1).nb"
    ],
    "06_Assessments and Other": [
        "underfive-question-2026.nb",
        "QuestionInsurance-JAN2026.nb"
    ]
}

# Create folders
for folder in folders.keys():
    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

# Process files
moved_files = 0
for file in os.listdir(base_dir):
    full_path = os.path.join(base_dir, file)
    if os.path.isfile(full_path) and not file.startswith('.'):
        # Clean current prefixed file name (e.g. 01_Lec1.nb -> Lec1.nb, 99_Extra_world.sql -> world.sql)
        clean_name = re.sub(r'^(\d{2}_|99_Extra_)*', '', file)
        
        # Determine destination folder
        dest_folder = "06_Assessments and Other" # default fallback
        for folder_name, expected_files in folders.items():
            if clean_name in expected_files:
                dest_folder = folder_name
                break
                
        dest_path = os.path.join(base_dir, dest_folder, clean_name)
        shutil.move(full_path, dest_path)
        moved_files += 1

print(f"Successfully reorganized {moved_files} files into categorical subfolders.")
