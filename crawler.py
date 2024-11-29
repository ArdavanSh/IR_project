import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urljoin, urlparse
from collections import deque

def crawlerThread(frontier, collection, num_targets):
    visited = set()
    target_pages_collected = 0
    allowed_domain = 'www.cpp.edu'

   
    non_html_extensions = (
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff',
        '.mp3', '.mp4', '.avi', '.mov', '.pdf', '.doc', '.docx',
        '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.tar',
        '.gz', '.css', '.js', '.xml', '.ico', '.svg', '.txt'
    )

    while frontier and target_pages_collected < num_targets:
        url = frontier.popleft()
        if url in visited:
            continue
        visited.add(url)
        print(f"Visiting: {url}")
        try:
            
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req)
            content_type = response.headers.get('Content-Type')
            if content_type and 'text/html' not in content_type:
                continue
            html_bytes = response.read()
           
            soup = BeautifulSoup(html_bytes, 'html.parser')
            
            fac_info_div = soup.find('div', class_=lambda x: x and 'fac-info' in x)
            if fac_info_div:
                
                html_text = str(soup)
                
                collection.insert_one({'url': url, 'html': html_text})
                target_pages_collected += 1
                print(f"Target page found ({target_pages_collected}/{num_targets}): {url}")
                if target_pages_collected >= num_targets:
                    print("Collected required number of target pages. Stopping crawler.")
                    break
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                new_url = urljoin(url, href)
                
                parsed_url = urlparse(new_url)
                if parsed_url.scheme not in ['http', 'https']:
                    continue
                if parsed_url.netloc != allowed_domain:
                    continue
                
                if parsed_url.path.lower().endswith(non_html_extensions):
                    continue
                if new_url not in visited:
                    frontier.append(new_url)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

def main():
    frontier = deque()
    start_url = 'https://www.cpp.edu/sci/biological-sciences/index.shtml'
    frontier.append(start_url)
    
    client = MongoClient()
    db = client['Project']
    collection = db['pages']
    crawlerThread(frontier, collection, 10)

if __name__ == "__main__":
    main()
