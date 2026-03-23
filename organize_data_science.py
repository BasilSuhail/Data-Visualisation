import os
import re
import shutil

downloads_dir = "/Users/basilsuhail/folders/Wolfram Resources/Introduction to Data Science"

# 1. Flatten the directory first
for root, dirs, files in os.walk(downloads_dir):
    if root != downloads_dir:
        for file in files:
            old_p = os.path.join(root, file)
            new_p = os.path.join(downloads_dir, file)
            shutil.move(old_p, new_p)
        # remove empty dir
        try: os.rmdir(root)
        except: pass

text_data = """
Introduction to Data Science
Course Content
University of Aberdeen logo.
Review essential information about this course, such as what and how you will learn, and how we will assess what you've learned, as well as information on key education policies and other useful resources.
Glossary-functions2026.nb
Tutorial 6 - Presidential Approval Rate (for self-exercise)
Tutorial 10 - Create MySQL and integrate it with Wolfram
Docker-Desktop.nb
Online Appendix "A Hands-on Introduction...", by Shah

Adjacency matrix of a digitally reconstructed Blue Brain Project
LTI Link
Thursday, 29 January 2026 at 10:14:01
Introduction to the class Lecture 0: Introduction to the course Lecture 1: Slide 1
LTI Link
Friday, 30 January 2026 at 11:13:59
Lecture 1 (Conceptual introductions), until the end.
LTI Link
30 January 2026 at 14:08:43
Tutorial Lecture 1
LTI Link
Thursday, 5 February 2026 at 10:00:34
More on linear functions, and Lecture 2 until slide 20 "Keys, Primary keys, Foregner keys ...".
LTI Link
Friday, 6 February 2026 at 11:08:12
Lecture 2 until end, and Tutorial 2, exercise 2.
LTI Link
Friday, 6 February 2026 at 14:06:02
Tutorial lecture 2 until end, Lecture 3 until slide 13.
LTI Link
Thursday, 12 February 2026 at 10:00:00
Dummy test, discussions about test 1, Lecture 3 until end, and tutorial 3, until end
LTI Link
Friday, 13 February 2026 at 11:07:30
Lecture 4, "Wolfram Data Structure", until slide 19.
LTI Link
Friday, 13 February 2026 at 14:00:05
Lecture 4 - Wolfram Data Structure until end
LTI Link
Thursday, 19 February 2026 at 10:03:03
Tutorial Lecture 4, until slide 12, slide 11 until needs to be discussed.
LTI Link
20 February 2026 at 11:16:20
End of Tutorial lecture 4 and discussions Symbolic Keys, and Lecture 5 until slide 10
LTI Link
Friday, 20 February 2026 at 13:57:37
Lecture 5 until end, Lecture 6, until slide 16.
LTI Link
Thursday, 26 February 2026 at 10:01:44
Lecture 6, until end.
LTI Link
Friday, 27 February 2026 at 11:04:45
Lecture 7, until slide 19
LTI Link
Friday, 27 February 2026 at 14:05:33
Lecture 7 until end, Lecture 8 until slide 9.
LTI Link
Thursday, 5 March 2026 at 10:03:02
Lecture 8 until end, lecture 9 until slide 8
LTI Link
Friday, 6 March 2026 at 10:59:51
Lecture 9, until end, and Lecture 10, until slide 12 (end).
LTI Link
Friday, 6 March 2026 at 13:55:10
Tutorial Lecture 10
LTI Link
Friday, 6 March 2026 at 16:12:12
Using Docker desktop (to install and use MySQL), talk delivered and notebooks prepared by Lincoln Summerlin.
LTI Link
Lecture 11 - Mongo
In this folder you will find 5 files that can help you a lot with the Wolfram language.
Syntax

String patterns

Special characters

Pure functions

Applying transformations

Functions and Querying
Wolfram connectivity
Updating values AND grouping data in Lists, Association and Datasets
In this folder you will find details of how you will be assessed, the weighting of the assessment(s), the grading criteria, the provision of grades/feedback, the assessment due dates and submission procedures, as well as links for submitting and/or taking your assessments.
Dummy test
Due date: 22/02/2026, 22:59 (GMT)
Grading, Feedback, Extensions and Late Penalties
Information on grading and moderation procedures, provision of grades and feedback, coursework extensions and late penalties.
This item is managed by your institution.
Academic Integrity and Use of GenAI Tools
Information on academic integrity, academic misconduct and GenAI tool use for assessments.
This item is managed by your institution.
Chen-ND2025-causal-feature-ship-degradation.pdf

Project_Report__anonymous-submittted.docx

Dimitrios_Bargiotas_ID52095437_Thesis_Report.pdf

Masters_Thesis.pdf

Thesis-Qunwang_Qian-final_version.pdf

What is really warming the world?
"""

expected_items = []
lines = [l.strip() for l in text_data.split('\n') if l.strip()]

skip_phrases = ["LTI Link", "Introduction to Data Science", "Course Content", "University of Aberdeen logo", "Review essential information", "This item is managed", "In this folder you will", "Due date", "Grading, Feedback", "Information on"]
for line in lines:
    if len(line) < 5: continue
    if any(line.startswith(p) for p in skip_phrases) or "Thursday," in line or "Friday," in line or "January 2026" in line or "February 2026" in line or "March 2026" in line:
        continue
    expected_items.append({"text": line, "files_matched": []})

downloaded_files = []
for f in os.listdir(downloads_dir):
    if not f.startswith('.') and "rename" not in f and os.path.isfile(os.path.join(downloads_dir, f)):
        downloaded_files.append(f)

downloaded_files.sort()

# Match
for f in downloaded_files:
    f_lower = f.lower()
    matched = False
    
    for item in expected_items:
        text_lower = item["text"].lower()
        if f_lower in text_lower or text_lower in f_lower:
            item["files_matched"].append(f)
            matched = True
            break
            
    if matched: continue
    
    lec_match = re.search(r'(lec|lecture)0*(\d+)', f_lower.replace('_', '').replace('.', ''))
    tut_match = re.search(r'(tut|tutorial)0*(\d+)', f_lower.replace('_', '').replace('.', ''))
    
    if tut_match:
        num = tut_match.group(2)
        for item in expected_items:
            t = item["text"].lower()
            if f"tutorial {num}" in t or f"tutorial lecture {num}" in t:
                item["files_matched"].append(f)
                matched = True
                break
    elif lec_match:
        num = lec_match.group(2)
        for item in expected_items:
            t = item["text"].lower()
            if f"lecture {num}" in t or f"lec {num}" in t:
                item["files_matched"].append(f)
                matched = True
                break
                
    if not matched:
        f_clean = re.sub(r'[^a-z0-9]', ' ', f_lower).split()
        best_item = None
        best_score = 0
        for item in expected_items:
            t_clean = re.sub(r'[^a-z0-9]', ' ', item["text"].lower()).split()
            overlap = set(f_clean).intersection(set(t_clean))
            overlap = {w for w in overlap if len(w) > 3 and w not in ['2026', 'jan', 'the', 'and']}
            if len(overlap) > best_score:
                best_score = len(overlap)
                best_item = item
        if best_score > 0 and best_item:
            best_item["files_matched"].append(f)
            matched = True

missing = []
for idx, item in enumerate(expected_items):
    matches = item["files_matched"]
    if not matches:
        t = item["text"].lower()
        if ".pdf" in t or ".docx" in t or "lecture" in t or "tutorial" in t or "appendix" in t:
            missing.append(item["text"])
        elif "syntax" in t or "string patterns" in t or "pure functions" in t:
            missing.append(item["text"])

# Rename
renamed_count = 0
used_files = set()
for idx, item in enumerate(expected_items):
    for f in item["files_matched"]:
        if f in used_files: continue
        used_files.add(f)
        
        if re.match(r'^\d{2}_', f): continue
            
        new_name = f"{idx+1:02d}_{f}"
        os.rename(os.path.join(downloads_dir, f), os.path.join(downloads_dir, new_name))
        renamed_count += 1
            
for f in downloaded_files:
    if f not in used_files and not re.match(r'^\d{2}_', f):
        os.rename(os.path.join(downloads_dir, f), os.path.join(downloads_dir, f"99_Extra_{f}"))

print(f"Renamed {renamed_count} files correctly.")
print(f"Missing items: {len(missing)}")
for m in missing: print("MISSING:", m)
