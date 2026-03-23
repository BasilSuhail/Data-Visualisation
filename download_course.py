import os
import re
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
COURSE_URL = "https://abdn.blackboard.com/ultra/courses/_72119_1/outline"
COURSE_FOLDER_NAME = "Introduction to Data Science"
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), COURSE_FOLDER_NAME)

PAGE_TIMEOUT = 20
SCROLL_PAUSE = 1.5
DOWNLOAD_TIMEOUT = 120
MAX_RETRIES = 2

def sanitise(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    return re.sub(r"_+", "_", name)[:200]

def make_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def download_file(url: str, dest_folder: Path, session: requests.Session):
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = session.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT, allow_redirects=True)
            resp.raise_for_status()

            cd = resp.headers.get("Content-Disposition", "")
            fname = None
            if "filename*=" in cd:
                match = re.search(r"filename\*=(?:UTF-8''|utf-8'')(.+)", cd, re.IGNORECASE)
                if match: fname = unquote(match.group(1).strip().strip('"\''))
            if not fname and "filename=" in cd:
                fname = cd.split("filename=")[-1].strip().strip('"\'')
            if not fname:
                fname = unquote(urlparse(url).path.split("/")[-1]) or "file"
            fname = sanitise(fname)

            if "." not in fname:
                ct = resp.headers.get("Content-Type", "")
                ext_map = {
                    "application/pdf": ".pdf",
                    "application/vnd.openxmlformats-officedocument.presentationml": ".pptx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml": ".docx",
                    "video/mp4": ".mp4",
                    "application/zip": ".zip",
                    "text/plain": ".txt"
                }
                for prefix, ext in ext_map.items():
                    if ct.startswith(prefix):
                        fname += ext
                        break

            ct = resp.headers.get("Content-Type", "")
            if "text/html" in ct and not fname.endswith(".html"):
                return

            dest = dest_folder / fname
            if dest.exists():
                print(f"  [skip] {fname} (already exists)")
                return

            total = int(resp.headers.get("content-length", 0))
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if dest.stat().st_size < 100:
                dest.unlink()
                return

            print(f"  \u2713 {fname} ({dest.stat().st_size / 1024:.1f} KB)")
            return
        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(2)
            else:
                print(f"  \u2717 Failed: {url}\n     {e}")

def cookies_to_session(driver) -> requests.Session:
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain", ""), path=cookie.get("path", "/"))
    session.headers.update({"User-Agent": driver.execute_script("return navigator.userAgent")})
    return session

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(30):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height: break
        last_height = new_height

def is_downloadable(href: str) -> bool:
    if not href: return False
    indicators = ["bbcswebdav", "/xid-", "download", "/get/", "/retrieve/"]
    exts = [".pdf", ".mp4", ".pptx", ".ppt", ".docx", ".doc", ".xlsx", ".zip", ".py", ".ipynb", ".r", ".txt", ".csv"]
    h_lower = href.lower()
    return any(i in h_lower for i in indicators) or any(h_lower.endswith(e) or f"{e}?" in h_lower for e in exts)

def expand_all_ultra_folders(driver):
    print("  \U0001F50D Expanding Blackboard Ultra folders to reveal hidden files...")
    # Keep finding collapsed items and clicking them until none remain
    expanded_any = True
    loops = 0
    while expanded_any and loops < 10:
        expanded_any = False
        loops += 1
        try:
            # Find elements that act as folder toggles
            toggles = driver.find_elements(By.CSS_SELECTOR, "button[aria-expanded='false'], .js-course-folder-toggle")
            for t in toggles:
                try:
                    # Scroll into view and click
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", t)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", t)
                    expanded_any = True
                    time.sleep(1)
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(1.5)

def extract_file_links(driver) -> list:
    expand_all_ultra_folders(driver)
    scroll_to_bottom(driver)
    seen, links = set(), []
    for a in driver.find_elements(By.TAG_NAME, "a"):
        try:
            href = a.get_attribute("href") or ""
            if href and href not in seen and is_downloadable(href):
                seen.add(href)
                links.append(href)
        except StaleElementReferenceException: pass
    return links

def crawl_course(driver, session, course_dir):
    visited = set()
    queue = [driver.current_url]
    all_links = []
    file_count = 0

    while queue:
        url = queue.pop(0)
        if url in visited: continue
        visited.add(url)
        
        try:
            driver.get(url)
            time.sleep(3)
        except Exception: continue

        title = ""
        try:
            h1 = driver.find_element(By.CSS_SELECTOR, "h1, #pageTitleText")
            if h1.text.strip(): title = sanitise(h1.text.strip())
        except Exception: pass
        
        section_dir = course_dir
        if title and title != sanitise(course_dir.name):
            section_dir = make_dir(course_dir / title)
            print(f"  \U0001F4C1 Section: {title}")

        links = extract_file_links(driver)
        for link in links:
            if link not in all_links:
                all_links.append(link)
                download_file(link, section_dir, session)
                file_count += 1
                
        for a in driver.find_elements(By.CSS_SELECTOR, "a[href*='listContent'], a[href*='content_id']"):
            try:
                href = a.get_attribute("href") or ""
                if href and href not in visited: queue.append(href)
            except Exception: pass

    return file_count

def main():
    root = make_dir(DOWNLOAD_DIR)
    print("=" * 60)
    print(f"  DOWNLOADING COURSE: {COURSE_FOLDER_NAME}")
    print(f"  To path: {root}")
    print("=" * 60)

    opts = Options()
    opts.add_argument("--window-size=1400,900")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    try:
        driver.get("https://abdn.blackboard.com")
        print("\n\u27a1 Log in manually in Chrome.")
        input("Press Enter here once you reach the dashboard...")

        print(f"\n\u27a1 Navigating to {COURSE_URL} ...")
        driver.get(COURSE_URL)
        time.sleep(5) # Wait for initial Ultra load
        
        session = cookies_to_session(driver)
        
        count = crawl_course(driver, session, root)

        print(f"\n\U0001F389 Done! Downloaded {count} files.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
