#!/usr/bin/env python3
"""
Scrapes chapter metadata and image URLs (without downloading images).
Populates the chapters and chapter_images tables with URLs for web frontend.

Usage:
    python3 scrape_chapters.py
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
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
        
        cur.execute("SELECT id FROM chapters WHERE manga_url=? AND number=?", (manga_url, number))
        res = cur.fetchone()
        if res:
            chapter_id = res[0]
    except Exception as e:
        print(f"[DB Error] inserting chapter: {e}")
    finally:
        con.close()
    return chapter_id

def db_insert_chapter_images(chapter_id, image_urls):
    """Insert image URLs for a chapter."""
    if not chapter_id:
        return
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        # Check if images already exist for this chapter
        cur.execute("SELECT COUNT(*) FROM chapter_images WHERE chapter_id=?", (chapter_id,))
        count = cur.fetchone()[0]
        if count > 0:
            print(f"      Chapter {chapter_id} already has images, skipping...")
            con.close()
            return
        
        for idx, url in enumerate(image_urls):
            cur.execute("INSERT INTO chapter_images (chapter_id, page_number, image_path) VALUES (?, ?, ?)", 
                        (chapter_id, idx, url))
        con.commit()
        print(f"      Saved {len(image_urls)} image URLs")
    except Exception as e:
        print(f"[DB Error] inserting images: {e}")
    finally:
        con.close()

def db_get_all_manga():
    """Get all manga from the database."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT title, url, last_chapter FROM manga")
    rows = cur.fetchall()
    con.close()
    return rows

def get_all_chapters_link(url_suffix):
    """Get all chapter links for a manga."""
    full_url = BASE_URL + url_suffix + "all-chapters/"
    try:
        r = requests.get(full_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        anchors = soup.find_all("a", href=re.compile(r"^/reader/"))
        return [a['href'] for a in anchors]
    except Exception as e:
        print(f"[Error] Failed to get chapters: {e}")
        return []

def get_chapter_image_urls(chapter_url_suffix):
    """Scrape image URLs from a chapter page (without downloading)."""
    full_url = BASE_URL + chapter_url_suffix
    try:
        r = requests.get(full_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        
        # Find all images
        imgs = soup.find_all("img", id=re.compile(r'^image-'))
        img_urls = [i.get('src') for i in imgs if i.get('src')]
        return img_urls
    except Exception as e:
        print(f"[Error] Failed to get images: {e}")
        return []

def scrape_chapters_for_manga(title, url_suffix, max_chapters=5):
    """Scrape chapter metadata and image URLs for a manga."""
    print(f"\n{'='*60}")
    print(f"Processing: {title}")
    print(f"{'='*60}")
    
    all_links = get_all_chapters_link(url_suffix)
    
    if not all_links:
        print("   No chapters found. Skipping.")
        return
    
    print(f"   Found {len(all_links)} chapters")
    
    # Reverse to process from oldest to newest, and limit
    all_links.reverse()
    chapters_to_process = all_links[:max_chapters]
    
    print(f"   Processing first {len(chapters_to_process)} chapters...")
    
    for link in chapters_to_process:
        # Extract chapter number from URL
        try:
            chap_num = int(re.findall(r"chapter-(\d+)", link)[0])
        except (IndexError, ValueError):
            continue

        print(f"   Chapter {chap_num}:")
        
        # Insert chapter into DB
        chap_id = db_insert_chapter(
            url_suffix, 
            f"Chapter {chap_num}", 
            chap_num, 
            "2024-01-01"
        )
        
        if chap_id:
            # Get image URLs (without downloading)
            image_urls = get_chapter_image_urls(link)
            
            if image_urls:
                db_insert_chapter_images(chap_id, image_urls)
            else:
                print(f"      No images found")
        
        # Be nice to the server
        time.sleep(0.5)
    
    print(f"   Done!")

def main():
    print("\n" + "="*60)
    print("CHAPTER URL SCRAPER (No Download)")
    print("="*60)
    
    rows = db_get_all_manga()
    print(f"Found {len(rows)} manga in database\n")
    
    for title, url_suffix, last_known_chap in rows:
        scrape_chapters_for_manga(title, url_suffix, max_chapters=3)
    
    print("\n" + "="*60)
    print("SCRAPING COMPLETE!")
    print("="*60)
    
    # Show summary
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM chapters")
    chap_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM chapter_images")
    img_count = cur.fetchone()[0]
    con.close()
    
    print(f"\nDatabase now has:")
    print(f"  - {chap_count} chapters")
    print(f"  - {img_count} image URLs")

if __name__ == '__main__':
    main()
