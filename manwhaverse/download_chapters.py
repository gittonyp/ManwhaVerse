#!/usr/bin/env python3
"""
Standalone script to download chapters for existing manga.
This downloads chapter images and populates the chapters/chapter_images tables.
Run this after the backend is already set up with manga entries.

Usage:
    python3 download_chapters.py              # Download new chapters for all manga
    python3 download_chapters.py --force      # Force re-download ALL chapters (resets last_chapter to 0)
    python3 download_chapters.py --manga "X"  # Download chapters for a specific manga title
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
from io import BytesIO
import os
import argparse
import time

BASE_URL = "https://www.mgeko.cc"
DB_NAME = "mangadb.db"

def db_insert_chapter(manga_url, title, number, release_date):
    """Insert a chapter into the database and return its ID."""
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
    """Insert image paths for a chapter."""
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
        print(f"   [DB] Saved {len(image_paths)} image paths for chapter {chapter_id}")
    except Exception as e:
        print(f"[DB Error] inserting images: {e}")
    finally:
        con.close()

def db_update_chapter(url, new_chapter_num):
    """Update the last_chapter number for a manga."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("UPDATE manga SET last_chapter=? WHERE url=?", (new_chapter_num, url))
    con.commit()
    con.close()

def db_get_all_manga():
    """Get all manga from the database."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT title, url, last_chapter FROM manga")
    rows = cur.fetchall()
    con.close()
    return rows

def db_reset_last_chapter(url):
    """Reset last_chapter to 0 for a manga (for force download)."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("UPDATE manga SET last_chapter=0 WHERE url=?", (url,))
    con.commit()
    con.close()

def get_all_chapters_link(url_suffix):
    """Get all chapter links for a manga."""
    full_url = BASE_URL + url_suffix + "all-chapters/"
    print(f"   Fetching chapters from: {full_url}")
    try:
        r = requests.get(full_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        anchors = soup.find_all("a", href=re.compile(r"^/reader/"))
        links = [a['href'] for a in anchors]
        print(f"   Found {len(links)} chapters")
        return links
    except Exception as e:
        print(f"[Error] Failed to get chapters: {e}")
        return []

def download_chapter(url_suffix, title, chapter_num, manga_url_suffix):
    """Download all images for a chapter and save to disk + database."""
    print(f"   [Download] Chapter {chapter_num}...")
    full_url = BASE_URL + url_suffix

    try:
        r = requests.get(full_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")

        # Find all images
        imgs = soup.find_all("img", id=re.compile(r'^image-'))
        img_urls = [i.get('src') for i in imgs]

        if not img_urls:
            print(f"   [Warning] No images found for chapter {chapter_num}")
            return False

        # Setup directory
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        chapter_dir = os.path.join("downloads", safe_title, f"ch_{chapter_num}")
        
        if not os.path.exists(chapter_dir):
            os.makedirs(chapter_dir)

        downloaded_image_paths = []

        print(f"   [Download] Downloading {len(img_urls)} images...")
        
        for index, i_url in enumerate(img_urls):
            try:
                img_req = requests.get(i_url, timeout=15)
                if img_req.status_code == 200:
                    filename = f"{index:03d}.jpg" 
                    file_path = os.path.join(chapter_dir, filename)
                    
                    with Image.open(BytesIO(img_req.content)) as img:
                        rgb_im = img.convert("RGB")
                        rgb_im.save(file_path, "JPEG", quality=90)
                        
                    # Store relative path for web serving
                    web_path = f"/downloads/{safe_title}/ch_{chapter_num}/{filename}"
                    downloaded_image_paths.append(web_path)
            except Exception as e:
                print(f"   [Warning] Skipped image {index}: {e}")
                continue

        if not downloaded_image_paths:
            return False

        # Insert chapter into DB
        chap_id = db_insert_chapter(
            manga_url_suffix, 
            f"Chapter {chapter_num}", 
            chapter_num, 
            "2024-01-01"  # Placeholder date
        )
        
        # Insert image paths into DB
        db_insert_chapter_images(chap_id, downloaded_image_paths)
        
        print(f"   [Success] Chapter {chapter_num} saved ({len(downloaded_image_paths)} pages)")
        return True

    except Exception as e:
        print(f"[Error] Failed to download chapter {chapter_num}: {e}")
        return False

def download_chapters_for_manga(title, url_suffix, last_known_chap, max_chapters=None):
    """Download all new chapters for a manga."""
    print(f"\n{'='*60}")
    print(f"Processing: {title}")
    print(f"Last known chapter: {last_known_chap}")
    print(f"{'='*60}")
    
    all_links = get_all_chapters_link(url_suffix)
    
    if not all_links:
        print("   No chapters found. Skipping.")
        return
    
    # Reverse to process from oldest to newest
    all_links.reverse()
    
    downloaded_count = 0
    
    for link in all_links:
        # Extract chapter number from URL
        try:
            chap_num = int(re.findall(r"chapter-(\d+)", link)[0])
        except (IndexError, ValueError):
            continue

        if chap_num > last_known_chap:
            if max_chapters and downloaded_count >= max_chapters:
                print(f"\n   Reached max chapters limit ({max_chapters}). Stopping.")
                break
                
            success = download_chapter(link, title, chap_num, url_suffix)
            
            if success:
                # Update last known chapter in DB
                db_update_chapter(url_suffix, chap_num)
                downloaded_count += 1
            
            # Be nice to the server
            time.sleep(1)
    
    print(f"\n   Downloaded {downloaded_count} new chapters for {title}")

def main():
    parser = argparse.ArgumentParser(description='Download manga chapters')
    parser.add_argument('--force', action='store_true', help='Force re-download all chapters')
    parser.add_argument('--manga', type=str, help='Download only for specific manga title')
    parser.add_argument('--max', type=int, default=5, help='Max chapters to download per manga (default: 5)')
    args = parser.parse_args()

    print("\n" + "="*60)
    print("MANGA CHAPTER DOWNLOADER")
    print("="*60)
    
    rows = db_get_all_manga()
    print(f"Found {len(rows)} manga in database")
    
    for title, url_suffix, last_known_chap in rows:
        # Filter by manga name if specified
        if args.manga and args.manga.lower() not in title.lower():
            continue
        
        # Reset chapter count if force mode
        if args.force:
            print(f"[Force Mode] Resetting last_chapter for {title}")
            db_reset_last_chapter(url_suffix)
            last_known_chap = 0
        
        download_chapters_for_manga(title, url_suffix, last_known_chap, args.max)
    
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("="*60)

if __name__ == '__main__':
    main()
