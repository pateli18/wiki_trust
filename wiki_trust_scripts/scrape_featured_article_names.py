import requests
from bs4 import BeautifulSoup
from db_helpers import push_records_to_db, get_unique_set

def scrape_featured_article_list():
	"""
	Scrapes all page names from wikipedias featured pages list
	"""

	# get the article section soup of the page
	all_page_ids = get_unique_set("pages", "id")

	url = "https://en.wikipedia.org/wiki/Wikipedia:Featured_articles"
	page_html = requests.get(url)
	soup = BeautifulSoup(page_html.text, "html.parser")
	article_section = soup.find_all("div", class_="hlist")[-1].find_all("li")

	pages_db_data = []
	# loop through each page in the section and add it to an array which is then pushed to the db
	for page in article_section:
		page_link = page.find("a")
		page_id = page_link["href"].replace("/wiki/", "")

		# check if page id already stored
		if page_id not in all_page_ids:
			page_data = {"id":page_id, "name":page_link["title"],
			"language":"english"}
			pages_db_data.append(page_data)

	push_records_to_db("pages", pages_db_data)

if __name__ == "__main__":
	scrape_featured_article_list()
	 