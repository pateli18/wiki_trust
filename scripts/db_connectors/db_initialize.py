import mysql.connector, os

def get_connection_db():
	"""
	Creates python connector to database

	Returns
	-------
	connection: mysql.connector object
	"""

	connection = mysql.connector.connect(user = os.environ["DB_USERNAME"], 
		password = os.environ["DB_PASSWORD"], host = os.environ["DB_HOSTNAME"], 
		database = os.environ["DB_NAME"])

	return connection

def execute_query_db(queries):
	"""
	Execute a list of queries on database

	Parameters
	----------
	queries: str array, array of string queries to execute on database 
	"""

	connection = get_connection_db()
	cursor = connection.cursor()

	# loop through each query and execute
	for query in queries:
		cursor.execute(query)

	cursor.close()
	connection.close()

def create_db(db_name):
	"""
	Creates database if it does not already exist

	Parameters
	----------
	db_name: str, name of the database
	"""

	query = f"""
	CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET 'utf8'
	"""

	execute_queries([query])