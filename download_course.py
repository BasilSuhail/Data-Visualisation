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

def set_headers(session, driver):
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain", ""), path=cookie.get("path", "/"))
    session.headers.update({"User-Agent": driver.execute_script("return navigator.userAgent")})

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
                ext_map = {"application/pdf": ".pdf", "application/vnd.openxmlformats-officedocument.presentationml": ".pptx", "application/vnd.openxmlformats-officedocument.wordprocessingml": ".docx", "video/mp4": ".mp4", "application/zip": ".zip", "text/plain": ".txt"}
                for prefix, ext in ext_map.items():
                    if ct.startswith(prefix):
                        fname += ext
                        break

            # Skip HTML
            ct = resp.headers.get("Content-Type", "")
            if "text/html" in ct and not fname.endswith(".html"):
                return

            dest = dest_folder / fname
            
            # recursive un-prefixing: if the dest already exists under any prefix, don't download
            existing_files = [f for root, dirs, files in os.walk(DOWNLOAD_DIR) for f in files]
            clean_existing = [re.sub(r'^(\d{2}_|Extra_)*', '', ef) for ef in existing_files]
            if fname in existing_files or fname in clean_existing:
                print(f"  [skip] {fname} (Already downloaded during previous run)")
                return

            if dest.exists():
                print(f"  [skip] {fname} (Already exists)")
                return

            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if dest.stat().st_size < 100:
                dest.unlink()
                return

            print(f"  \u2713 NEW FILE DOWNLOADED: {fname} ({dest.stat().st_size / 1024:.1f} KB)")
            return
        except Exception as e:
            if attempt < MAX_RETRIES: time.sleep(2)

def is_downloadable(href: str) -> bool:
    if not href: return False
    indicators = ["bbcswebdav", "/xid-", "download", "/get/", "/retrieve/", "LaunchLTI", "Panopto"]
    exts = [".pdf", ".mp4", ".pptx", ".docx", ".xlsx", ".zip", ".nb", ".csv", ".tsv", ".sql"]
    h_lower = href.lower()
    return any(i in h_lower for i in indicators) or any(h_lower.endswith(e) or f"{e}?" in h_lower for e in exts)

def extract_file_links(driver) -> list:
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
    file_count = 0
    
    # In Ultra, deep folders can have links inside them when expanded.
    # We will expand everything
    for _ in range(3):
        try:
            toggles = driver.find_elements(By.CSS_SELECTOR, "button[aria-expanded='false'], .js-course-folder-toggle")
            for t in toggles:
                try: 
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", t)
                    time.sleep(1)
                except: pass
        except: pass

    # Also extract all links from any iframes
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        try:
            driver.switch_to.frame(iframe)
            links = extract_file_links(driver)
            for link in links:
                download_file(link, course_dir, session)
                file_count += 1
            driver.switch_to.default_content()
        except: driver.switch_to.default_content()

    links = extract_file_links(driver)
    for link in links:
        download_file(link, course_dir, session)
        file_count += 1

    return file_count

def main():
    root = make_dir(DOWNLOAD_DIR)
    
    opts = Options()
    opts.add_argument("--window-size=1400,900")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    try:
        driver.get("https://abdn.blackboard.com")
        print("➡ Please log in.")
        input("Press Enter once on the dashboard...")

        print(f"➡ Navigating to {COURSE_URL} ...")
        driver.get(COURSE_URL)
        print("➡ Expand any folders that you specifically want to ensure are downloaded (like 'Files for final project')")
        input("Press Enter here when you are ready to let the scraper crawl the open page...")
        
        session = requests.Session()
        set_headers(session, driver)
        
        count = crawl_course(driver, session, root)
        print(f"\n🎉 Done! Found and downloaded {count} files.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
