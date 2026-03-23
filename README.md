# Wolfram Resources

University of Aberdeen course materials downloaded from MyAberdeen (Blackboard Ultra).

## Course Structure

```
blackboard_downloads/
|
|-- Introduction to Programming/
|   |-- 01_PX5007 (2025-26)_ Introduction to Programming/
|   |-- 02_Welcome to the Degree/
|   |-- 05_Module 1 _ Introduction/
|   |-- 06_Module 2_ Syntax and Evaluation/
|   |-- 07_Programming in the Wolfram Language/
|   |-- 08_Visualisation and Interactivity/
|   |-- 09_Maths And Statistics/
|   |-- 10_Getting Data and Exploratory Analysis/
|   |-- 11_Curve fitting/
|   |-- 12_Laura's Wolfram Support/
|   |-- 13_Timothy's Computer Corner/
|   |-- 14_Ethics/
|   |-- 15_Wednesday Workshop/
|
|-- Data Visualisation/
|   |-- 01_Notebooks/           (Lecture1-10 .nb files)
|   |-- 02_Notebooks_Problem sheets/  (Answers + Problems .nb files)
|   |-- Exam 1/
|   |-- Exam 2/
|
|-- Introduction to Data Science/
|   |-- 01_Course Content/      (Lec0-Lec9 .nb notebooks)
|   |-- 02_Tutorials/           (Tutorial notebooks + solutions)
|   |-- 04_Lectures on SQL/     (Lec10-11 .nb + world.sql)
|   |-- 05_Syntax, string patterns, special characters.../  (PDFs + .nb)
|   |-- 06_Assessments and Grading/
|   |-- 07_Data sets/           (CSV, XLSX, TSV, SQL, TXT)
|   |-- 08_Examples of thesis/  (PDFs + docx)
|
|-- Machine Learning/
|   |-- Lectures/               (Ch0-Ch9 .nb notebooks, .ipynb, .pptx)
|   |-- Practicals/             (Questions + Answers .nb files)
|   |-- Data/                   (Campylobacter dataset .csv)
|   |-- Additional materials - Papers, etc./  (PDFs)
|   |-- Course Guide/           (Timetable)
```

## How to Download From Blackboard

### 1. Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install selenium requests tqdm webdriver-manager
```

### 2. The API Approach

The downloader uses Blackboard's REST API with a Selenium session for authentication. Here's how it works:

**Step 1** - Copy your Chrome profile and launch Selenium so you can log in via SSO:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json, time, os, re, requests

opts = Options()
opts.add_argument("--user-data-dir=/path/to/temp/chrome/profile")
driver = webdriver.Chrome(options=opts)

# Navigate to the course - log in when the browser opens
driver.get("https://abdn.blackboard.com/ultra/courses/_72119_1/outline")
# Wait until you're on the course page
```

**Step 2** - Use the REST API to map all content:

```python
COURSE_ID = "_72119_1"
BASE = "https://abdn.blackboard.com"

def get_api(path):
    driver.get(f"{BASE}{path}")
    time.sleep(2)
    return json.loads(driver.find_element(By.TAG_NAME, "body").text)

# Get top-level sections
top = get_api(f"/learn/api/public/v1/courses/{COURSE_ID}/contents?limit=200")

# Get children of each section
for item in top["results"]:
    if item.get("hasChildren"):
        children = get_api(f"/learn/api/public/v1/courses/{COURSE_ID}/contents/{item['id']}/children?limit=200")
```

**Step 3** - Download files via the attachments API:

```python
cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

for item in all_items:
    att_data = get_api(f"/learn/api/public/v1/courses/{COURSE_ID}/contents/{item['id']}/attachments")
    for att in att_data.get("results", []):
        url = f"{BASE}/learn/api/public/v1/courses/{COURSE_ID}/contents/{item['id']}/attachments/{att['id']}/download"
        resp = requests.get(url, cookies=cookies, stream=True)
        with open(att["fileName"], "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
```

### 3. Key API Endpoints

| Endpoint | Returns |
|---|---|
| `/learn/api/public/v1/courses/{COURSE_ID}/contents?limit=200` | Top-level sections |
| `/learn/api/public/v1/courses/{COURSE_ID}/contents/{id}/children?limit=200` | Items inside a section |
| `/learn/api/public/v1/courses/{COURSE_ID}/contents/{id}/attachments` | Downloadable files for an item |
| `/learn/api/public/v1/courses/{COURSE_ID}/contents/{id}/attachments/{att_id}/download` | File download |

### 4. Notes

- `COURSE_ID` is in the Blackboard URL: `ultra/courses/_72119_1/outline` -> `_72119_1`
- Selenium is only needed for SSO login - the actual downloads use `requests` with the session cookies
- Skip items with handler `resource/x-bb-blti-link` (lecture recordings / Panopto)
- Skip `.mp4` files if you only want documents and datasets
- GitHub rejects files over 100MB - split large datasets with `split -b 95m` if needed
