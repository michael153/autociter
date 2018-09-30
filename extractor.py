from html import unescape
from urllib import request
from os.path import splitext
import threading, sys, os

num_elements_collected = 0
num_links_visited = 0

def debug(elements, link):
    global num_elements_collected, num_links_visited
    num_elements_collected += len(elements)
    num_links_visited += 1
    print(num_elements_collected, '\t', num_links_visited, '\t', link)

def write_elements(elements):
    global_lock.acquire()
    with open(output_filename, "a", encoding="utf-8") as file:
        for element in elements:
            file.write(element + "\n")
    global_lock.release()

def extract_elements(text):
    left, right = 0, 0
    elements = []
    while start_tag in text[right:]:
        left = text.find(start_tag, right)
        right = text.find(end_tag, left) + len(end_tag)
        elements.append(text[left:right])
    return elements

def retrieve_byte_code(link):
    website = request.urlopen(link)
    byte_code = website.read()
    return byte_code

def retrieve_source_code(link):
    byte_code = retrieve_byte_code(link)
    source_code = byte_code.decode("utf-8", "replace")
    source_code = unescape(source_code)
    return source_code

def scrape_websites(links):
    for link in links:
        source_code = retrieve_source_code(link)
        elements = extract_elements(source_code)
        write_elements(elements)
        debug(elements, link)

def execute_threads(threads):
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

def retrieve_links(filename):
    with open(filename, "r") as file:
        text = file.read()
        links = text.splitlines()
    return links

def assign_links(thread_number, num_threads):
    links = retrieve_links(input_filename)
    links_per_thread = len(links) // num_threads
    start = thread_number * links_per_thread
    return links[start:start + links_per_thread]

def build_threads(num_threads):
    threads = []
    for thread_number in range(num_threads):
        links = assign_links(thread_number, num_threads)
        thread = threading.Thread(target=scrape_websites, args=(links, ))
        threads.append(thread)
    return threads

if __name__ == "__main__":
    assert len(sys.argv) == 5, "Four arguments expected."
    input_filename, output_filename = sys.argv[1], sys.argv[2]
    start_tag, end_tag = sys.argv[3], sys.argv[4]
    global_lock = threading.Lock()
    threads = build_threads(10)
    execute_threads(threads)
