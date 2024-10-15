import sys
import os
import json
import requests
import re
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLineEdit, 
                             QLabel, QHBoxLayout, QMessageBox, QCheckBox, QGroupBox, QGridLayout, QScrollArea)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor

class DataFetchThread(QThread):
    finished = pyqtSignal(list)

    def run(self):
        url = "https://papers.miccai.org/miccai-2024/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        papers = []
        paper_elements = soup.find_all('div', class_='posts-list-item')

        for paper in paper_elements:
            title_element = paper.find('b')
            title = title_element.text.strip() if title_element else "No title"
            authors = [a.text.strip() for a in paper.find_all('a', href=lambda href: href and '/miccai-2024/tags#' in href)]
            pdf_link = paper.find('a', href=lambda href: href and href.endswith('.pdf'))['href']
            paper_info_link = paper.find('a', href=lambda href: href and href.startswith('/miccai-2024/'))['href']
            
            papers.append({
                'title': title,
                'authors': ', '.join(authors),
                'pdf_link': pdf_link,
                'paper_info_link': paper_info_link
            })

        self.finished.emit(papers)

class MICCAIPaperScraper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.papers = []
        self.filtered_papers = []
        self.selected_papers = []
        self.initUI()
        self.loadLocalData()

    def initUI(self):
        self.setWindowTitle('MICCAI 2024 Paper Scraper')
        self.setGeometry(100, 100, 1000, 800)

        main_layout = QVBoxLayout()

        # Fetch data button
        self.fetchButton = QPushButton('Fetch Data', self)
        self.fetchButton.clicked.connect(self.fetchData)
        main_layout.addWidget(self.fetchButton)

        # Search functionality
        search_group = QGroupBox("Search")
        search_layout = QGridLayout()

        self.searchInputs = []
        self.searchCheckboxes = []
        for i in range(3):
            input_layout = QHBoxLayout()
            input_layout.addWidget(QLabel(f'Keyword {i+1}:'))
            search_input = QLineEdit(self)
            input_layout.addWidget(search_input)
            self.searchInputs.append(search_input)
            search_layout.addLayout(input_layout, i, 0)

            checkbox_layout = QHBoxLayout()
            title_checkbox = QCheckBox('Title', self)
            authors_checkbox = QCheckBox('Authors', self)
            checkbox_layout.addWidget(title_checkbox)
            checkbox_layout.addWidget(authors_checkbox)
            self.searchCheckboxes.append((title_checkbox, authors_checkbox))
            search_layout.addLayout(checkbox_layout, i, 1)

        self.searchButton = QPushButton('Search', self)
        self.searchButton.clicked.connect(self.searchPapers)
        search_layout.addWidget(self.searchButton, 3, 0, 1, 2)

        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        # Download PDFs button
        self.downloadButton = QPushButton('Download Selected PDFs', self)
        self.downloadButton.clicked.connect(self.downloadPDFs)
        main_layout.addWidget(self.downloadButton)

        # Results area
        self.resultArea = QScrollArea()
        self.resultWidget = QWidget()
        self.resultLayout = QVBoxLayout(self.resultWidget)
        self.resultArea.setWidget(self.resultWidget)
        self.resultArea.setWidgetResizable(True)
        main_layout.addWidget(self.resultArea)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def loadLocalData(self):
        if os.path.exists('miccai_papers.json'):
            with open('miccai_papers.json', 'r') as f:
                self.papers = json.load(f)
            self.displayPapers(self.papers)

    def fetchData(self):
        self.fetchButton.setEnabled(False)
        self.fetchThread = DataFetchThread()
        self.fetchThread.finished.connect(self.onDataFetched)
        self.fetchThread.start()

    def onDataFetched(self, papers):
        self.papers = papers
        with open('miccai_papers.json', 'w') as f:
            json.dump(papers, f)
        self.displayPapers(self.papers)
        self.fetchButton.setEnabled(True)
        QMessageBox.information(self, "Success", "Data fetched and saved successfully!")

    def highlightKeywords(self, text, keywords):
        highlighted_text = text
        for keyword in keywords:
            highlighted_text = highlighted_text.replace(keyword, f"<span style='background-color: yellow;'>{keyword}</span>")
        return highlighted_text

    def displayPapers(self, papers_to_display):
        # Clear previous results
        for i in reversed(range(self.resultLayout.count())): 
            self.resultLayout.itemAt(i).widget().setParent(None)

        self.selected_papers = []
        keywords = [input.text().lower() for input in self.searchInputs if input.text()]

        for paper in papers_to_display:
            paper_widget = QWidget()
            paper_layout = QVBoxLayout(paper_widget)
            
            # Add checkbox for selection
            checkbox = QCheckBox(self)
            checkbox.stateChanged.connect(lambda state, p=paper: self.onPaperSelected(state, p))
            paper_layout.addWidget(checkbox)

            # Highlight keywords in title
            highlighted_title = self.highlightKeywords(paper['title'], keywords)
            title_label = QLabel(f"<b>{highlighted_title}</b>")
            title_label.setWordWrap(True)
            title_label.setTextFormat(Qt.RichText)
            paper_layout.addWidget(title_label)
            
            authors_label = QLabel(f"Authors: {paper['authors']}")
            authors_label.setWordWrap(True)
            paper_layout.addWidget(authors_label)
            
            pdf_link = QLabel(f"<a href='{paper['pdf_link']}'>PDF</a>")
            pdf_link.setOpenExternalLinks(True)
            paper_layout.addWidget(pdf_link)
            
            info_link = QLabel(f"<a href='{paper['paper_info_link']}'>More Info</a>")
            info_link.setOpenExternalLinks(True)
            paper_layout.addWidget(info_link)
            
            paper_layout.addWidget(QLabel(""))  # Spacer
            
            self.resultLayout.addWidget(paper_widget)

        self.resultWidget.setLayout(self.resultLayout)

    def onPaperSelected(self, state, paper):
        if state == Qt.Checked:
            self.selected_papers.append(paper)
        else:
            self.selected_papers.remove(paper)

    def searchPapers(self):
        keywords = [input.text().lower() for input in self.searchInputs if input.text()]
        if not keywords:
            self.displayPapers(self.papers)
            return

        self.filtered_papers = []
        for paper in self.papers:
            for i, keyword in enumerate(keywords):
                title_checked = self.searchCheckboxes[i][0].isChecked()
                authors_checked = self.searchCheckboxes[i][1].isChecked()
                
                if (title_checked and keyword in paper['title'].lower()) or \
                   (authors_checked and keyword in paper['authors'].lower()):
                    self.filtered_papers.append(paper)
                    break

        self.displayPapers(self.filtered_papers)

    def sanitize_filename(self, filename):
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Limit filename length (adjust as needed)
        return filename[:200]

    def downloadPDFs(self):
        if not self.selected_papers:
            QMessageBox.warning(self, "Warning", "No papers selected for download!")
            return

        download_dir = 'downloaded_pdfs'
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        for paper in self.selected_papers:
            pdf_url = paper['pdf_link']
            base_filename = self.sanitize_filename(paper['title']) + '.pdf'
            filename = os.path.join(download_dir, base_filename)
            
            # Check if file already exists and add number if necessary
            counter = 1
            while os.path.exists(filename):
                name, ext = os.path.splitext(base_filename)
                filename = os.path.join(download_dir, f"{name}_{counter}{ext}")
                counter += 1

            response = requests.get(pdf_url)
            with open(filename, 'wb') as f:
                f.write(response.content)

        QMessageBox.information(self, "Success", f"Selected PDFs downloaded to {download_dir}!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MICCAIPaperScraper()
    ex.show()
    sys.exit(app.exec_())
