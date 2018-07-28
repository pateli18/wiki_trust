import requests
from bs4 import BeautifulSoup
from db_helpers import push_records_to_db, get_unique_set, get_latest_page_id

def scrape_page(all_page_ids, soup):
	"""
	Scrapes pages with list of wikipedia pages and adds it to db

	Parameters
	----------
	all_page_ids: set, all page ids already in db
	soup: BeautifulSoup object, soup of page with list of pages
	"""

	pages_db_data = []

	# loop through each page link and add it to list
	for item in soup.find("div", class_="mw-allpages-body").find_all("li"):
		page_link = item.find("a")
		page_id = page_link["href"].replace("/wiki/", "")

		# check if page already in db
		if page_id not in all_page_ids:
			page_data = {"id":page_id, "name":page_link["title"], "language":"english"}
			pages_db_data.append(page_data)

	push_records_to_db("pages", pages_db_data)

def scrape_all_article_names():
	"""
	Scrapes all wikipedia article names
	"""

	# get page ids that have already been scraped
	all_page_ids = get_unique_set("pages", "id")

	additional_pages = True
	latest_page_id = get_latest_page_id()
	url = f"https://en.wikipedia.org/w/index.php?title=Special:AllPages&from={latest_page_id}"
	print(url)

	# keep scraping while there is a 'next' page
	while additional_pages:

		page_html = requests.get(url)
		soup = BeautifulSoup(page_html.text, "html.parser")
		scrape_page(all_page_ids, soup)

		url_suffix = soup.find("div", class_="mw-allpages-nav").find_all("a")[1]["href"]

		# check if next page
		if url_suffix:
			url = f"https://en.wikipedia.org{url_suffix}"
			print(url)
		else:
			additional_pages = False

if __name__ == "__main__":
	scrape_all_article_names()