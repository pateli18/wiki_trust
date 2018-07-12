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

def get_pages_to_scrape():
	"""
	Function that gets page ids that have not been scraped

	Returns
	-------
	page_ids: str array, array of page ids that have not been scraped
	"""

	query = """
	SELECT * FROM pages WHERE id NOT IN (SELECT page_id FROM citations)
	"""

	connection = get_db_connection()
	cursor = connection.cursor()
	cursor.execute(query)

	page_ids = []
	for page in cursor:
		page_ids.append(page)

	cursor.close()
	connection.close()

	return page_ids