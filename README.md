# 🎓 Blackboard Course Downloader & Organizer

A collection of Python scripts to automate downloading, organizing, and cleaning up course materials from the University of Aberdeen's MyAberdeen (Blackboard) portal.

Specifically, this repository contains tools to bypass the tedious manual downloading of lectures, tutorials, problem sheets, and multimedia assets, organizing them logically for effective studying.

---

## 🛠 Features

1. **Interactive SSO Downloader (`blackboard_downloader.py`)**
   - Headful Chrome automation allows you to log in via your university's Microsoft SSO (which typically blocks headless scrapers).
   - Prompts you to navigate to any course, then scrapes and downloads all deep-linked files, subpages, embedded Panopto/Welcome videos, and attachments.
   - Automatically attempts to infer missing extensions (`.pdf`, `.mp4`, `.zip`, `.nb`) from HTTP headers.
   - Organizes downloaded contents into a neat `/blackboard_downloads` subfolder named after the course.
   - Includes resume capability (skips already downloaded files).

2. **Automated Folder Ordering (`rename_dv_files.py` & `rename_folders.py`)**
   - Automatically cleans up and sequentially numbers the downloaded folders/files based on actual course chronologies (like `01_...`, `02_...`).
   - Ensures files sort cleanly in your OS Explorer or Finder.

3. **Content Verification (`verify_user_list.py` & `compare_downloads.py`)**
   - Parses text/PDFs of course syllabi and checks them against physically downloaded files (via fuzzy matching) to produce an accurate missing files report.

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
 ├── 01_Problems1.nb
 ├── ...
 └── 10_Lecture10-Answers.nb
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
python blackboard_downloader.py
```

### 3. Verification
If you have a syllabus list, edit `text_data` in `verify_user_list.py` and run it to ensure no files were left behind by Blackboard's lazy-loading UI.
```bash
python verify_user_list.py
```
