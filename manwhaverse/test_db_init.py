
import sys

print("Checking imports...")
try:
    import telethon
    import bs4
    import requests
    import PIL
    import img2pdf
    import dotenv
    print("Imports OK")
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

import scraper
print("Running init_db...")
scraper.init_db()
print("Done.")
