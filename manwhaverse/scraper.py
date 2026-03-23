import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
from io import BytesIO
import os
import asyncio
from telethon import TelegramClient, functions
from telethon.extensions import html
from multiprocessing import Pool
import img2pdf
import shutil
from dotenv import load_dotenv

load_dotenv()
# --- CONFIGURATION ---
# Get these from my.telegram.org
API_ID = os.getenv("api_id")  # REPLACE WITH YOUR ID
API_HASH = os.getenv("api_hash") # REPLACE WITH YOUR HASH
BASE_URL = "https://www.mgeko.cc"
DB_NAME = "mangadb.db"
MAX_CONCURRENT_TASKS = 4
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

client = None
if API_ID and API_HASH:
    try:
        client = TelegramClient('anon', int(API_ID), API_HASH)
    except Exception as e:
        print(f"[Warning] Telegram client init failed: {e}")
else:
    print("[Warning] No API_ID/API_HASH found. Telegram features disabled.")

# --- DATABASE FUNCTIONS (V2 - Sidecar Tables) ---
def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    
    # 1. LEGACY TABLE (Keep untouched)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS manga(
            title text, 
            url text UNIQUE, 
            last_chapter integer, 
            channel_id integer
        )
    """)

    # 2. NEW SIDECAR TABLES
    # Stores rich metadata not present in the original 'manga' table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS manga_details(
            manga_url text PRIMARY KEY,
            description text,
            banner_image text,
            author text,
            status text,
            views text,
            genres text,
            FOREIGN KEY(manga_url) REFERENCES manga(url)
        )
    """)

    # Stores chapters linked to the manga
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chapters(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manga_url text,
            title text,
            number REAL,
            release_date text,
            FOREIGN KEY(manga_url) REFERENCES manga(url),
            UNIQUE(manga_url, number)
        )
    """)

    # Stores paths to images for each chapter (for the Web API)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chapter_images(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id INTEGER,
            page_number INTEGER,
            image_path text,
            FOREIGN KEY(chapter_id) REFERENCES chapters(id)
        )
    """)

    con.commit()
    con.close()

def db_add_manga(title, url, channel_id):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO manga VALUES (?, ?, ?, ?)", (title, url, 0, channel_id))
        con.commit()
        print(f"[DB] Added {title} to database.")
    except sqlite3.IntegrityError:
        print(f"[DB] {title} already exists in database.")
    finally:
        con.close()

def db_update_manga_details(url, description, banner, author, status, views, genres):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT OR REPLACE INTO manga_details 
            (manga_url, description, banner_image, author, status, views, genres)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (url, description, banner, author, status, views, genres))
        con.commit()
        print(f"[DB] Updated details for {url}")
    except Exception as e:
        print(f"[DB Error] updating details: {e}")
    finally:
        con.close()

def db_insert_chapter(manga_url, title, number, release_date):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    chapter_id = None
    try:
        cur.execute("""
            INSERT OR IGNORE INTO chapters (manga_url, title, number, release_date)
            VALUES (?, ?, ?, ?)
        """, (manga_url, title, number, release_date))
        con.commit()
        
        # Get the ID (whether inserted or existing)
        cur.execute("SELECT id FROM chapters WHERE manga_url=? AND number=?", (manga_url, number))
        res = cur.fetchone()
        if res:
            chapter_id = res[0]
    except Exception as e:
        print(f"[DB Error] inserting chapter: {e}")
    finally:
        con.close()
    return chapter_id

def db_insert_chapter_images(chapter_id, image_paths):
    if not chapter_id:
        return
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        # Clear old images for this chapter if re-downloading
        cur.execute("DELETE FROM chapter_images WHERE chapter_id=?", (chapter_id,))
        
        for idx, path in enumerate(image_paths):
            cur.execute("INSERT INTO chapter_images (chapter_id, page_number, image_path) VALUES (?, ?, ?)", 
                        (chapter_id, idx, path))
        con.commit()
    except Exception as e:
        print(f"[DB Error] inserting images: {e}")
    finally:
        con.close()

def db_get_manga(url):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT * FROM manga WHERE url=?", (url,))
    result = cur.fetchone()
    con.close()
    return result

def db_update_chapter(url, new_chapter_num):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("UPDATE manga SET last_chapter=? WHERE url=?", (new_chapter_num, url))
    con.commit()
    con.close()

def db_get_all_manga():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT title, url FROM manga")
    rows = cur.fetchall()
    con.close()
    return rows

# --- SCRAPER FUNCTIONS ---
def get_manga_details_extended(url_suffix):
    """
    Fetches extended details matching the new schema requirements.
    Updated to properly extract description after "The Summary is" phrase.
    """
    full_url = "https://www.mgeko.cc" + url_suffix
    print(f"[Scraper] Fetching extended details from {full_url}...")
    
    try:
        r = requests.get(full_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")

        # 1. Description - Extract after "The Summary is" phrase
        summary = "No description available."
        description_tag = soup.find("p", class_="description")
        if description_tag:
            full_text = description_tag.get_text(separator='\n').strip()
            # The actual summary starts AFTER "The Summary is"
            if "The Summary is" in full_text:
                parts = full_text.split("The Summary is", 1)
                if len(parts) > 1:
                    summary = parts[1].strip()
                    # Clean up excessive newlines
                    summary = re.sub(r'\n{3,}', '\n\n', summary)
            else:
                # Fallback to old logic
                text_parts = full_text.split('\n')
                clean_parts = [t.strip() for t in text_parts if t.strip()]
                if len(clean_parts) > 1:
                    summary = clean_parts[1]
                elif len(clean_parts) == 1:
                    summary = clean_parts[0]
            
            # Limit length
            if len(summary) > 1500:
                summary = summary[:1500] + "..."

        # 2. Cover/Banner Image - Use og:image meta tag (more reliable)
        cover_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            cover_url = og_image["content"]
        else:
            # Fallback to figure.cover
            div_cover = soup.find("figure", class_="cover")
            if div_cover:
                img_tag = div_cover.find("img")
                if img_tag:
                    cover_url = img_tag.get('data-src') or img_tag.get('src')

        # 3. Metadata (Author, Status, Genres, Views)
        author = "Unknown"
        status = "Unknown"
        views = "0"
        genres = []

        # Genres - look for genre links
        genre_links = soup.select(".genres a, .genre a, .tags a")
        if genre_links:
            genres = [g.text.strip() for g in genre_links if g.text.strip()]

        return {
            "description": summary,
            "banner_image": cover_url,
            "author": author,
            "status": status,
            "views": views,
            "genres": ", ".join(genres[:10]) if genres else ""
        }

    except Exception as e:
        print(f"[Error] Failed to fetch extended details: {e}")
        return None

def download_cover_image(img_url, title):
    if not img_url:
        return None
    
    try:
        r = requests.get(img_url, timeout=10)
        if r.status_code == 200:
            # Create filename
            # ext = img_url.split('.')[-1]
            folder_name = re.sub(r'[\\/*?:"<>|]', "", title)
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            filename = f"{folder_name}/{title}_cover.png"
            
            # Save to disk
            with open(filename, 'wb') as f:
                f.write(r.content)
            return filename
    except Exception as e:
        print(f"[Error] Could not download cover: {e}")
    return None

def get_all_chapters_link(url_suffix):
    full_url = BASE_URL + url_suffix + "all-chapters/"
    try:
        r = requests.get(full_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        # Find links that look like /reader/
        anchors = soup.find_all("a", href=re.compile(r"^/reader/"))
        # Reverse so oldest is first (index 0) if you want to download in order
        return [a['href'] for a in anchors]
    except Exception as e:
        print(f"[Error] Failed to get chapters: {e}")
        return []

def download_chapter_and_process(url_suffix, title, chapter_num, manga_url_suffix):
    """
    Downloads images, saves them for web (API), AND creates PDF for Telegram.
    Updates 'chapters' and 'chapter_images' tables.
    """
    print(f"[Scraper] Downloading {title} Chapter {chapter_num}...")
    full_url = BASE_URL + url_suffix

    try:
        r = requests.get(full_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")

        # Find all images
        imgs = soup.find_all("img", id=re.compile(r'^image-'))
        img_urls = [i.get('src') for i in imgs]

        if not img_urls:
            print("No images found.")
            return None

        # 1. Setup Directories
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        
        # Web Serving Directory: downloads/{manga_title}/{chapter_num}/
        # This will be served by Spring Boot
        web_base_dir = "downloads" 
        chapter_dir = os.path.join(web_base_dir, safe_title, f"ch_{chapter_num}")
        
        if not os.path.exists(chapter_dir):
            os.makedirs(chapter_dir)

        downloaded_image_paths = []

        # 2. Download Images
        print(f"   > Processing {len(img_urls)} images...")
        
        for index, i_url in enumerate(img_urls):
            try:
                img_req = requests.get(i_url, timeout=10)
                if img_req.status_code == 200:
                    # Save for Web API
                    filename = f"{index:03d}.jpg" 
                    file_path = os.path.join(chapter_dir, filename)
                    
                    with Image.open(BytesIO(img_req.content)) as img:
                        rgb_im = img.convert("RGB")
                        rgb_im.save(file_path, "JPEG", quality=90)
                        
                    downloaded_image_paths.append(file_path)
            except Exception as e:
                print(f"   [Warning] Skipped image {index}: {e}")
                continue

        if not downloaded_image_paths:
            return None

        # 3. Update DB (Chapters & Images) (For Web API)
        chap_id = db_insert_chapter(manga_url_suffix, f"Chapter {chapter_num}", chapter_num, "2023-01-01") # Date placeholder
        db_insert_chapter_images(chap_id, downloaded_image_paths)

        # 4. Create PDF (For Telegram - Legacy Requirement)
        # We use the images we just saved
        pdf_filename = f"{safe_title} - Ch {chapter_num}.pdf"
        output_pdf_path = os.path.join(web_base_dir, safe_title, pdf_filename) # Store PDF next to chapter folder or root
        
        try:
            with open(output_pdf_path, "wb") as f:
                f.write(img2pdf.convert(downloaded_image_paths))
            return output_pdf_path
        except Exception as e:
            print(f"[Error] PDF conversion failed: {e}")
            return None

    except Exception as e:
        print(f"[Error] Failed download: {e}")
        return None

# --- BACKFILL / MIGRATION ---
async def backfill_existing_manga():
    """
    Iterates through all manga in the legacy 'manga' table.
    Scrapes metadata to populate 'manga_details'.
    Checking for chapters is harder without re-downloading everything, 
    but we can at least fill the details.
    """
    print("\n[Backfill] Starting backfill of manga details...")
    rows = db_get_all_manga()
    print(f"[Backfill] Found {len(rows)} manga to process.")
    
    for row in rows:
        title, url_suffix = row
        print(f"[Backfill] Processing: {title}")
        
        # 1. Fetch & Update Details
        details = get_manga_details_extended(url_suffix)
        if details:
            db_update_manga_details(
                url_suffix, 
                details['description'], 
                details['banner_image'], 
                details['author'], 
                details['status'],
                details['views'],
                details['genres']
            )
        
        # Note: We are NOT automatically downloading all chapters here to save bandwidth/time.
        # The chapter list will populate as new chapters are found or if we force a re-scan.
        
        await asyncio.sleep(1) # Be nice to the server

    print("[Backfill] Completed.")


# --- TELEGRAM FUNCTIONS (ASYNC) ---

async def create_channel(title):
    print(f"[Telegram] Creating channel for: {title}")
    try:
        result = await client(functions.channels.CreateChannelRequest(
            title=title[:120], # Telegram title limit
            about=f'Manga updates for {title}',
            broadcast=True,
            democracy=True
        ))
        # Telethon returns Updates object, we need the channel ID
        # usually in result.chats[0]
        new_channel = result.chats[0]
        print(f"[Telegram] Channel created. ID: {new_channel.id}")
        return new_channel.id
    except Exception as e:
        print(f"[Telegram Error] Could not create channel: {e}")
        return None

def resize_for_telegram(input_path, output_path, size=512):
    img = Image.open(input_path)
    width, height = img.size

    # Crop to square (center crop)
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim

    img = img.crop((left, top, right, bottom))
    img = img.resize((size, size), Image.LANCZOS)
    out=output_path[:-4]+"edited.png"
    img.save(out, quality=95)
    return out

from telethon import functions, types
import os

def format_caption(title, description, manga_info=None):
    """
    Formats the caption to look like the screenshot with Quotes and Styling.
    """
    # 1. Basic Info (You can customize these static values or scrape them)
    # Since we are just scraping title/desc, we will use placeholders or scraped data
    manga_type = "MANHWA"
    status = "ONGOING"
    
    # 2. Build the "Info Block" with Bold Arrows
    # HTML format is easier for mixed styling
    info_block = (
        f"<b>➜ Type:</b> {manga_type}\n"
        f"<b>➜ Status:</b> {status}\n"
        f"<b>➜ Genres:</b> Action, Adventure, Fantasy" 
    )

    # 3. Handle Description Length (Crucial Step!)
    # Caption limit is 1024. We reserve ~300 chars for title/info.
    # So description must be max ~700 chars.
    max_desc_len = 700
    if len(description) > max_desc_len:
        description = description[:max_desc_len] + "... (Read More on Site)"

    # 4. Construct the Final HTML Caption
    # <blockquote> adds the vertical bar on the left
    caption = (
        f"<blockquote><b>{title}</b></blockquote>\n\n"  # The Title Box
        f"{info_block}\n\n"                              # The Info Lines
        f"<blockquote>{description}</blockquote>"        # The Description Box
    )
    
    return caption

async def create_channel_advanced(title, username, cover_image_path, description):
    """
    Creates a public channel, sets a profile photo, and sends an intro.
    """
    print(f"[Telegram] Creating channel: {title}...")

    # 1. Create the Channel (Initially Private)
    # Note: 'democracy' is not a standard arg for Channels, usually just broadcast=True
    created = await client(functions.channels.CreateChannelRequest(
        title=title,
        about=title,
        broadcast=True
    ))
    
    # Get the channel entity (ID and Hash) from the result
    channel_entity = created.chats[0]
    print(f"[Telegram] Channel created. ID: {channel_entity.id}")

    # 2. Make it Public (Set Username)
    # WARNING: Usernames must be unique globally and 5+ chars. 
    # If this fails, the channel remains private.
    if username:
        try:
            await client(functions.channels.UpdateUsernameRequest(
                channel=channel_entity,
                username=username[0:30]
            ))
            print(f"[Telegram] Channel is now public: t.me/{username}")
        except Exception as e:
            print(f"[Error] Could not set username '{username}': {e}")
            print("Channel will remain private.")

    # 3. Set Channel Profile Photo

    logo_image=resize_for_telegram(cover_image_path,(cover_image_path))

    if logo_image and os.path.exists(logo_image):
        print("[Telegram] Setting profile photo...")
        try:
            # Upload the file first
            uploaded_file = await client.upload_file(logo_image)
            
            # Request to edit the photo
            await client(functions.channels.EditPhotoRequest(
                channel=channel_entity,
                photo=uploaded_file
            ))
        except Exception as e:
            print(f"[Error] Could not set profile photo: {e}")

    # 4. Send Intro Message (Image + Markdown)
    if cover_image_path and os.path.exists(cover_image_path):
        print("[Telegram] Sending intro message...")
        
        caption=format_caption(title,description)

        await client.send_file(
            entity=channel_entity,
            file=cover_image_path,
            caption=caption,
            parse_mode='html' # Enables Markdown
        )

    return channel_entity.id

def format_caption_chapter(captiont):
   
    # 4. Construct the Final HTML Caption
    # <blockquote> adds the vertical bar on the left
    caption = (
        f"<blockquote><b>{captiont}</b></blockquote>\n\n"  # The Title Box
    )
    
    return caption

async def send_pdf_to_channel(channel_id, file_path, caption):
    print(f"[Telegram] Uploading {file_path}...")
    caption=format_caption_chapter(caption)
   # receiver = await client.get_entity(channel_id)
    try:
        await client.send_file(
            entity=channel_id,
            file=file_path,
            caption=caption,
            parse_mode='html'
        )
        print("[Telegram] Upload complete.")
    except Exception as e:
        print(f"[Telegram Error] Upload failed: {e}")


def sanitize_telegram_username(title: str) -> str:
    username = title.lower()

    # keep only a-z, 0-9, space, underscore
    username = re.sub(r'[^a-z0-9_ ]', '', username)

    # spaces -> single underscore
    username = re.sub(r'\s+', '_', username)

    # trim underscores
    username = re.sub(r'^_+|_+$', '', username)

    # must start with a letter
    if not re.match(r'^[a-z]', username):
        username = 'u_' + username

    # length constraints
    username = username[:32]

    # minimum length
    if len(username) < 5:
        username = username.ljust(5, '0')

    return username


async def process_new_manga(title, url_suffix):
    """
    Full workflow: 
    1. Scrape Description & Cover
    2. Create Channel
    3. Upload Cover & Intro
    4. Save to DB
    """
    
    # 1. Get Details
    # Use V2 extended details
    details = get_manga_details_extended(url_suffix)
    summary = details['description'] if details else "No description"
    cover_url = details['banner_image'] if details else None
    
    print(f"Summary found: {summary[:50]}...")
    
    # 2. Download Cover Image temporarily
    local_cover_path = download_cover_image(cover_url, title)
    
    usernamemade=sanitize_telegram_username(title)
    # 3. Create Channel and Send Intro
    # (Using the create_channel_advanced function from previous step)
    channel_id = await create_channel_advanced(
        title=title,
        username=usernamemade+"devscans", 
        cover_image_path=local_cover_path,
        description=summary
    )

    if channel_id:
        # 4. Add to Database
        # Note: You need to import your db_add_manga function here
        db_add_manga(title, url_suffix, channel_id)
        
        # V2: Also save details to sidecar
        if details:
             db_update_manga_details(
                url_suffix, 
                details['description'], 
                details['banner_image'], 
                details['author'], 
                details['status'],
                details['views'],
                details['genres']
            )
        
    # Cleanup: Remove the temporary cover image
    if local_cover_path and os.path.exists(local_cover_path):
        os.remove(local_cover_path)


async def check_updates_and_upload():
    """Loops through DB, checks for new chapters, downloads and uploads them"""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT title, url, last_chapter, channel_id FROM manga")
    rows = cur.fetchall()
    con.close()

    for row in rows:
        title, url_suffix, last_known_chap, channel_id = row
        print(f"\nChecking updates for {title}...")
        
        # Get all chapter links
        all_links = get_all_chapters_link(url_suffix)
        # Reverse list to process from old to new
        all_links.reverse() 
        
        for link in all_links:
            # Extract chapter number from URL (basic regex)
            # URL format example: /reader/title-chapter-10/
            try:
                # Find number specifically in the last part of url
                chap_num = int(re.findall(r"chapter-(\d+)", link)[0])
            except IndexError:
                continue

            if chap_num > last_known_chap:
                print(f"Found new chapter: {chap_num}")
                
                # 1. Download & Process (V2: Saves images + DB updates)
                pdf_path = download_chapter_and_process(link, title, chap_num, url_suffix)
                
                # 2. Upload to Telegram
                if pdf_path and channel_id:
                    await send_pdf_to_channel(channel_id, pdf_path, f"{title} - Chapter {chap_num}")
                    
                    # We can remove the PDF after upload, but keep the images!
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                    
                    # 3. Update DB (Legacy Table)
                    db_update_chapter(url_suffix, chap_num)
                    
                    # Optional: Sleep to avoid hitting limits
                    await asyncio.sleep(2) 

# --- MAIN ENTRY POINT ---
async def main():
    init_db()
    # await client.get_dialogs() # Requires login
    
    # MIGRATION: Uncomment to run one-time backfill
    # await backfill_existing_manga()
    
    # EXAMPLE 1: Add a new Manga
    # await process_new_manga("Test Manga", "/manga/test-manga/")
    
    # EXAMPLE 2: Check for updates
    # await check_updates_and_upload()

    print("Tasks finished.")

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
