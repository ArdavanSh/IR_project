import pymongo
from bs4 import BeautifulSoup
import re

def parse_and_store(pages_collection, faculty_collection):
    # Fetch all documents from the pages collection
    documents = pages_collection.find()
    for doc in documents:
        url = doc['url']
        html_text = doc['html']
        soup = BeautifulSoup(html_text, 'html.parser')

        # Extract the name (assuming it's in the <h1> tag)
        name = None
        name_tag = soup.find('h1')
        if name_tag:
            name = name_tag.get_text(strip=True)
            print(f"Extracted Name: {name}")
        else:
            print(f"No name found in {url}")
            continue  # Skip if name is not found

        # Extract the main body text
        main_body_text = ''
        main_body = soup.find('div', id='main-body')
        if main_body:
            # Extract main text content
            main_body_text = main_body.get_text(separator='\n', strip=True)
            print(f"Extracted Main Body Text from {url}")
        else:
            print(f"No main body found in {url}")

        # Extract additional text from aside sections inside main
        aside_text = ''
        asides = soup.select('main aside')
        for aside in asides:
            aria_label = aside.get('aria-label', 'Unknown Section')
            section_text = aside.get_text(separator='\n', strip=True)
            aside_text += f"\n[Section: {aria_label}]\n{section_text}\n"
            print(f"Extracted text from aside section: {aria_label}")

        # Combine main body and aside text
        combined_text = f"{main_body_text}\n\n{aside_text}".strip()

        # Prepare the data to be inserted into the faculty collection
        faculty_data = {
            'name': name,
            'text': combined_text,
            'url': url
        }

        # Insert the data into the faculty collection
        faculty_collection.insert_one(faculty_data)
        print(f"Data inserted into 'faculty' collection for {name}")

def main():
    # Connect to MongoDB
    client = pymongo.MongoClient()
    db = client['Project']
    pages_collection = db['pages']
    faculty_collection = db['faculty']  # New collection for faculty data
    parse_and_store(pages_collection, faculty_collection)

if __name__ == "__main__":
    main()
