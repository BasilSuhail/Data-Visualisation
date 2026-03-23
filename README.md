# 🎓 Blackboard Course Downloader & Organizer

A collection of Python scripts to automate downloading, organizing, and cleaning up course materials from the University of Aberdeen's MyAberdeen (Blackboard) portal.

Specifically, this repository contains tools to bypass the tedious manual downloading of lectures, tutorials, problem sheets, and multimedia assets, organizing them logically for effective studying.

---

## 🛠 Features

1. **Interactive SSO Downloader (`download_course.py`)**
   - Headful Chrome automation allows you to log in via your university's Microsoft SSO (which typically blocks headless scrapers).
   - Capable of expanding Blackboard Ultra folders and crawling deeply nested content.
   - Automatically attempts to infer missing extensions (`.pdf`, `.mp4`, `.zip`, `.nb`) from HTTP headers.

2. **Automated Folder Ordering (`reorganize_data_science.py` & `rename_dv_files.py`)**
   - Cleanly maps messy Blackboard outputs into visually structured layout exactly matching real course modules.
   - Files are sorted smoothly into respective subfolders.

3. **Content Verification (`organize_data_science.py` & `verify_user_list.py`)**
   - Parses text/PDFs of course syllabi and matches them against downloaded files via heuristic matching to output thorough Missing File Reports.

---

## 📂 Current Course Structures

The following courses have their materials structurally aligned with the official chronological syllabus:

### 1. Introduction to Programming
```text
01_PX5007 (2025-26)_ Introduction to Programming/
02_Welcome to the Degree/
03_Welcome in different languages/
04_Welcome MSc.mp4
05_Module 1 _ Introduction/
06_Module 2_ Syntax and Evaluation/
07_Programming in the Wolfram Language/
08_Visualisation and Interactivity/
09_Maths And Statistics/
10_Getting Data and Exploratory Analysis/
11_Curve fitting/
12_Laura's Wolfram Support/
13_Timothy's Computer Corner/
14_Ethics/
15_Wednesday Workshop/
```

### 2. Data Visualisation
In Data Visualisation, the files themselves are prefixed by their `Lecture X` or `Answers X` numeric order so they align perfectly alongside their problem sheets (Exams ignored):
```text
01_Notebooks/
 ├── 01_Lecture1(1).nb
 ├── 03_Lecture3.nb
 ├── ...
 └── 10_Lecture10.nb

02_Notebooks_Problem sheets/
 ├── 01_Answers1.nb
 ├── ...
 └── 10_Lecture10-Answers.nb
```

### 3. Introduction to Data Science
Files are grouped into structured subfolders perfectly matching the Blackboard Ultra layout sections:
```text
01_Course Content/
 ├── Lec0 ...
 ├── Lec1 ...
 └── Lec9 ...

02_Tutorials/
 ├── Tutorial.Lec1 ...
 └── Tutorial.Lec9 ...

03_Lectures on SQL/
 ├── Docker-Desktop.nb
 ├── Lec10.RDB-Wolfram ...
 └── world.sql

04_Data sets/
 ├── Base_MUNIC_2021.xlsx
 └── UNICEF-CME...csv

05_Syntax and Wolfram Features/
 ├── EM-updating-values-AND-grouping...nb
 └── Functions(1)(1).nb

06_Assessments and Other/
 └── Extra files...
```

---

## 🚀 Usage

### 1. Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install selenium requests tqdm webdriver-manager pypdf pymupdf
```

### 2. Run the Downloader
Execute the main script. Chrome will open for you to log in physically. Navigate to a course page, return to terminal, and hit enter to crawl.
```bash
python download_course.py
```
