import concurrent.futures
import json
from rake_nltk import Rake
import re
import fitz
from collections import Counter
from datetime import datetime
import os


def rakefn(text):
    r = Rake()
    r.extract_keywords_from_text(text) 
    ranked_phrases = r.get_ranked_phrases() 
    filtered_phrases = []
    for phrase in ranked_phrases: 
        if re.search(r'\b\w\b', phrase) : 
            continue
        if re.search(r'\b(\w)\1\b', phrase):
            continue
        if re.search(r'\d', phrase):
            continue
        if re.search(r'[*&!()?/>.<,:;\"\]\[\}\{]', phrase):
            continue
        
        for x in phrase.split():
            filtered_phrases.append(x)
    return filtered_phrases

def extractKw(file_path):
    text = ''
    try:
        with fitz.open(file_path) as pdf_document:
            num_pages = pdf_document.page_count
            for page_num in range(num_pages):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
    except Exception as e:
        print(f"Error opening or reading PDF file: {file_path} - {e}")
    return rakefn(text)


def process(pdf_part):  # processes a text file with file paths...
    result = {}
    with open(pdf_part, 'r') as file:
        file_paths = file.readlines()

    for path in file_paths:
        file_path = path.strip()
        result[file_path] = extractKw(file_path)
    return result

def find_highest_frequency(D):
    for key, values in D.items():
        value_counts = Counter(values)
        top_values = [value for value, _ in value_counts.most_common(90)]

        for i in range(len(top_values)):
            words = top_values[i].split()
            top_values.extend(words)
        D[key] = top_values
    return D

def search(query):
    query_key_words = rakefn(query)
    matching_keys = {}

    for i in query_key_words:
        for key2, vL in D.items():
            if i in vL:
                if key2 not in matching_keys:
                    matching_keys[key2] = 1
                else:
                    matching_keys[key2] += 1
                    
    sorted_keys = sorted(matching_keys.keys(), key=lambda key: matching_keys[key], reverse=True)

    s = [key.replace('\\', '/') for key in sorted_keys]
    return s




from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices, QIcon, QKeyEvent, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QCompleter
import subprocess

class CustomCompleter(QCompleter):
    def __init__(self, words, *args, **kwargs):
        super().__init__(words, *args, **kwargs)
        self.words = words

    def splitPath(self, path):
        text = self.widget().text()[:self.widget().cursorPosition()]
        last_word = text.split()[-1]
        return [word for word in self.words if word.startswith(last_word)]

class MyWidget(QWidget):
    def __init__(self,autocomplete_words):
        super().__init__()
        self.initUI(autocomplete_words)

    def initUI(self,autocomplete_words):
        self.setWindowTitle('Lexical Search Engine')
        # Set a custom icon for the application window
        self.setWindowIcon(QIcon('icon.png'))
        layout = QVBoxLayout()

        # Game Boy style Search input
        completer = CustomCompleter(autocomplete_words)
        self.search_input = QLineEdit()
        self.search_input.setCompleter(completer)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #b8eac8; /* Light green background */
                border: 2px solid #747573; /* Gray border */
                border-radius: 10px;
                padding: 8px;
                font-family: "Courier New", monospace;
                font-size: 16px;
                color: #000000; /* Black text */
            }
            QLineEdit:focus {
                border-color: #5e6060; /* Dark gray on focus */
            }
        """)

        layout.addWidget(self.search_input)
        search_button = QPushButton('Search')
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #747573; /* Gray button background */
                color: #ffffff; /* White text */
                padding: 6px 12px; /* Smaller padding for the button */
                border: none;
                border-radius: 10px;
                font-family: "Courier New", monospace;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #9c9e9e; /* Light gray on hover */
            }
            QPushButton:pressed {
                background-color: #5e6060; /* Dark gray on press */
            }
        """)
        search_button.clicked.connect(self.perform_search)
        layout.addWidget(search_button)

        # Game Boy style Result list
        self.result_list = QListWidget()
        self.result_list.setStyleSheet("""
            QListWidget {
                background-color: #f0fff4; /* Pale green background */
                border: 2px solid #747573; /* Gray border */
                border-radius: 10px;
                padding: 8px;
                font-family: "Courier New", monospace;
                font-size: 16px;
                color: #000000; /* Black text */
                outline: none;
            }
            QListWidget:item:selected {
                background-color: #747573; /* Grayish selection */
                color: #ffffff; /* White text on selection */
            }
        """)
        self.result_list.itemClicked.connect(self.open_file)  # Connect the itemClicked signal to the open_file slot
        layout.addWidget(self.result_list)
        self.setLayout(layout)

        # Set focus to the search input initially
        self.search_input.setFocus()

    def perform_search(self):
        query = self.search_input.text()
        folder_results = search(query)
        
        # Clear the result_list before updating with new results
        self.result_list.clear()
        # Add folder names to the result_list
        for folder in folder_results:
            self.result_list.addItem(folder)

        # Select the first item in the folder list
        if folder_results:
            self.result_list.setCurrentRow(0)

    def open_file(self, path):
        item = path.text()
        subprocess.Popen([item], shell=True)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Check if the search input has focus
            if self.search_input.hasFocus():
                self.perform_search()
            else:
                # Check if an item is selected in the result list
                selected_items = self.result_list.selectedItems()
                if selected_items:
                    selected_item = selected_items[0]
                    self.open_file(selected_item)
        elif event.key() == Qt.Key_Tab:
            # Switch focus between the search input and the result list using the Tab key
            if self.search_input.hasFocus():
                self.result_list.setFocus()
                self.result_list.setCurrentRow(0)
            else:
                self.search_input.setFocus()

        # Pass the event to the parent class for default handling
        super().keyPressEvent(event)

if __name__ == "__main__":
    start = datetime.now()
    flag = False
    if os.path.exists('all'):
        flag = True
        with open('output.json','r') as file:
            json_data = file.read()
        D = json.loads(json_data)
        end = datetime.now()
        td = (end - start).total_seconds() * 10**3
        print(f"The time of execution of above program is : {td:.03f}ms")        
        app = QApplication([])
        with open('autocomplete_words.json','r') as file:
            json_data = file.read()
        autocomplete_words = json.loads(json_data)
        widget = MyWidget(autocomplete_words)
        widget.show()
        app.exec_()
    else :
        subprocess.call(['search_pdf.bat'])
        pdf_parts = []
        for i in range(1, 10):
            if os.path.exists(f"all/pdf_part_{i}.txt"):
                pdf_parts.append(f"all/pdf_part_{i}.txt")  # 9 parts max
        D = {}
        with concurrent.futures.ProcessPoolExecutor() as executor: 
            results = list(executor.map(process, pdf_parts))

        for result in results:
            D.update(result)

        D = find_highest_frequency(D)
        
        with open('output.json', 'w') as json_file:
            json.dump(D, json_file)

        end = datetime.now()
        td = (end - start).total_seconds() * 10**3
        words = []
        for i in D.values():
            words += i
        word_frequency = Counter(words)
        autocomplete_words = [word for word, _ in word_frequency.most_common(100)]
        with open('autocomplete_words.json','w') as json_file:
            json.dump(autocomplete_words,json_file)
        print(f"The time of execution of above program is : {td:.03f}ms")
        app = QApplication([])
        widget = MyWidget(autocomplete_words)
        widget.show()
        app.exec_()