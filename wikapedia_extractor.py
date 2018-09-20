from html import unescape
from urllib import request
import threading

def write_citations_to_file(citations, filename):
    with open("citations.txt", "a", -1, "utf-8") as file:
        for citation in citations:
            file.write(citation + "\n")

def extract_elements(source_code, tag):
    element_count = source_code.count(tag)
    left_index, right_index = 0, 0
    elements = []
    for x in range(0, element_count):
        left_index = source_code.find(tag, right_index)
        right_index = source_code.find("}}", left_index) + len ("}}")
        raw_element = source_code[left_index : right_index]
        element = raw_element.replace("\n", "")
        elements.append(element)
    return elements

def extract_citations(source_code):
    primary_citations = extract_elements(source_code, "{{cite")
    secondary_citations = extract_elements(source_code, "{{Cite")
    citations = primary_citations + secondary_citations
    return citations

def retrieve_byte_code(link):
    website = request.urlopen(link)
    byte_code = website.read()
    return byte_code

def retrieve_source_code(link):
    byte_code = retrieve_byte_code(link)
    source_code = byte_code.decode("utf-8", "ignore")
    source_code = unescape(source_code)
    return source_code

def retrieve_citations(link):
    source_code = retrieve_source_code(link)
    citations = extract_citaitons(source_code)
    return citations

def create_citation_list(links):
    for link in links:
        citations = retrieve_citations(link)
        write_citations_to_file(citations)

def retrieve_links_from_file(filename):
    with open(filename, "r") as file:
        text = file.read()
        links = text.splitlines()
    return links

def retrieve_links_for_thread(thread_number, number_of_threads):
    links = retrieve_links_from_file("links.txt")
    number_of_links = len(links)
    links_per_thread = number_of_links // number_of_threads
    start_index = thread_number * links_per_thread
    return links[start_index : start_index + links_per_thread]

def build_threads(number_of_threads):
    threads = []
    for thread_number in range(0, number_of_threads):
        links = retrieve_links_for_thread(thread_number, number_of_threads)
        thread = threading.Thread(target = create_citation_list, args = (links, ))
        threads.append(thread)
    return threads

if __name__ == "__main__":
	threads = build_threads(10)
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()
