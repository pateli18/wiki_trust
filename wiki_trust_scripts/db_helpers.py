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