# Wolfram Resources

Course materials and tools for MSc Data Science at the University of Aberdeen.

## Contents

- **blackboard_downloader.py** — Automated Blackboard Ultra course content downloader
- **blackboard_downloads/** — Downloaded course materials organized by module

### Introduction to Programming (PX5007)

| Module | Contents |
|--------|----------|
| Module 1: Introduction | Wolfram notebooks, transcripts, datasets |
| Module 2: Syntax and Evaluation | Lecture notebooks, datasets |
| Programming in the Wolfram Language | Notebooks, scribbles |
| Visualisation and Interactivity | Notebooks, transcripts |
| Maths and Statistics | Notebooks, data files |
| Getting Data and Exploratory Analysis | Notebooks |
| Curve Fitting | Notebooks |
| Wednesday Workshop | Notebooks, presentations |

## Downloader Usage

```bash
pip install selenium requests tqdm webdriver-manager
python blackboard_downloader.py --url "<course_url>" --name "<folder_name>" --skip-login
```

## Requirements

- Python 3.10+
- Google Chrome
- Selenium, requests, tqdm, webdriver-manager
