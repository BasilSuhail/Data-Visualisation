import os
import re
import shutil

target_dir = "/Users/basilsuhail/folders/Wolfram Resources/blackboard_downloads/Introduction to Data Science"

# Exact hierarchy matching screenshot visually (top down order)
folder_map = {
    "01_Course Content": [
        "Glossary-functions2026.nb",
        "Lec0.overview_of_course-2026_Jan.nb",
        "Lec1.Conceptual-Introduction-to-Data-Science-2026_Jan.nb",
        "Lec2.Data-Types-and-Databases-2026_Jan.nb",
        "Lec3.conceptual-pre-processing-data-2026_Jan.nb",
        "Lec4.Wolfram-DataStructure-2026_Jan.nb",
        "Lec5.TS-sound-audio-image-video2026_Jan.nb",
        "Lec6.datacollection-storage2026_Jan.nb",
        "Lec7.preprocessing2026_Jan.nb",
        "Lec8.techniques2026_Jan.nb",
        "Lec9.intro-machine-learning2026_Jan.nb"
    ],
    "02_Tutorials": [
        "Tutorial.Lec10-CreateMySQL-2026_Jan.nb",
        "Docker-Desktop.nb",
        "Tutorial.Lec6-presidential-approval-rate-TS_2026_Jan.nb",
        "Online_Appendix_Aug_2020.docx",
        "OA1.2.xlsx",
        "connectivity matrix table 1.csv",
        "Tutorial.Lec1-ConceptualIntroductions2026_Jan.nb",
        "Tutorial.Lec1-solutions-2026_Jan.nb",
        "Tutorial.Lec2-DataStructures-2026_Jan.nb",
        "Tutorial.Lec2-solutions-2026_Jan.nb",
        "Tutorial.Lec3-Pre-processing-2026_Jan.nb",
        "Tutorial.Lec4-Associations-Datasets-solutions2026_Jan.nb",
        "Tutorial.Lec4-Associations-Datasets-2026_Jan.nb",
        "Tutorial.Lec9-ML-for-medicine-solutions-2026_Jan.nb",
        "Tutorial.Lec9-ML-for-medicine-2025b_Jan.nb"
    ],
    "03_Recordings of Blackboard Collaborate sessions": [
    ],
    "04_Lectures on SQL": [
        "Lec10.RDB-Wolfram2026_Jan.nb",
        "Lec11.NRDB-Wolfram2026_Jan.nb",
        "world.sql"
    ],
    "05_Syntax, string patterns, special characters, pure functions and applying transformations": [
        "Syntax.pdf",
        "StringPatterns.pdf",
        "Special Characters—Wolfram Language Documentation.pdf",
        "Pure Functions—Wolfram Language Documentation.pdf",
        "Applying Transformation Rules—Wolfram Language Documentation.pdf",
        "Functions.nb",
        "WolframConnectivity.nb",
        "EM-updating-values-AND-grouping-data-in-list-association-dataset.nb"
    ],
    "06_Assessments and Grading": [
        "underfive-question-2026.nb",
        "QuestionInsurance-JAN2026.nb"
    ],
    "07_Data sets": [
        "Aircraft_Incident_Dataset.csv",
        "B2020.csv",
        "B2025.csv",
        "Base_MUNIC_2021.xlsx",
        "Base_MUNIC_2021_MERGED.xlsx",
        "breamData.csv",
        "cci30_OHLCV.csv",
        "Chapter2-OA2.1.xlsx",
        "Chapter2_Exercise1.csv",
        "chicagotemps.csv",
        "coneccoes.txt",
        "housing.csv",
        "madagascar raw data.xlsx",
        "Popularity of Programming Languages from 2004 to 2024.csv",
        "RenewablesGrowth.xls",
        "RenewablesGrowth.xlsx",
        "stockdata.csv",
        "stockhighlowclose.tsv",
        "table_1_14_a.xlsx",
        "test1.xlsx",
        "test12.xlsx",
        "test.xlsx",
        "UNICEF-CME_DF_2021_WQ-1.0.csv",
        "vix-daily_csv.csv"
    ],
    "08_Examples of thesis": [
        "Chen-ND2025-causal-feature-ship-degradation.pdf",
        "Project_Report__anonymous-submittted.docx",
        "Dimitrios_Bargiotas_ID52095437_Thesis_Report.pdf",
        "Masters_Thesis.pdf",
        "Thesis-Qunwang_Qian-final_version.pdf",
        "whats_really_warming_the_World.pdf",
        "whats_really_warming_the-World.pdf"
    ]
}

all_files = {}
for root, dirs, files in os.walk(target_dir):
    for f in files:
        if f.startswith('.'): continue
        pure_name = re.sub(r'^\d{2}_', '', f) # Strip numbering
        pure_name = re.sub(r'\(1\)', '', pure_name) # Strip (1)
        all_files[pure_name] = os.path.join(root, f)

for folder in folder_map.keys():
    os.makedirs(os.path.join(target_dir, folder), exist_ok=True)

moved_count = 0
not_found = []

for idx_f, (folder, expected_files) in enumerate(folder_map.items()):
    for idx_item, expected_file in enumerate(expected_files):
        clean_expected = expected_file.replace("(1)", "")
        
        actual_path = all_files.get(clean_expected)
        if not actual_path:
            found = False
            for k, p in all_files.items():
                if clean_expected.lower().replace("-","").replace("_","") in k.lower().replace("-","").replace("_",""):
                    actual_path = p
                    found = True
                    break
            if not found:
                not_found.append(expected_file)
                continue
                
        new_name = f"{idx_item+1:02d}_{clean_expected}"
        new_path = os.path.join(target_dir, folder, new_name)
        
        if actual_path != new_path:
            shutil.move(actual_path, new_path)
            # Update key reference
            for k, p in list(all_files.items()):
                if p == actual_path: all_files[k] = new_path
        moved_count += 1

# Cleanup
for root, dirs, files in os.walk(target_dir, topdown=False):
    for d in dirs:
        dir_path = os.path.join(root, d)
        if not re.match(r'^0\d_', d): 
            try: os.rmdir(dir_path)
            except OSError: pass

print(f"Successfully organized {moved_count} files via strict visual mapping.")
if not_found:
    print("Missing (Not found in downloaded stack):")
    for f in not_found: print(f" - {f}")
