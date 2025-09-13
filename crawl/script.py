import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

# Define categories with their URLs
categories = {
    "Food Pantry": [
        "https://www.depts.ttu.edu/raiderrelief/foodpantry.php",
        # add more URLs here if needed
    ],
    "Category 2": [
        "https://example.com/page2",
        # add more URLs
    ]
}

resources = {}

def crawl(url):
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        return None  # skip if the page can't be reached

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        title = soup.title.string if soup.title else "No Title"
        return {
            "title": title,
            "text": text,
            "url": url
        }
    return None

# Crawl each category
for category_name, urls in categories.items():
    resources[category_name] = []
    for url in urls:
        page_data = crawl(url)
        if page_data:
            resources[category_name].append(page_data)

# Save JSON
with open("crawl/ttu_resources.json", "w") as f:
    json.dump(resources, f, indent=2)

print("Crawled pages organized by category and saved to ttu_resources.json")
