# MICCAI 2024 Paper Scraper

## Project Description

MICCAI 2024 Paper Scraper is a Python-based Graphical User Interface (GUI) application designed to scrape, search, and download paper information from the MICCAI 2024 conference website. This tool allows users to easily browse conference papers, search for specific keywords, and download PDFs of interest.

## Key Features

1. Scrape paper data from the MICCAI 2024 website
2. Save and load scraped data locally
3. Search papers by title and authors
4. Highlight keywords in search results
5. Select and download multiple paper PDFs
6. Avoid duplicate downloads of existing PDF files

## Tech Stack

- Python 3.x
- PyQt5 for GUI
- BeautifulSoup for web parsing
- Requests for HTTP requests

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/seanxuu/MICCAI-downloader.git
   ```

2. Navigate to the project directory:
   ```
   cd MICCAI-downloader
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the program:
   ```
   python downloader.py
   ```

2. Click the "Fetch Data" button to retrieve the latest data from the MICCAI 2024 website.

3. Use the search boxes and checkboxes to search for specific papers.

4. Select papers of interest and click the "Download Selected PDFs" button to download PDF files.

## Notes

- Downloaded PDF files will be saved in the `downloaded_pdfs` directory.
- The program automatically skips files that have already been downloaded to avoid duplicates.
- Keywords in search results will be highlighted in red.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

