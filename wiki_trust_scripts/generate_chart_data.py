from calculate_metric import get_metric_data, get_lin_model_residual, get_rank
from db_helpers import get_db_connection
import json, argparse
import pandas as pd

def get_chart_data():
	"""
	Retrieves, formats, and calculates trust factor and trust factor rank on db data for use in charts. 
	Data is filtered for only news sites

	Returns
	-------
	df: Pandas DataFrame, contains relevant metric data for news sites
	"""

	df, _ = get_metric_data()
	df["trust_factor"] = get_lin_model_residual(df["alexa_linksincount"], df["link_count"])
	df = df[df["news_site"] == True]
	df = get_rank(df, ['trust_factor'], [False])

	return df

def get_connections_data():
	"""
	Retreives data from db that can be used to calculate connections between domains

	Returns
	-------
	df: Pandas DataFrame, contains page id and domains cited on that page
	"""

	connection = get_db_connection()
	query = """
	SELECT citations.page_id, news_domains.domain FROM citations LEFT JOIN 
		(SELECT link_domain_map.processed_link, link_domain_map.domain FROM link_domain_map 
		JOIN domains ON link_domain_map.domain = domains.domain WHERE domains.news_site = TRUE) news_domains 
	ON citations.processed_link = news_domains.processed_link WHERE NOT news_domains.processed_link IS NULL
	"""
	df = pd.read_sql(query, connection)
	return df

def generate_nodes(df):
	"""
	Creates json of nodes for force directed graph

	Parameters
	----------
	df: Pandas DataFrame, contains relevant metric data for news sites

	Returns
	-------
	nodes: arr of dict, list of dictionaries with relevant node data 
	"""
	data_labels = df.columns
	nodes = []

	# iterrate over each row in df
	for _, row in df.iterrows():
		row_data = {label:row[label] for label in data_labels}
		nodes.append(row_data)

	return nodes

def generate_link_counts(pair_join = '[uniquejoin]'):
	"""
	Counts the number of times two domains appear together on the same page

	Parameters
	----------
	pair_join: str, random str to allow for splitting in generate_links function

	Returns
	-------
	link_counts: dict, dictionary with domain pairs and the number of times they occur
	"""
	df = get_connections_data()
	pages = df.page_id.unique()
	link_counts = {}

	for count, page in enumerate(pages):

		domains = sorted(df[df['page_id'] == page]['domain'].unique())
		
		for i in range(0, len(domains) - 1):

			for j in range(i + 1, len(domains) - 1):

				connection = f"{domains[i]}{pair_join}{domains[j]}"

				if connection in link_counts:
					link_counts[connection] += 1
				else:
					link_counts[connection] = 1

		if count % 1000 == 0:
			print(f'{count} out of {len(pages)} pages complete...')

	return link_counts

def generate_links(link_counts, pair_join = '[uniquejoin]'):
	"""
	Creates a json of domain links for use in force directed graph

	Parameters
	----------
	link_counts: dict, dictionary with domain pairs and the number of times they occur
	pair_join: str, random str to allow for splitting in generate_links function

	Returns
	-------
	links: arr of dict, list of dictionaries with relevant links data
	"""
	links = []        
	for link in link_counts:
		domains = link.split(pair_join)
		links.append({'source':domains[0], 'target':domains[1], 'value':link_counts[link]})

	return links

def generate_force_directed_graph_json(output_folder_path):
	"""
	Creates csv for domain metrics and json for force directed graph showing connections between news sites.
	Both data sets used in site

	Parameters
	----------
	output_folder_path: str, folder path to save data files
	"""
	df = get_chart_data()

	# save metric data for non connections charts
	df.to_csv(f"{output_folder_path}domain_metrics.csv", index = False)

	# create connections chart json data
	nodes = generate_nodes(df)
	link_counts = generate_link_counts()
	links = generate_links(link_counts)

	chart_data = {"nodes":nodes, "links":links}

	json.dump(chart_data, open(f"{output_folder_path}domain_connections.json", 'w'))


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--output_folder_path', nargs = '?', type = str, default = 'docs/data/')

	args = parser.parse_args()
	params = {"output_folder_path":args.output_folder_path}

	generate_force_directed_graph_json(**params)