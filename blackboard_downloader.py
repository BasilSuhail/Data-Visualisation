"""
Blackboard Course Content Downloader
University of Aberdeen MyAberdeen Portal

Interactive mode: opens Chrome for manual SSO login, then you navigate to
each course page and press Enter to trigger the crawl + download.

Requirements:
    pip install selenium requests tqdm webdriver-manager

Usage:
    python blackboard_downloader.py
"""

import os
import re
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin, unquote
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from webdriver_manager.chrome import ChromeDriverManager


# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

BLACKBOARD_URL = "https://myaberdeen.abdn.ac.uk"
DOWNLOAD_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blackboard_downloads")

# Direct mode: set via command-line args --url and --name
DIRECT_URL  = None
DIRECT_NAME = None
SKIP_LOGIN  = False

# File extensions to download (None = grab everything)
WANTED_EXTENSIONS = None
# Example to restrict: WANTED_EXTENSIONS = {".pdf", ".mp4", ".pptx", ".docx", ".xlsx", ".zip", ".py", ".ipynb", ".r", ".csv", ".txt"}

PAGE_TIMEOUT     = 20
SCROLL_PAUSE     = 1.5
DOWNLOAD_TIMEOUT = 120
MAX_RETRIES      = 2


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════

def sanitise(name: str) -> str:
    """Make a string safe for folder/file names."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    name = re.sub(r"_+", "_", name)
    return name[:200]  # cap length for OS limits


def make_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def download_file(url: str, dest_folder: Path, session: requests.Session):
    """Download a single file into dest_folder with a progress bar."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = session.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT, allow_redirects=True)
            resp.raise_for_status()

            # Determine filename from Content-Disposition header or URL
            cd = resp.headers.get("Content-Disposition", "")
            fname = None
            if "filename*=" in cd:
                # RFC 5987 encoded filename
                match = re.search(r"filename\*=(?:UTF-8''|utf-8'')(.+)", cd, re.IGNORECASE)
                if match:
                    fname = unquote(match.group(1).strip().strip('"\''))
            if not fname and "filename=" in cd:
                fname = cd.split("filename=")[-1].strip().strip('"\'')
            if not fname:
                path_part = urlparse(url).path
                fname = unquote(path_part.split("/")[-1]) or "file"
            fname = sanitise(fname)

            # If no extension, try to infer from content type
            if "." not in fname:
                ct = resp.headers.get("Content-Type", "")
                ext_map = {
                    "application/pdf": ".pdf",
                    "application/vnd.openxmlformats-officedocument.presentationml": ".pptx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml": ".docx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml": ".xlsx",
                    "application/zip": ".zip",
                    "video/mp4": ".mp4",
                    "text/plain": ".txt",
                    "text/html": ".html",
                    "image/png": ".png",
                    "image/jpeg": ".jpg",
                }
                for content_prefix, ext in ext_map.items():
                    if ct.startswith(content_prefix):
                        fname += ext
                        break

            # Filter by wanted extensions
            if WANTED_EXTENSIONS:
                ext = Path(fname).suffix.lower()
                if ext not in WANTED_EXTENSIONS:
                    return

            # Skip HTML pages masquerading as downloads
            ct = resp.headers.get("Content-Type", "")
            if "text/html" in ct and not fname.endswith(".html"):
                return

            dest = dest_folder / fname
            if dest.exists():
                print(f"  [skip] {fname} (already exists)")
                return

            total = int(resp.headers.get("content-length", 0))
            with open(dest, "wb") as f, tqdm(
                desc=fname[:55],
                total=total if total > 0 else None,
                unit="B",
                unit_scale=True,
                leave=False,
            ) as bar:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))

            # Remove empty/tiny files that are likely error pages
            if dest.stat().st_size < 100:
                dest.unlink()
                return

            print(f"  \u2713  {fname} ({dest.stat().st_size / 1024:.1f} KB)")
            return

        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"  [retry {attempt+1}] {fname if 'fname' in dir() else url} ... {e}")
                time.sleep(2)
            else:
                print(f"  \u2717  Failed: {url}\n     {e}")


def cookies_to_session(driver) -> requests.Session:
    """Copy Selenium cookies into a requests Session for file downloads."""
    session = requests.Session()
    cookies = driver.get_cookies() or []
    for cookie in cookies:
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain", ""),
            path=cookie.get("path", "/"),
        )
    session.headers.update({
        "User-Agent": driver.execute_script("return navigator.userAgent"),
    })
    return session


# ══════════════════════════════════════════════
#  BROWSER SETUP
# ══════════════════════════════════════════════

def create_driver(use_profile: bool = False) -> webdriver.Chrome:
    opts = Options()
    # Visible mode so user can log in via SSO
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    if use_profile:
        # Copy Chrome profile to a temp dir so we can use it while Chrome is open
        import shutil, tempfile
        src_profile = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        tmp_profile = os.path.join(tempfile.gettempdir(), "bb_chrome_profile")
        if os.path.exists(tmp_profile):
            shutil.rmtree(tmp_profile, ignore_errors=True)
        os.makedirs(tmp_profile, exist_ok=True)
        # Copy only essential files for session cookies
        for item in ["Default"]:
            src = os.path.join(src_profile, item)
            dst = os.path.join(tmp_profile, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                    "Cache", "Code Cache", "GPUCache", "Service Worker",
                    "File System", "blob_storage", "IndexedDB", "Local Storage",
                    "Session Storage", "*.log", "GCM Store",
                ), dirs_exist_ok=True)
        # Copy Local State file
        local_state = os.path.join(src_profile, "Local State")
        if os.path.exists(local_state):
            shutil.copy2(local_state, os.path.join(tmp_profile, "Local State"))
        opts.add_argument(f"--user-data-dir={tmp_profile}")
        opts.add_argument("--profile-directory=Default")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


# ══════════════════════════════════════════════
#  CONTENT CRAWLING
# ══════════════════════════════════════════════

def scroll_to_bottom(driver):
    """Scroll the page fully so lazy loaded items appear."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(30):  # safety cap
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def is_downloadable_link(href: str) -> bool:
    """Check if a URL looks like it points to downloadable content."""
    if not href:
        return False
    download_indicators = [
        "bbcswebdav",
        "/xid-",
        "@X@",
        "courses/1/",
        "/get/",
        "/retrieve/",
        "downloadFile",
        "downloadDocument",
        "downloadAssignment",
    ]
    file_extensions = [
        ".pdf", ".mp4", ".pptx", ".ppt", ".docx", ".doc",
        ".xlsx", ".xls", ".zip", ".rar", ".7z",
        ".py", ".ipynb", ".r", ".rmd",
        ".csv", ".txt", ".json", ".xml",
        ".png", ".jpg", ".jpeg", ".gif", ".svg",
        ".mp3", ".wav", ".avi", ".mov", ".wmv",
        ".sav", ".sps",  # SPSS files
        ".m", ".mat",    # MATLAB files
    ]
    href_lower = href.lower()
    for indicator in download_indicators:
        if indicator.lower() in href_lower:
            return True
    for ext in file_extensions:
        if href_lower.endswith(ext) or f"{ext}?" in href_lower:
            return True
    return False


def is_content_page_link(href: str) -> bool:
    """Check if a URL leads to another Blackboard content page to recurse into."""
    if not href:
        return False
    content_indicators = [
        "listContent",
        "content_id",
        "listContentEditable",
        "content_handler",
    ]
    return any(ind in href for ind in content_indicators)


def extract_file_links(driver) -> list:
    """Find all downloadable file links on the current page."""
    scroll_to_bottom(driver)
    seen = set()
    links = []

    for a in driver.find_elements(By.TAG_NAME, "a"):
        try:
            href = a.get_attribute("href") or ""
        except StaleElementReferenceException:
            continue
        if not href or href in seen:
            continue
        seen.add(href)
        if is_downloadable_link(href):
            links.append(href)

    return links


def extract_subpage_links(driver) -> list:
    """Find links to content subpages for recursive crawling."""
    links = []
    seen = set()

    selectors = [
        "a[href*='listContent']",
        "a[href*='content_id']",
        "a[href*='listContentEditable']",
    ]

    for selector in selectors:
        try:
            for a in driver.find_elements(By.CSS_SELECTOR, selector):
                try:
                    href = a.get_attribute("href") or ""
                except StaleElementReferenceException:
                    continue
                if href and href not in seen and is_content_page_link(href):
                    seen.add(href)
                    links.append(href)
        except Exception:
            continue

    return links


def get_page_title(driver) -> str:
    """Try to extract a meaningful page/section title."""
    try:
        # Blackboard Classic breadcrumb
        crumbs = driver.find_elements(By.CSS_SELECTOR, "#breadcrumbs span, .path span")
        if crumbs:
            return sanitise(crumbs[-1].text.strip())
    except Exception:
        pass
    try:
        h1 = driver.find_element(By.CSS_SELECTOR, "h1, #pageTitleText")
        if h1.text.strip():
            return sanitise(h1.text.strip())
    except Exception:
        pass
    return ""


def crawl_course(driver, session: requests.Session, course_dir: Path):
    """Crawl the current course page and all its sub pages, downloading everything."""
    current_url = driver.current_url

    # Detect if this is Blackboard Ultra
    if "/ultra/" in current_url:
        return crawl_course_ultra(driver, session, course_dir)
    else:
        return crawl_course_classic(driver, session, course_dir)


def crawl_course_ultra(driver, session: requests.Session, course_dir: Path):
    """Crawl a Blackboard Ultra course by expanding sections and following file links."""
    file_count = 0
    downloaded_urls = set()
    import re as _re

    print(f"\n  Crawling course content (Ultra mode)...")

    outline_url = driver.current_url

    def load_all_content(drv):
        """Scroll inner content container and click ALL 'Load more' buttons."""
        for attempt in range(30):
            # Scroll the inner scrollable container (not the page body)
            drv.execute_script("""
                var containers = document.querySelectorAll("*");
                for (var i = 0; i < containers.length; i++) {
                    var el = containers[i];
                    var style = window.getComputedStyle(el);
                    if ((style.overflowY === "auto" || style.overflowY === "scroll") &&
                        el.scrollHeight > el.clientHeight && el.clientHeight > 300) {
                        el.scrollTop = el.scrollHeight;
                        break;
                    }
                }
            """)
            time.sleep(2)
            try:
                load_btns = drv.find_elements(By.XPATH,
                    "//button[contains(text(),'Load') and contains(text(),'more')]")
                # Filter out "No more content" buttons
                clickable = [b for b in load_btns
                             if b.is_displayed() and "No more" not in b.text]
                if clickable:
                    drv.execute_script("arguments[0].click();", clickable[0])
                    print(f"     Loaded more content items (round {attempt+1})...")
                    time.sleep(3)
                else:
                    break
            except Exception:
                break
        # Scroll back to top
        drv.execute_script("""
            window.scrollTo(0, 0);
            var containers = document.querySelectorAll("*");
            for (var i = 0; i < containers.length; i++) {
                var el = containers[i];
                var style = window.getComputedStyle(el);
                if ((style.overflowY === "auto" || style.overflowY === "scroll") &&
                    el.scrollHeight > el.clientHeight && el.clientHeight > 300) {
                    el.scrollTop = 0;
                    break;
                }
            }
        """)
        time.sleep(1)

    # Step 1: Load ALL content items on the page
    print("  Loading all content sections...")
    load_all_content(driver)

    # Step 2: Collect section names — look for ALL clickable content sections
    # In Ultra, sections are buttons but also <a> links and other clickable elements
    section_names = []
    skip_labels = ["Status for", "More options", "Search", "Download Alternative",
                   "Course Coordinators", "Details & Actions"]
    skip_texts = ["Courses", "Help for current page", "OPEN",
                   "No more content items to load"]

    # Scroll through the entire page to collect all buttons
    page_height = driver.execute_script("return document.body.scrollHeight")
    scroll_pos = 0
    while scroll_pos < page_height:
        driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
        time.sleep(0.5)
        scroll_pos += 500

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    for btn in driver.find_elements(By.CSS_SELECTOR, "button"):
        try:
            text = btn.text.strip()
            aria = btn.get_attribute("aria-label") or ""
            if not text or len(text) < 3:
                continue
            if any(skip in aria for skip in skip_labels):
                continue
            if text in skip_texts:
                continue
            if "Load" in text and "more" in text:
                continue
            if text not in section_names:
                section_names.append(text)
        except StaleElementReferenceException:
            continue

    print(f"  Found {len(section_names)} content section(s):")
    for s in section_names:
        print(f"     - {s}")

    # Step 3: For each section, click to expand, scroll within, collect ALL links
    all_file_links = []  # (section_name, url, link_text)

    def collect_links_from_page(drv, section):
        """Collect all downloadable links from current page state."""
        links_found = []
        # Scroll through the page to load lazy content
        drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        drv.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        for a in drv.find_elements(By.TAG_NAME, "a"):
            try:
                href = a.get_attribute("href") or ""
                link_text = a.text.strip() or ""
            except StaleElementReferenceException:
                continue
            if not href:
                continue

            if "bbcswebdav" in href:
                links_found.append((section, href, link_text))
            elif "/outline/file/" in href:
                links_found.append((section, href, link_text))
            elif "panopto" in href.lower() and link_text:
                print(f"     [panopto] {link_text}")

        # Also scan page source for bbcswebdav URLs not in <a> tags
        src = drv.page_source
        existing_urls = {x[1] for x in links_found}
        for match in _re.finditer(r'https?://[^"]*bbcswebdav[^"]*', src):
            url = match.group()
            if url not in existing_urls:
                links_found.append((section, url, ""))
                existing_urls.add(url)

        return links_found

    for section_name in section_names:
        try:
            print(f"\n  \U0001F4C1 Expanding: {section_name}")

            # Re-find the button fresh by matching text
            found = False
            # Scroll through page to find the button
            buttons = driver.find_elements(By.CSS_SELECTOR, "button")
            for btn in buttons:
                try:
                    btn_text = btn.text.strip()
                    if btn_text == section_name:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(0.5)
                        btn.click()
                        found = True
                        break
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue

            if not found:
                # Try partial match as fallback
                for btn in driver.find_elements(By.CSS_SELECTOR, "button"):
                    try:
                        btn_text = btn.text.strip()
                        if section_name in btn_text or btn_text in section_name:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            time.sleep(0.5)
                            btn.click()
                            found = True
                            break
                    except (StaleElementReferenceException, Exception):
                        continue

            if not found:
                print(f"     [warn] Could not find button for '{section_name}'")
                continue

            time.sleep(4)

            # Collect links from the expanded section
            section_links = collect_links_from_page(driver, section_name)
            if section_links:
                print(f"     Found {len(section_links)} link(s)")
            all_file_links.extend(section_links)

            # Navigate back to outline and reload all sections
            driver.get(outline_url)
            time.sleep(4)
            load_all_content(driver)

        except Exception as e:
            err_msg = str(e).split('\n')[0][:100]
            print(f"     [warn] Could not expand '{section_name}': {err_msg}")
            try:
                driver.get(outline_url)
                time.sleep(4)
                load_all_content(driver)
            except Exception:
                pass

    # Step 4: Process and download all collected links
    # Deduplicate while preserving section assignment
    unique_links = []
    seen_urls = set()
    for section_name, url, link_text in all_file_links:
        if url not in seen_urls:
            seen_urls.add(url)
            unique_links.append((section_name, url, link_text))

    print(f"\n  Collected {len(unique_links)} unique link(s) to process")

    for section_name, url, link_text in unique_links:
        if url in downloaded_urls:
            continue
        downloaded_urls.add(url)

        section_dir = make_dir(course_dir / sanitise(section_name))

        # If it's a file detail page, navigate to it and find the actual download URL
        if "/outline/file/" in url and "bbcswebdav" not in url:
            try:
                driver.get(url)
                time.sleep(5)
                session = cookies_to_session(driver)

                # Look for bbcswebdav links on the file detail page
                found_download = False

                # Check <a> tags
                for a in driver.find_elements(By.TAG_NAME, "a"):
                    try:
                        href = a.get_attribute("href") or ""
                    except StaleElementReferenceException:
                        continue
                    if "bbcswebdav" in href and href not in downloaded_urls:
                        downloaded_urls.add(href)
                        download_file(href, section_dir, session)
                        file_count += 1
                        found_download = True

                # Also check page source for download URLs
                if not found_download:
                    src = driver.page_source
                    for match in _re.finditer(r'https?://[^"]*bbcswebdav[^"]*', src):
                        dl_url = match.group()
                        if dl_url not in downloaded_urls:
                            downloaded_urls.add(dl_url)
                            download_file(dl_url, section_dir, session)
                            file_count += 1
                            found_download = True

                if not found_download:
                    print(f"     [skip] No download found for: {link_text or url}")
            except Exception as e:
                err_msg = str(e).split('\n')[0][:80]
                print(f"     [warn] Could not process file page: {err_msg}")
        else:
            # Direct bbcswebdav URL
            download_file(url, section_dir, session)
            file_count += 1

    print(f"\n  \u2705 Course crawl complete. Downloaded {file_count} file(s).")
    return file_count


def crawl_course_classic(driver, session: requests.Session, course_dir: Path):
    """Crawl a Blackboard Classic course page and all its sub pages."""
    visited = set()
    queue = [driver.current_url]
    all_file_links = []
    file_count = 0

    print(f"\n  Crawling course content (Classic mode)...")

    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            driver.get(url)
            time.sleep(2)
        except Exception as e:
            print(f"  [warn] Could not load page: {e}")
            continue

        page_title = get_page_title(driver)
        if page_title:
            print(f"  \U0001F4C1 Section: {page_title}")

        section_dir = course_dir
        if page_title and page_title != sanitise(course_dir.name):
            section_dir = make_dir(course_dir / page_title)

        file_links = extract_file_links(driver)
        if file_links:
            print(f"     Found {len(file_links)} file(s)")

        for link in file_links:
            if link not in all_file_links:
                all_file_links.append(link)
                download_file(link, section_dir, session)
                file_count += 1

        subpages = extract_subpage_links(driver)
        for sp in subpages:
            if sp not in visited:
                queue.append(sp)

    print(f"\n  \u2705 Course crawl complete. Processed {file_count} file(s) across {len(visited)} page(s).")
    return file_count


# ══════════════════════════════════════════════
#  SIDEBAR MENU CRAWLING (Ultra style)
# ══════════════════════════════════════════════

def try_find_sidebar_links(driver) -> list:
    """For Blackboard Ultra, try to find course menu / sidebar links."""
    links = []
    selectors = [
        "#courseMenuPalette_contents a",
        ".courseListing a",
        "nav a[href*='content']",
        "#menuPu498 a",
        "ul.portletList-img a",
    ]
    for sel in selectors:
        try:
            for a in driver.find_elements(By.CSS_SELECTOR, sel):
                href = a.get_attribute("href") or ""
                if href and ("content" in href.lower() or "material" in href.lower()):
                    links.append(href)
        except Exception:
            continue
    return list(set(links))


# ══════════════════════════════════════════════
#  MAIN — INTERACTIVE LOOP
# ══════════════════════════════════════════════

def main():
    root = make_dir(DOWNLOAD_DIR)
    print("=" * 60)
    print("  BLACKBOARD COURSE CONTENT DOWNLOADER")
    print("  University of Aberdeen")
    print("=" * 60)
    print(f"\n  Downloads will be saved to:\n  {Path(DOWNLOAD_DIR).resolve()}\n")

    driver = create_driver(use_profile=SKIP_LOGIN)
    total_files = 0

    try:
        # Step 1: Open Blackboard and let user log in
        start_url = DIRECT_URL if DIRECT_URL else BLACKBOARD_URL
        print(f"\u27a1  Opening {start_url} ...")
        driver.get(start_url)
        if SKIP_LOGIN:
            print("  Waiting for page to fully load (SSO redirect + Blackboard Ultra)...")
            time.sleep(15)
            # Check if we landed on a login page and need more time
            current = driver.current_url
            if "login" in current.lower() or "sso" in current.lower() or "adfs" in current.lower():
                print("  Detected login/SSO redirect, waiting longer...")
                time.sleep(15)
        else:
            print()
            print("-" * 60)
            print("  LOG IN MANUALLY in the Chrome window (if needed).")
            print("  Once you are fully logged in and see the course/dashboard,")
            print("  come back here and press Enter.")
            print("-" * 60)
            input("\n  Press Enter once you are logged in ... ")
            print()

        # Refresh cookies after login
        session = cookies_to_session(driver)

        # Direct mode: single course, then exit
        if DIRECT_URL and DIRECT_NAME:
            course_name = sanitise(DIRECT_NAME)
            course_dir = make_dir(root / course_name)
            print(f"\n  \U0001F4DA Course: {course_name}")
            print(f"  Saving to: {course_dir}")

            # Navigate to the course URL if not already there
            if driver.current_url != DIRECT_URL:
                driver.get(DIRECT_URL)
                time.sleep(3)
                session = cookies_to_session(driver)

            sidebar_links = try_find_sidebar_links(driver)
            if sidebar_links:
                print(f"  Found {len(sidebar_links)} sidebar section(s) to crawl")

            count = crawl_course(driver, session, course_dir)
            total_files += count

            for sl in sidebar_links:
                try:
                    driver.get(sl)
                    time.sleep(2)
                    session = cookies_to_session(driver)
                    count = crawl_course(driver, session, course_dir)
                    total_files += count
                except Exception as e:
                    print(f"  [warn] Sidebar link failed: {e}")

            print(f"\n  Done with '{course_name}'!")
        else:
            # Step 2: Interactive course loop
            course_num = 0
            while True:
                print("=" * 60)
                print("  COURSE DOWNLOAD MODE")
                print("=" * 60)
                print()
                print("  In the Chrome window, navigate to a course page.")
                print("  Then come back here and type the course name")
                print("  (this will be used as the folder name).")
                print()
                print("  Type 'quit' or 'q' to exit.\n")

                course_name = input("  Course name (or 'quit'): ").strip()
                if course_name.lower() in ("quit", "q", "exit"):
                    break
                if not course_name:
                    print("  [!] Please enter a course name.\n")
                    continue

                course_name = sanitise(course_name)
                course_dir = make_dir(root / course_name)
                course_num += 1

                print(f"\n  \U0001F4DA Course #{course_num}: {course_name}")
                print(f"  Saving to: {course_dir}")

                # Refresh session cookies (they may have changed during navigation)
                session = cookies_to_session(driver)

                # Also check sidebar for additional content links
                sidebar_links = try_find_sidebar_links(driver)
                if sidebar_links:
                    print(f"  Found {len(sidebar_links)} sidebar section(s) to crawl")

                # Crawl the current page + subpages
                count = crawl_course(driver, session, course_dir)
                total_files += count

                # If there were sidebar links, crawl those too
                for sl in sidebar_links:
                    try:
                        driver.get(sl)
                        time.sleep(2)
                        session = cookies_to_session(driver)
                        count = crawl_course(driver, session, course_dir)
                        total_files += count
                    except Exception as e:
                        print(f"  [warn] Sidebar link failed: {e}")

                print(f"\n  Done with '{course_name}'!")
                print(f"  Total files downloaded so far: {total_files}\n")

    except KeyboardInterrupt:
        print("\n\n  Interrupted by user.")
    finally:
        driver.quit()

    print()
    print("=" * 60)
    print(f"  \U0001F389 All done! {total_files} file(s) downloaded.")
    print(f"  Saved to: {Path(DOWNLOAD_DIR).resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Direct course URL to crawl")
    parser.add_argument("--name", help="Course folder name")
    parser.add_argument("--skip-login", action="store_true", help="Skip login prompt (already logged in)")
    args = parser.parse_args()
    if args.url:
        DIRECT_URL = args.url
    if args.name:
        DIRECT_NAME = args.name
    if args.skip_login:
        SKIP_LOGIN = True
    main()
