import requests
from bs4 import BeautifulSoup
from db_helpers import push_records_to_db, get_pages_to_scrape

def process_citation_item(citation):
	"""
	Extracts links and text from individual wikipedia citation item

	Parameters
	----------
	citation: BeautifulSoup object, one of the li items in wikipedia citation section

	Returns
	-------
	citation_text: str, text of citation
	links: str array, array of links in citation
	"""
	links = [link["href"] for link in citation.find_all("a")]
	citation_text = citation.text

	return citation_text, links


def process_citations_html(page):
	"""
	Takes raw html of a wikipedia page and returns list of citations

	Parameters
	----------
	page: html, wiki page from which to scrape citations

	Returns
	-------
	citation_data: [(str, [str,...]),..], each item in the list has the text of a citation and all the links in that citation
	"""

	# extract citation items from html of page
	soup = BeautifulSoup(page.text, "html.parser")
	citation_section = soup.find("ol", class_="references")
	citations = citation_section.find_all("li")
	
	# loop through each citation item, extract relevant info, add to data list
	citation_data = []
	for citation in citations:

		citation_text, links = process_citation_item(citation)
		citation_data.append((citation_text, links))
		
	return citation_data

def scrape_page(page_id):
	"""
	Scrapes wikipedia page for citations and adds to database

	Parameters
	----------
	page_id: str, name of wikipedia page to add to base url
	"""

	# get and process wiki page html
	url = f"https://en.wikipedia.org/wiki/{page_id}"
	page_html = requests.get(url)
	citation_data = process_citations_html(page_html)

	# loop through each link in each citation and add to db
	citation_db_data = []
	for citation_num, citation in enumerate(citation_data):
		citation_text, links = citation
		for link in links:
			link_data = {"page_id":page_id, "citation_num":citation_num, 
			"citation_text":citation_text, "link":link}
			citation_db_data.append(link_data)

	push_records_to_db("citations", citation_db_data)

def scrape_all_pages():
	"""
	Scrapes all outstanding pages
	"""

	pages_to_scrape = get_pages_to_scrape()

	for counter, page in enumerate(pages_to_scrape):
		scrape_page(page)

		# progress print out
		if counter % 50 == 0:
			print(f"{counter} out of {len(pages_to_scrape)} complete...")


if __name__ == "__main__":
	scrape_all_pages()







