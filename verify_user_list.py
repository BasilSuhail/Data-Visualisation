import os
import re

text_data = """
PX5007 (2025-26): Introduction to Programming
Course Content
Welcome to MSc
A short welcome video by Marco's digital Avatar.
This folder contains the welcome message in various languages.
Welcome MSc (Mandarin)
Welcome MSc (Finnish)
Welcome MSc (Spanish)
Welcome MSc (Arabic)
Welcome MSc (Cantonese)
Welcome MSc (Urdu)
Welcome MSc (Bulgarian)
Welcome MSc (Swahili)
Welcome MSc (Tamil)
Introduction: Laura (virtual teaching assistant; tutorials and programming problems)
Introduction: Timothy (virtual teaching assistant; technology, setup, etc)
University of Aberdeen logo.
Review essential information about this course, such as what and how you will learn, and how we will assess what you've learned, as well as information on key education policies and other useful resources.
Course Essentials
Essential information such as the course team, intended learning outcomes, teaching methods, assessment, attendance and engagement requirements.
Course Schedule
Overview of the course schedule, including topics being covered and staff teaching that topic.
Education Policies, Guidance, Useful Resources
Link to absence reporting tool, policy on extensions and penalties, information on academic integrity, policies on appeals and complaints and links to support services.
This item is managed by your institution.
MySkills
Details of the skills you will have the opportunity to develop, as well as the skills assessed in this course.
Sustainable Development Goals (SDGs)
Details of the content that contributes to the United Nations' Sustainable Development Goals.
This is a short course (approx 6 hours) of Mathematica. You can use it to revise or as a sneak peak of what is coming up.
Intro to Mathematica - Part 1
Intro to Mathematica - Part 2
Intro to Mathematica - Part 3
This transcript captures a university professor's introductory lecture for a Master's in Data Science program. The lecture covers course logistics, including fire safety procedures and available math support. A significant portion focuses on the transformative impact of generative AI and large language models on the field of data science, discussing both the opportunities and challenges presented by these rapidly evolving technologies. The professor demonstrates the capabilities of AI tools in real-time, emphasizing the need for students to adapt and utilize these tools effectively.
MScDataScienceWelcome -Sep 2025
Lecture 22.9.2025 (am)
Transcript 22.9.2025 (am)
Podcast 22.9.2025.mp4
Vodcast 22.9.2025.mp4
I robot clip
This lecture introduces the Wolfram language, emphasizing a hands-on, interactive learning approach. The instructor demonstrates the language's capabilities, showcasing its ability to handle diverse data types (images, text, geographic data) and integrate with other programming languages like Python. Key features highlighted include natural language input, automated code generation, and the seamless integration of large language models. The lecture promotes efficiency and problem-solving, encouraging students to utilize the tool's features to tackle complex tasks quickly. The overall goal is to equip students with practical skills for data science and real-world applications.
15 of 23 started

LLMs - What Has Changed
LLM for Research
Lecture 23.9.25 (part 1)
Transcript 23.9.25 (part 1)
Podcast 23.9.25 (part 1)
Vodcast 23.9.25 (part 1)
Lecture 23.9.25 (part 2)
Transcript 23.9.25 (part 2).txt
Podcast 23.9.25 (part 2)
Vodcast 23.9.25 (part 2)
Lecture 1a - Introduction to DATA science - Sep 2025
Lecture 1b - What makes the Wolfram Language Special - Sep 2025
Lecture 29.9.2025 (am)
Transcript 29.9.2025 (am)
Podcast 29.9.2025 (am)
Vodcast 29.9.2025 (am)
Lecture 30.9.2025
Transcript 30.9.2025
Podcast 30.9.2025
Vodcast 30.9.2025
Lecture 1c - Aspects of the Wolfram Language - Sep 2025
Lecture 1d - The notebook environment - Sep 2025
DataDir.zip
This module provides a foundational understanding of the syntax and evaluation mechanisms in the Wolfram Language. It covers the structure of expressions, including their head and argument syntax, the use of square brackets, and the importance of capitalisation. Students learn how to define variables and functions and explore different types of expressions, such as numbers, symbols, and lists. The module also introduces key programming constructs, including function definitions (both named and pure functions), list manipulation techniques, and options handling. Students gain hands-on experience with working with structured data using lists, matrices, and associations, as well as practical applications like importing and exporting data.
2 of 6 started

Lecture 02 - Syntax and Evaluation
Lecture 7.10.2025 (pm)
Transcript 7.10.2025
Podcast lecture 7.10.2025
Vodcast 7.10.2025
dataset.txt
This module introduces key programming paradigms in the Wolfram Language, including procedural, functional, and rule-based programming. It covers control structures such as loops and conditionals, the use of pattern matching, and recursive function definitions. Functional programming concepts like `Map`, `Fold`, and `Nest` are explored alongside anonymous functions and list manipulation techniques. Additionally, the module discusses parallel computing and GPU-based acceleration for efficient computation. By the end, students will have a solid foundation in writing efficient, structured Wolfram Language code.
5 of 9 started

04 ProgrammingWithTheWolframLanguage - Sep 2025
Lecture 14.10.2025 (pm)
Vodcast 14.10.25
Scribbles 2- 14.10.25.nb
Scribbles_14.10.2025.nb
Lecture 20.10.25
Transcript 20.10.25
Podcast 20.10.25
Vodcast 20.10.25
Introduction to Programming in the Wolfram Language, explores how to create, customise, and interact with graphical and dynamic content in Mathematica. It begins with the syntax for basic 2D and 3D plotting functions such as Plot, ParametricPlot, and Plot3D, and progresses to advanced data visualisation tools including ListPlot, ListPlot3D, and DateListPlot for temporal data. Students learn domain-specific visualisation functions—such as VectorPlot, BodePlot, and WaveletScalogram—and statistical tools like Histogram, BoxWhiskerChart, and DistributionChart for analysing distributions. The lecture also introduces graph visualisation, and demonstrates how to customise aesthetics via PlotTheme, PlotStyle, legends, and frames.
4 of 5 started

Visualization And Interactivity
Lecture 21.10.25
Transcript 21.10.25
Podcast 21.10.25
Vodcast 21.10.25
1 of 2 started

Math And Statistics
DataDir
2 of 3 started

Getting And Organizing The Data
Lecture 28.10.25
DataInvestigations
1 of 1 started

Curve Fitting
In this folder you will find details of how you will be assessed, the weighting of the assessment(s), the grading criteria, the provision of grades/feedback, the assessment due dates and submission procedures, as well as links for submitting and/or taking your assessments.
LTI Link
Reading List
Access to your reading list on Leganto, which provides links to digital resources such as e-books, journal articles, and physical books available in the Library.
Ask your Course Team
Have you got a query about the course or assessments? Post it here! Please remember to review the information provided in the Course Guide and the Assessment folder, as many common queries, such as assessment details and due dates, are already answered there. Staff will endeavour to respond to your query within 1-3 working days. Please note Staff will not respond to course or assessment queries via email or direct messages . Email should only be used for confidential or personal matters. All posts, whether anonymous or not, must be professional and respectful, and should follow expected standards of online etiquette . If a post goes against these expectations, we may need to take formal steps to ensure we keep this a helpful and ...
In this area Laura will discuss programming problems and other academic issues. CAREFUL: THIS IS AI GENERATED CONTENT.
Academic Misconduct
Academic Integrity Student Guide August 2022.pdf

MSc Data Science Resources and Opportunities
Wolfram Language Programming Sections 1 & 2 (some examples)
Mock Exam
No due date
Formative
This is a mock exam for the course. You only have 10 questions (as opposed to the 20 questions in the full exam). I do not guarantee that the mock exam is equally difficult to a full exam. It is to learn how the system works. Do not necessarily take it as an indication of the level of difficulty of the real exam. I have allowed you unlimited attempts and there is no time limit on the mock exam. Like for the full exam you will need the latest version of the Wolfram Language to work on the questions. In the full exam you have 2 hours for 20 questions. These 10 questions should take no longer than about 1 hour.
Summary Lecture 1 b
Logistic Modelling and Curve Fitting
In this area Timothy will give instructions on technical issues, such as how to install Wolfram on your computer. CAREFUL: THIS IS AI GENERATED CONTENT.
Installing Wolfram (Mathematica) with a University of Aberdeen License
Installing Wolfram (Mathematica) with University of Aberdeen License (pptx)

Installing Ollama and Local LLMs A Guide for Data Science Students
Accessing Online AI Models A Complete Guide
Running Local AI Models with LM Studio
How to Install Gemini CLI
Essential_Tools_and_Techniques for MSc Data Science Students
Ethics Lecture- Ben Martin
Homework - Elementary Introduction to the Wolfram Language
No due date
Formative
This is the submission area for your current Wolfram notebook with solutions to the problems in the book "Elementary Introduction to the Wolfram Language": https://www.wolfram.com/language/elementary-introduction/3rd-ed/ Every weekday starting 22. September you should do 4 sections from the book and upload the (total) notebook with all new and previous problems.
Frequently asked Questions
ModellingTheory-Temperature
workshop_guide.pdf

AI-Powered_Development_From_Terminal_to_IoT.pptx
"""

downloads_dir = "blackboard_downloads"

# Find lines that are likely files or resources
expected_items = []
indicator_words = ["welcome", "intro", "transcript", "podcast", "vodcast", "lecture", "data", "scribbles", "install", "guide", ".mp4", ".pdf", ".txt", ".zip", ".nb", ".pptx", "clip", "model", "tools"]
ignore_phrases = ["this is", "overview", "link to", "details of", "short course", "this lecture", "the instructor", "the module", "in this folder", "have you got", "this is a submission"]

lines = [l.strip() for l in text_data.split('\n') if l.strip()]
for line in lines:
    if line.lower() in [i.lower() for i in ignore_phrases] or any(line.lower().startswith(i.lower()) for i in ignore_phrases):
        continue
    if len(line.split()) > 15: # Too long to be a filename
        continue
    if " of " in line and "started" in line: # e.g. 15 of 23 started
        continue
    
    # Check if looks like file
    is_file = False
    if any(line.lower().endswith(ext) for ext in [".mp4", ".pdf", ".txt", ".zip", ".nb", ".pptx", ".m4a"]):
        is_file = True
    elif any(word in line.lower() for word in indicator_words):
        is_file = True
        
    if is_file:
        expected_items.append(line)

# Collect downloaded files
downloaded_files = []
for root, dirs, files in os.walk(downloads_dir):
    for file in files:
        if not file.startswith('.'):
            downloaded_files.append((file.lower(), file))

missing = []

for expected in expected_items:
    found = False
    expected_clean = re.sub(r'[\\/*?:"<>|]', "", expected).lower()
    expected_clean = re.sub(r'[^a-zA-Z0-9 ]', '', expected_clean).strip()
    
    # Look for partial matches 
    for dl_lower, dl_orig in downloaded_files:
        dl_clean = re.sub(r'[\\/*?:"<>|]', "", dl_lower).lower()
        dl_clean = os.path.splitext(dl_clean)[0]
        dl_clean = re.sub(r'[^a-zA-Z0-9 ]', '', dl_clean).strip()
        
        # If words intersect significantly or it's a substring
        if expected_clean in dl_clean or dl_clean in expected_clean:
            # We assume "found" if one is a substring of another
            if len(expected_clean) > 5 and len(dl_clean) > 5:
                found = True
                break
                
        # Token overlap check for loose matches
        exp_tokens = set(expected_clean.split())
        dl_tokens = set(dl_clean.split())
        if exp_tokens and dl_tokens:
            overlap = exp_tokens.intersection(dl_tokens)
            if len(overlap) >= max(len(exp_tokens)-1, 2): # mostly lines up
                 found = True
                 break

    if not found:
        missing.append(expected)

print("--- Missing Check ---")
if not missing:
    print("All identifiable expected files appear to be downloaded!")
else:
    for m in missing:
        print(f"MISSING: {m}")
