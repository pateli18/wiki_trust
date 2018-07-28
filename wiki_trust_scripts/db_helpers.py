import mysql.connector, os, argparse
import pandas as pd

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
		'host': os.environ["DBHOST"],
		'auth_plugin': 'caching_sha2_password'
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
	connection.commit()
	connection.close()

def push_records_to_db(table_name, data_dicts):
	"""
	Inserts records into selected db table

	Parameters
	----------
	table_name: str, name of table in the db to insert new record into
	data_dicts: dict array, array of dicts with keys as column names and values as the record's value
	"""
	connection = get_db_connection()
	cursor = connection.cursor()

	# loop through each data_dictionary, create a query and execute it
	for data_dict in data_dicts:

		placeholder = ", ".join(["%s"] * len(data_dict))
		query = "insert into `{table}` ({columns}) values ({values});".format(table=table_name, columns=",".join(data_dict.keys()), values=placeholder)
		try:
			cursor.execute(query, list(data_dict.values()))
		except mysql.connector.errors.DatabaseError as err:
			if err.errno == 1366:
				data_dict["citation_text"] = ""
				query = "insert into `{table}` ({columns}) values ({values});".format(table=table_name, columns=",".join(data_dict.keys()), values=placeholder)
				cursor.execute(query, list(data_dict.values()))
				
	cursor.close()
	connection.commit()
	connection.close()

def update_domain_record(domain, alexa_rank, alexa_linksincount):
	"""
	Updates domain record in db with alexa data

	Parameters
	----------
	domain: str, domain name
	alexa_rank: int, domain's alexa rank
	alexa_linksincount: int, number of sites linking into domain
	"""

	query = f"""
	UPDATE domains 
	SET alexa_rank={alexa_rank}, alexa_linksincount={alexa_linksincount} 
	WHERE domain='{domain}'
	"""

	execute_db_queries([query])

def get_unique_set(table_name, column_name):
	"""
	Function that gets all unique values in a specific table column

	Parameters
	----------
	table_name: str, name of table in db
	column_name: str, name of column in table

	Returns
	-------
	values: set, set of values in chosen column
	"""

	query = f"""
	SELECT {column_name} FROM {table_name}
	"""

	connection = get_db_connection()
	cursor = connection.cursor()
	cursor.execute(query)

	values_raw = []
	for item in cursor:
		values_raw.append(item[0])

	cursor.close()
	connection.close()

	values = set(values_raw)

	return values

def get_latest_page_id():
	"""
	Retreives the id of the most recent page retrieved

	Returns
	-------
	value: str, id of page
	"""

	query = """
	SELECT id FROM pages 
	WHERE note IS NULL AND id NOT LIKE '%\%%' 
	ORDER BY name DESC 
	LIMIT 1
	"""

	connection = get_db_connection()
	cursor = connection.cursor()
	cursor.execute(query)

	values = []
	for item in cursor:
		values.append(item[0])

	cursor.close()
	connection.close()

	value = values[0]

	return value


def get_list_from_custom_query(query, column_num):
	"""
	Function that returns list of values based on custom SQL query

	Parameters
	----------
	query: str, SQL query to execute on DB
	column_num: num of column to get value from

	Returns
	-------
	values: array, array of values from SQL column
	"""

	connection = get_db_connection()
	cursor = connection.cursor()
	cursor.execute(query)

	values = []
	for item in cursor:
		values.append(item[column_num])

	cursor.close()
	connection.close()

	return values

def download_tables(folder_path):
	"""
	Downloads all tables from the db

	Parameters
	----------
	folder_path: str, folder to save all tables
	"""
	connection = get_db_connection()
	tables = ["pages", "citations", "domains", "link_domain_map", "metrics"]
	for table in tables:
		print(f"Downloading {table}...")
		df = pd.read_sql(f"SELECT * FROM {table}", connection)
		df.to_csv(f"{folder_path}{table}.csv", index = False)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--folder_path', nargs = 1, type = str)
	args = parser.parse_args()
	params = {"folder_path":args.folder_path[0]}

	download_tables(**params)
