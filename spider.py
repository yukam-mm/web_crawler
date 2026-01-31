# This spider will work on simple static websites, but modern
# dynamic or protected websites will require significant modifications

import sqlite3
import ssl
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Connect to database
conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

# Create tables
cur.execute('''CREATE TABLE IF NOT EXISTS Pages
    (id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT,
     error INTEGER, old_rank REAL, new_rank REAL)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Links
    (from_id INTEGER, to_id INTEGER, UNIQUE(from_id, to_id))''')

cur.execute('''CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)''')

# Check if crawl already in progress
cur.execute('SELECT id,url FROM Pages WHERE html IS NULL and error IS NULL ORDER BY RANDOM() LIMIT 1')
row = cur.fetchone()
if row is not None:
    print("Restarting existing crawl. Remove spider.sqlite to start fresh.")
else:
    starturl = input('Enter web url or enter: ').strip()
    if len(starturl) < 1:
        print("No URL entered, exiting.")
        exit()
    if starturl.endswith('/'):
        starturl = starturl[:-1]
    web = starturl
    if starturl.endswith('.htm') or starturl.endswith('.html'):
        web = starturl[:starturl.rfind('/')]
    cur.execute('INSERT OR IGNORE INTO Webs (url) VALUES (?)', (web,))
    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES (?, NULL, 1.0)', (starturl,))
    conn.commit()

# Load all webs
cur.execute('SELECT url FROM Webs')
webs = [str(row[0]) for row in cur]
print(webs)

many = 0
while True:
    if many < 1:
        sval = input('How many pages: ').strip()
        if len(sval) < 1:
            break
        many = int(sval)
    many -= 1

    cur.execute('SELECT id,url FROM Pages WHERE html IS NULL and error IS NULL ORDER BY RANDOM() LIMIT 1')
    row = cur.fetchone()
    if row is None:
        print('No unretrieved HTML pages found')
        break

    fromid, url = row
    print(fromid, url, end=' ')

    # Remove old links from this page
    cur.execute('DELETE FROM Links WHERE from_id=?', (fromid,))

    try:
        # Use a browser-like User-Agent
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        document = urlopen(req, context=ctx)
        html_bytes = document.read()

        if document.getcode() != 200:
            print("Error on page:", document.getcode())
            cur.execute('UPDATE Pages SET error=? WHERE url=?', (document.getcode(), url))
            conn.commit()
            continue

        if 'text/html' != document.info().get_content_type():
            print("Ignore non text/html page")
            cur.execute('DELETE FROM Pages WHERE url=?', (url,))
            conn.commit()
            continue

        # Decode HTML safely
        html = html_bytes.decode('utf-8', errors='replace')
        print(f'({len(html)} chars)', end=' ')

        soup = BeautifulSoup(html, "html.parser")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user...")
        break
    except Exception as e:
        print("Unable to retrieve or parse page:", e)
        cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url,))
        conn.commit()
        continue

    # Store HTML in DB
    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES (?, NULL, 1.0)', (url,))
    cur.execute('UPDATE Pages SET html=? WHERE url=?', (html, url))
    conn.commit()

    # Extract links
    tags = soup('a')
    count = 0
    for tag in tags:
        href = tag.get('href')
        if href is None:
            continue

        up = urlparse(href)
        if len(up.scheme) < 1:
            href = urljoin(url, href)
        if '#' in href:
            href = href[:href.find('#')]
        if href.endswith(('.png', '.jpg', '.gif')):
            continue
        if href.endswith('/'):
            href = href[:-1]
        if len(href) < 1:
            continue

        # Only follow links within allowed webs
        if not any(href.startswith(web) for web in webs):
            continue

        cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES (?, NULL, 1.0)', (href,))
        count += 1
        conn.commit()

        cur.execute('SELECT id FROM Pages WHERE url=? LIMIT 1', (href,))
        row = cur.fetchone()
        if row is None:
            continue
        toid = row[0]
        cur.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES (?, ?)', (fromid, toid))

    print(count)

cur.close()
conn.close()
