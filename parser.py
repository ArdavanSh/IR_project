import pymongo
from bs4 import BeautifulSoup
import re

def parse_and_store(pages_collection, faculty_collection):
    
    documents = pages_collection.find()
    for doc in documents:
        url = doc['url']
        html_text = doc['html']
        soup = BeautifulSoup(html_text, 'html.parser')

        
        name = None
        name_tag = soup.find('h1')
        if name_tag:
            name = name_tag.get_text(strip=True)
            print(f"Extracted Name: {name}")
        else:
            print(f"No name found in {url}")
            continue  

        
        main_body_text = ''
        main_body = soup.find('div', id='main-body')
        if main_body:
            
            main_body_text = main_body.get_text(separator='\n', strip=True)
            print(f"Extracted Main Body Text from {url}")
        else:
            print(f"No main body found in {url}")

       
        aside_text = ''
        asides = soup.select('main aside')
        for aside in asides:
            aria_label = aside.get('aria-label', 'Unknown Section')
            section_text = aside.get_text(separator='\n', strip=True)
            aside_text += f"\n[Section: {aria_label}]\n{section_text}\n"
            print(f"Extracted text from aside section: {aria_label}")

        
        combined_text = f"{main_body_text}\n\n{aside_text}".strip()

        
        faculty_data = {
            'name': name,
            'text': combined_text,
            'url': url
        }

        
        faculty_collection.insert_one(faculty_data)
        print(f"Data inserted into 'faculty' collection for {name}")

def main():
    
    client = pymongo.MongoClient()
    db = client['Project']
    pages_collection = db['pages']
    faculty_collection = db['faculty']  
    parse_and_store(pages_collection, faculty_collection)

if __name__ == "__main__":
    main()
