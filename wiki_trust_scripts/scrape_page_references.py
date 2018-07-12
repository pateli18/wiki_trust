import requests, argparse, re
from bs4 import BeautifulSoup
from db_helpers import push_records_to_db, get_pages_to_scrape
from multiprocessing import Pool

def extract_archive_site(link_raw):
	"""
	Extracts base url from those sites that have been archived

	Parameters
	----------
	link_raw: str, link directly from wikipedia citation

	Returns
	-------
	link: str, non-archive-site link
	"""
	if "//web.archive.org" in link_raw or "//archive.is" in link_raw or "//www.webcitation.org" in link_raw:
		link_index = link_raw.find("http", 5)
	else:
		link_index = 0

	link = link_raw[link_index:]
	return link

def standardize_wiki_url(processed_link):
	"""
	Standardizes the url for wikipedia for a post-processed link

	Parameters
	----------
	processed_link: str, wiki link that has been processed by the extract_base_url function

	Returns
	-------
	standardized_link: str, link that has been standardized
	"""
	if processed_link == "wiki" or processed_link == "w":
		standardized_link = "www.wikipedia.org"
	else:
		standardized_link = processed_link

	return standardized_link

def extract_base_url(link_raw):
	"""
	Processes links from wikipedia citations to get base urls

	Parameters
	----------
	link_raw: str, link directly from wikipedia citation

	Returns
	-------
	processed_link: str, base url (basically only the subdomain and domain)
	"""
	try:
		processed_link = re.search('^((http[s]?|ftp):\/)?\/?\/?([^\/\s]+)', link_raw).group(3)
	except AttributeError:
		processed_link = ""

	return processed_link

def process_link(link_raw):
	"""
	Processes citation link from wikipedia through various steps

	Parameters
	----------
	link_raw: str, link directly from wikipedia citation

	Returns
	-------
	standardized_link: str
	"""
	non_archive_link = extract_archive_site(link_raw)
	processed_link = extract_base_url(non_archive_link)
	standardized_link = standardize_wiki_url(processed_link)
	return standardized_link

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

	links = [link["href"] for link in citation.find_all("a") if link.has_attr("href")]
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
	citation_section = soup.find("div", class_="references-column-count") if citation_section is None else citation_section
	citation_section = soup.find("div", class_="references-column-width") if citation_section is None else citation_section
	
	if citation_section is None:
		citations = soup.find_all("cite")
	else:
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
			processed_link = process_link(link)
			link_data = {"page_id":page_id, "citation_num":citation_num, 
			"citation_text":citation_text, "link":link, "processed_link":processed_link}
			citation_db_data.append(link_data)

	push_records_to_db("citations", citation_db_data)

def scrape_all_pages(processes = 1):
	"""
	Scrapes all outstanding pages
	"""

	pages_to_scrape = get_pages_to_scrape()
	print(f"Scraping {len(pages_to_scrape)} pages...")

	pool = Pool(processes)
	pool.map(scrape_page, pages_to_scrape)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--processes', nargs = '?', type = int, default = 1)

	args = parser.parse_args()
	params = {}
	params["processes"] = args.processes

	scrape_all_pages(**params)







