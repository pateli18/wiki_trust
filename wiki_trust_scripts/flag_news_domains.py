import argparse
from db_helpers import execute_db_queries

def flag_news_domains(input_data_file):
	"""
	Flags those domains that are news sites in database

	Parameters
	----------
	input_data_file: str, filepath to .txt file with domain on each line
	"""
	news_domains = open(input_data_file)

	# reset all flags to false
	reset_query = """
	UPDATE domains
	SET news_site = FALSE
	"""
	domain_queries = [reset_query]

	# loop through each line and create a db query
	for domain in news_domains:
		domain_name = domain.strip()

		flag_query = f"""
		UPDATE domains
		SET news_site = TRUE
		WHERE domain = '{domain_name}'
		"""

		domain_queries.append(flag_query)

	execute_db_queries(domain_queries)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input_data_file', nargs = 1, type = str)
	args = parser.parse_args()
	params = {"input_data_file":args.input_data_file[0]}

	flag_news_domains(**params)

