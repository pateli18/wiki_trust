import mysql.connector, os

def get_db_connection(db_created = True):
	"""
	Creates python connector to database

	Parameters
	----------
	db_created: bool, indicates whether database has already been created

	Returns
	-------
	connection: mysql.connector object
	"""

	connection_params = {
		'user': os.environ["DBUSER"],
		'password': os.environ["DBPASSWORD"],
		'host': os.environ["DBHOST"]
	}

	if db_created:
		connection_params["database"] = os.environ["DBNAME"]

	connection = mysql.connector.connect(**connection_params)

	return connection

def execute_db_queries(queries, db_created = True):
	"""
	Execute a list of queries on database

	Parameters
	----------
	queries: str array, array of string queries to execute on database
	db_created: bool, indicates whether database has already been created
	"""

	connection = get_db_connection(db_created)
	cursor = connection.cursor()

	# loop through each query and execute
	for query in queries:
		cursor.execute(query)

	cursor.close()
	connection.close()

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


