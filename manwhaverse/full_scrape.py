#!/usr/bin/env python3
"""
Complete scraper that:
1. Scrapes metadata (author, description, genres, status, views, banner) for all manga
2. Scrapes ALL chapter URLs and image URLs for all manga

Usage:
    python3 full_scrape.py
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time

BASE_URL = "https://www.mgeko.cc"
DB_NAME = "mangadb.db"

# ============================================
# DATABASE FUNCTIONS
# ============================================

def db_update_manga_details(url, description, banner, author, status, views, genres):
    """Update or insert manga details in the sidecar table."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT OR REPLACE INTO manga_details 
            (manga_url, description, banner_image, author, status, views, genres)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (url, description, banner, author, status, views, genres))
        con.commit()
        print(f"   [DB] Updated details")
    except Exception as e:
        print(f"[DB Error] updating details: {e}")
    finally:
        con.close()

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
        # Check if images already exist
        cur.execute("SELECT COUNT(*) FROM chapter_images WHERE chapter_id=?", (chapter_id,))
        count = cur.fetchone()[0]
        if count > 0:
            con.close()
            return False  # Already has images
        
        for idx, url in enumerate(image_urls):
            cur.execute("INSERT INTO chapter_images (chapter_id, page_number, image_path) VALUES (?, ?, ?)", 
                        (chapter_id, idx, url))
        con.commit()
        return True
    except Exception as e:
        print(f"[DB Error] inserting images: {e}")
        return False
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

def db_chapter_exists(manga_url, number):
    """Check if a chapter already exists with images."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
        SELECT c.id, COUNT(ci.id) 
        FROM chapters c 
        LEFT JOIN chapter_images ci ON c.id = ci.chapter_id 
        WHERE c.manga_url=? AND c.number=?
        GROUP BY c.id
    """, (manga_url, number))
    res = cur.fetchone()
    con.close()
    if res and res[1] > 0:
        return True
    return False

# ============================================
# SCRAPER FUNCTIONS
# ============================================

def get_manga_metadata(url_suffix):
    """Scrape full metadata from the manga page."""
    full_url = BASE_URL + url_suffix
    print(f"   Fetching metadata from {full_url}")
    
    try:
        r = requests.get(full_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")

        # Description
        description = "No description available."
        desc_tag = soup.find("p", class_="description")
        if desc_tag:
            text_parts = desc_tag.get_text(separator='\n').split('\n')
            clean_parts = [t.strip() for t in text_parts if t.strip()]
            if len(clean_parts) > 1:
                description = clean_parts[1]
            elif len(clean_parts) == 1:
                description = clean_parts[0]

        # Cover/Banner Image
        banner_image = None
        div_cover = soup.find("figure", class_="cover")
        if div_cover:
            img_tag = div_cover.find("img")
            if img_tag:
                banner_image = img_tag.get('data-src') or img_tag.get('src')

        # Author, Status, Genres from the manga info table
        author = "Unknown"
        status = "Unknown"
        views = "0"
        genres = []

        # Look for the manga-info or summary section
        info_container = soup.find("div", class_="summary")
        if not info_container:
            info_container = soup.find("div", class_="manga-info")
        
        if info_container:
            # Try to find rows/items with labels
            items = info_container.find_all(["div", "li", "p"])
            for item in items:
                text = item.get_text().lower()
                if "author" in text or "artist" in text:
                    # Try to extract value
                    links = item.find_all("a")
                    if links:
                        author = ", ".join([a.get_text().strip() for a in links])
                    else:
                        parts = item.get_text().split(":")
                        if len(parts) > 1:
                            author = parts[1].strip()
                elif "status" in text:
                    if "ongoing" in text:
                        status = "Ongoing"
                    elif "completed" in text or "finished" in text:
                        status = "Completed"
                    else:
                        parts = item.get_text().split(":")
                        if len(parts) > 1:
                            status = parts[1].strip()

        # Genres - look for genre links
        genre_links = soup.select(".genres a, .genre a, .tags a")
        if genre_links:
            genres = [g.get_text().strip() for g in genre_links if g.get_text().strip()]
        
        # Try alternative genre location
        if not genres:
            genre_container = soup.find("div", class_="genres")
            if genre_container:
                genre_links = genre_container.find_all("a")
                genres = [g.get_text().strip() for g in genre_links]

        # Views - look for view count
        view_element = soup.find(string=re.compile(r"[0-9,]+\s*(views|Views)", re.I))
        if view_element:
            match = re.search(r"([0-9,]+)", view_element)
            if match:
                views = match.group(1)

        return {
            "description": description[:1000] if description else "No description",  # Limit length
            "banner_image": banner_image,
            "author": author[:200] if author else "Unknown",
            "status": status,
            "views": views,
            "genres": ", ".join(genres[:10]) if genres else ""  # Limit genres
        }

    except Exception as e:
        print(f"   [Error] Failed to fetch metadata: {e}")
        return None

def get_all_chapters_link(url_suffix):
    """Get all chapter links for a manga."""
    full_url = BASE_URL + url_suffix + "all-chapters/"
    try:
        r = requests.get(full_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        anchors = soup.find_all("a", href=re.compile(r"^/reader/"))
        return [a['href'] for a in anchors]
    except Exception as e:
        print(f"   [Error] Failed to get chapters: {e}")
        return []

def get_chapter_image_urls(chapter_url_suffix):
    """Scrape image URLs from a chapter page."""
    full_url = BASE_URL + chapter_url_suffix
    try:
        r = requests.get(full_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        
        imgs = soup.find_all("img", id=re.compile(r'^image-'))
        img_urls = [i.get('src') for i in imgs if i.get('src')]
        return img_urls
    except Exception as e:
        print(f"   [Error] Failed to get images: {e}")
        return []

# ============================================
# MAIN PROCESSING
# ============================================

def process_manga(title, url_suffix):
    """Process a single manga: metadata + all chapters."""
    print(f"\n{'='*60}")
    print(f"Processing: {title}")
    print(f"URL: {url_suffix}")
    print(f"{'='*60}")
    
    # 1. Scrape and update metadata
    print("\n   [Step 1] Scraping metadata...")
    metadata = get_manga_metadata(url_suffix)
    if metadata:
        db_update_manga_details(
            url_suffix,
            metadata['description'],
            metadata['banner_image'],
            metadata['author'],
            metadata['status'],
            metadata['views'],
            metadata['genres']
        )
        print(f"      Author: {metadata['author']}")
        print(f"      Status: {metadata['status']}")
        print(f"      Genres: {metadata['genres'][:50]}...")
    else:
        print("      Failed to get metadata")
    
    time.sleep(0.5)
    
    # 2. Get all chapter links
    print("\n   [Step 2] Fetching chapter list...")
    all_links = get_all_chapters_link(url_suffix)
    
    if not all_links:
        print("      No chapters found")
        return
    
    print(f"      Found {len(all_links)} chapters")
    
    # Reverse to process from oldest to newest
    all_links.reverse()
    
    # 3. Process each chapter
    print("\n   [Step 3] Processing chapters...")
    new_chapters = 0
    skipped = 0
    
    for link in all_links:
        # Extract chapter number
        try:
            # Try different patterns
            match = re.search(r"chapter-(\d+(?:\.\d+)?)", link)
            if match:
                chap_num = float(match.group(1))
            else:
                continue
        except (IndexError, ValueError):
            continue

        # Check if chapter already exists with images
        if db_chapter_exists(url_suffix, chap_num):
            skipped += 1
            continue
        
        print(f"      Chapter {chap_num}...", end=" ")
        
        # Insert chapter
        chap_id = db_insert_chapter(
            url_suffix, 
            f"Chapter {int(chap_num) if chap_num == int(chap_num) else chap_num}", 
            chap_num, 
            "2024-01-01"
        )
        
        if chap_id:
            # Get image URLs
            image_urls = get_chapter_image_urls(link)
            
            if image_urls:
                if db_insert_chapter_images(chap_id, image_urls):
                    print(f"{len(image_urls)} images")
                    new_chapters += 1
                else:
                    print("already exists")
                    skipped += 1
            else:
                print("no images found")
        
        # Rate limiting
        time.sleep(0.3)
    
    print(f"\n   Summary: {new_chapters} new chapters, {skipped} skipped")

def main():
    print("\n" + "="*60)
    print("FULL MANGA SCRAPER")
    print("Metadata + All Chapters")
    print("="*60)
    
    rows = db_get_all_manga()
    print(f"\nFound {len(rows)} manga in database\n")
    
    for title, url_suffix, _ in rows:
        process_manga(title, url_suffix)
    
    # Final summary
    print("\n" + "="*60)
    print("SCRAPING COMPLETE!")
    print("="*60)
    
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(*) FROM manga_details")
    details_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM chapters")
    chap_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM chapter_images")
    img_count = cur.fetchone()[0]
    
    con.close()
    
    print(f"\nDatabase summary:")
    print(f"  - {details_count} manga with metadata")
    print(f"  - {chap_count} total chapters")
    print(f"  - {img_count} total image URLs")

if __name__ == '__main__':
    main()
