#!/usr/bin/env python3
"""
Scrapes ONLY the description (summary) for all manga from their homepage.
Also gets the cover image URL from og:image meta tag.

Usage:
    python3 update_descriptions.py
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time

BASE_URL = "https://www.mgeko.cc"
DB_NAME = "mangadb.db"

def db_update_description(manga_url, description, banner_image=None):
    """Update only the description (and optionally banner) in manga_details."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        # Check if entry exists
        cur.execute("SELECT manga_url FROM manga_details WHERE manga_url=?", (manga_url,))
        exists = cur.fetchone()
        
        if exists:
            # Update existing
            if banner_image:
                cur.execute("""
                    UPDATE manga_details 
                    SET description=?, banner_image=?
                    WHERE manga_url=?
                """, (description, banner_image, manga_url))
            else:
                cur.execute("""
                    UPDATE manga_details 
                    SET description=?
                    WHERE manga_url=?
                """, (description, manga_url))
        else:
            # Insert new
            cur.execute("""
                INSERT INTO manga_details (manga_url, description, banner_image, author, status, views, genres)
                VALUES (?, ?, ?, 'Unknown', 'Unknown', '0', '')
            """, (manga_url, description, banner_image))
        
        con.commit()
        print(f"   [DB] Updated description")
    except Exception as e:
        print(f"   [DB Error]: {e}")
    finally:
        con.close()

def db_get_all_manga():
    """Get all manga from the database."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT title, url FROM manga")
    rows = cur.fetchall()
    con.close()
    return rows

def get_description_from_page(url_suffix):
    """
    Scrape the description from the manga homepage.
    
    The HTML structure is:
    <p class="description">
        {Title} is a Manga/Manhwa/Manhua... The Summary is
        <br><br>
        [ACTUAL SUMMARY STARTS HERE]
        ...
    </p>
    
    We extract everything AFTER "The Summary is" and the <br> tags.
    """
    full_url = BASE_URL + url_suffix
    print(f"   Fetching: {full_url}")
    
    try:
        r = requests.get(full_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        
        # Get og:image for banner
        banner_image = None
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            banner_image = og_image["content"]
            print(f"   Found banner: {banner_image[:50]}...")
        
        # Get description
        desc_tag = soup.find("p", class_="description")
        
        if not desc_tag:
            print("   No description tag found")
            return None, banner_image
        
        # Get the full text content
        full_text = desc_tag.get_text(separator="\n").strip()
        
        # The actual summary starts AFTER "The Summary is"
        # Split by this phrase and take the second part
        if "The Summary is" in full_text:
            parts = full_text.split("The Summary is", 1)
            if len(parts) > 1:
                summary = parts[1].strip()
            else:
                summary = full_text
        else:
            # Fallback: just use everything after first sentence
            summary = full_text
        
        # Clean up the summary
        # Remove leading/trailing whitespace and excessive newlines
        summary = re.sub(r'\n{3,}', '\n\n', summary)  # Max 2 newlines
        summary = summary.strip()
        
        # Limit length
        if len(summary) > 1500:
            summary = summary[:1500] + "..."
        
        print(f"   Summary preview: {summary[:100]}...")
        
        return summary, banner_image
        
    except Exception as e:
        print(f"   [Error] {e}")
        return None, None

def main():
    print("\n" + "="*60)
    print("DESCRIPTION UPDATER")
    print("="*60)
    
    rows = db_get_all_manga()
    print(f"\nFound {len(rows)} manga to update\n")
    
    updated = 0
    failed = 0
    
    for title, url_suffix in rows:
        print(f"\n[{title}]")
        
        description, banner = get_description_from_page(url_suffix)
        
        if description:
            db_update_description(url_suffix, description, banner)
            updated += 1
        else:
            print("   No description found, skipping")
            failed += 1
        
        # Be nice to the server
        time.sleep(0.5)
    
    print("\n" + "="*60)
    print(f"COMPLETE: {updated} updated, {failed} failed")
    print("="*60)
    
    # Show sample of what we got
    print("\nSample of updated descriptions:")
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT manga_url, description FROM manga_details LIMIT 2")
    for row in cur.fetchall():
        print(f"\n--- {row[0]} ---")
        print(row[1][:200] + "..." if len(row[1]) > 200 else row[1])
    con.close()

if __name__ == '__main__':
    main()
