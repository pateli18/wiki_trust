from db_helpers import execute_db_queries

def create_db():
	"""
	Creates database if it does not already exist
	"""

	print("Creating database...")
	query = """
	CREATE DATABASE IF NOT EXISTS wiki_trust DEFAULT CHARACTER SET 'utf8'
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
		PRIMARY KEY (id),
		FOREIGN KEY (page_id)
			REFERENCES pages(id)
        	ON DELETE CASCADE
	)
	"""

	execute_db_queries([query])

if __name__ == "__main__":
	create_db()
	create_pages_table()
	create_citations_table()


