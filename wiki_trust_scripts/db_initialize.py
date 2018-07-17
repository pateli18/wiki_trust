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
		processed_link VARCHAR(400) NOT NULL,
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
		alexa_rank INT,
		alexa_linksincount INT,
		news_site BOOLEAN,
		PRIMARY KEY (domain)
	)
	"""

	execute_db_queries([query])

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
		#FOREIGN KEY (processed_link)
		#	REFERENCES citations(processed_link)
		#	ON DELETE CASCADE,
		FOREIGN KEY (domain)
			REFERENCES domains(domain)
			ON DELETE CASCADE
	)
	"""

	execute_db_queries([query])

def create_metrics_table():
	"""
	Creates the metrics tabls
	"""

	# drop metrics if exists
	print("Dropping metrics table...")
	drop_query = """
	DROP TABLE IF EXISTS metrics
	"""

	# Creates metrics table
	print("Creating metrics table...")
	create_query = """
	CREATE TABLE metrics (
		SELECT domains.*, link_count FROM 
			(SELECT domain, SUM(num_links) AS link_count FROM 
				(SELECT processed_link, COUNT(*) AS num_links FROM citations 
				WHERE processed_link NOT LIKE '%#%' GROUP BY 1) AS top_links 
			INNER JOIN link_domain_map ON top_links.processed_link = link_domain_map.processed_link 
			GROUP BY 1) AS top_domains 
		INNER JOIN domains ON top_domains.domain = domains.domain ORDER BY link_count DESC
	)
	"""

	execute_db_queries([drop_query, create_query])

if __name__ == "__main__":
	create_db()
	create_pages_table()
	create_citations_table()
	create_domains_table()
	create_link_domain_map_table()
	create_metrics_table()


