from db_helpers import execute_db_queries

def create_db():
	"""
	Creates database if it does not already exist
	"""

	print("Creating database...")
	query = """
	CREATE DATABASE IF NOT EXISTS wiki_trust DEFAULT CHARACTER SET 'utf8mb4'
	"""

	execute_db_queries([query], False)

def create_pages_table():
	"""
	Creates the pages table
	"""

	print("Creating pages table...")
	query = """
	CREATE TABLE IF NOT EXISTS pages (
		id VARCHAR(400) NOT NULL,
		name TEXT NOT NULL,
		language TEXT NOT NULL,
		PRIMARY KEY (id)
	)
	"""

	execute_db_queries([query])

def create_citations_table():
	"""
	Creates the citations table
	"""

	print("Creating citations table...")
	query = """
	CREATE TABLE IF NOT EXISTS citations (
		id BIGINT NOT NULL AUTO_INCREMENT,
		page_id VARCHAR(400) NOT NULL,
		citation_num SMALLINT NOT NULL,
		citation_text TEXT,
		link TEXT NOT NULL,
		processed_link VARCHAR(400),
		PRIMARY KEY (id),
		FOREIGN KEY (page_id)
			REFERENCES pages(id)
        	ON DELETE CASCADE
	)
	"""

	execute_db_queries([query])

def create_domains_table():
	"""
	Creates the domains table
	"""

	print("Creating domains table...")
	query = """
	CREATE TABLE IF NOT EXISTS domains (
		domain VARCHAR(400) NOT NULL,
		rank INT,
		linksincount INT,
		news_site BOOLEAN
	)
	"""

def create_link_domain_map_table():
	"""
	Creates table that maps links to domains
	"""

	print("Creating link domain map table...")
	query = """
	CREATE TABLE IF NOT EXISTS link_domain_map (
		processed_link VARCHAR(400) NOT NULL,
		domain VARCHAR(400) NOT NULL,
		PRIMARY KEY (processed_link),
		FOREIGN KEY (processed_link)
			REFERENCES citations(processed_link)
			ON DELETE CASCADE,
		FOREIGN KEY (domain)
			REFERENCES domains(domain)
			ON DELETE CASCADE
	)
	"""

if __name__ == "__main__":
	create_db()
	create_pages_table()
	create_citations_table()
	create_domains_table()
	create_link_domain_map_table()


