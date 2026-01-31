# Website Link Structure Visualizer

This project is a **web crawler** that retrieves web pages, stores their links in a database, computes PageRank, and visualizes the network structure of the crawled website using a force-directed graph in the browser.

---

## Features

- Crawl a website and store pages and links in an SQLite database (`spider.sqlite`).  
- Compute PageRank for each page iteratively.  
- Export nodes and links to a JSON file (`spider.js`) for visualization.  
- Visualize the website link structure in a browser using `force.html` and D3.js.

---

## Requirements

- Python 3.8+  
- Libraries:
  - `beautifulsoup4`
  - `sqlite3` (standard library)
- Optional: `ssl` (standard library)
- **SQLite database**:  
  - SQLite comes pre-installed with most Python distributions.  
  - You should install the **SQLite Browser** to view and modify the databases from:  
    [http://sqlitebrowser.org/](http://sqlitebrowser.org/)

---

## Setup and Usage

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-directory>

2. Create a virtual enviroments (optional)
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows

4. Install dependencies:
   ```bash
   pip install beautifulsoup4

6. Run the spider to crawl a website:
   ```bash
   python3 spider.py

8. Compute PageRank
   ```bash
   python3 sprank.py

10. Generate JSON for visualization:
    ```bash
    python3 spjson.py
    
   - Enter how mnay nodes you want to include
   - This creates spider.js with the node and link data
     
11. Open the visualization
    ```bash
    open force.html 
   
---

## Notes
- Only pages within the specified domain are crawled.
- Pages with non-HTML content or errors are skipped.
- The visualization uses D3.js v2 to render the graph.

### Credits
This project is adapted from the Python for Everybody course by Dr. Charles Severance, using examples from the “Using Python to Access Web Data” chapter.
