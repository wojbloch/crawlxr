import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import csv
import atexit
import re

def is_valid_url(url):
    return urlparse(url).scheme in ("http", "https")

def is_same_domain(url):
    return urlparse(url).netloc.endswith(gutted_url or gutted)

def target_str(url, search_string):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"failed to fetch content from {url}.")
        return False
    html_content = response.text
    return search_string in html_content

def fetch_urls(url, search_string, depth=1, max_depth=3, visited=None, results_file=None):
    if visited is None:
        visited = set()
    if depth > max_depth:
        return []
    if url in visited:
        return []
    visited.add(url)

    global derp
    if derp == 1:
        print(f"- crawling {url}, depth: {depth}")
        derp += 1
    else:
        print(f"+ crawling {url}, depth: {depth}")
        derp -= 1

    if not is_valid_url(url):
        print(f"invalid url schema for {url} ... ")
        return []

    if target_str(url, search_string):
        print(f"found '{search_string}' in {url}")
        if results_file:
            with open(results_file, "a", newline="") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([url, search_string])

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"failed to fetch content from {url}.")
            return []

        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        extracted_urls = []
        for tag in soup.find_all("a"):
            link = tag.get("href")
            if link:
                absolute_url = urljoin(url, link)
                if is_valid_url(absolute_url) and is_same_domain(url):
                    extracted_urls.append(absolute_url)

        for extracted_url in extracted_urls:
            extracted_urls.extend(fetch_urls(extracted_url, search_string, depth + 1, max_depth, visited, results_file))
        return extracted_urls

    except requests.exceptions.RequestException as e:
        print(f"failed to fetch content {url}: {e}")
        return []

def save_results_on_exit(csvfile, visited):
    print("saving results before exit...")
    with open(csvfile, "a", newline="") as file:
        csvwriter = csv.writer(file)
        for url in visited:
            csvwriter.writerow([url, ""])

target_url = input(str(f"set target: "))
gutted_url = re.sub(r'https\S+', '', target_url)
gutted = re.sub(r'http\S+', '', target_url)
search_string = input(str(f"what should I look for, master: "))
max_depth = 3
derp = 1
results_file = "bigdata.csv"

atexit.register(save_results_on_exit, results_file, visited=set())

with open(results_file, "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["url", "", "target value"])

urls = fetch_urls(target_url, search_string, max_depth=max_depth, results_file=results_file)
