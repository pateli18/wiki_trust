import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from db_helpers import get_db_connection
import argparse, sys

def print_results(df, metric, label):
	"""
	Prints dataframe results

	Parameters
	----------
	df: Pandas dataframe, dataframe to display results from - must have domain column
	metric: str, name of metric - must be column in dataframe
	label: str, title of results
	"""
	print(f"\n{label}\n------")

	for index, row in df.iterrows():
		print(f"{row['domain']}, {row[metric]}")

def results_quick_view(df_main, metric,results_num = 10):
	"""
	Displays top and bottom results for a selected metric

	Parameters
	----------
	df_main: Pandas dataframe, dataframe to display results from - must have domain column
	metric: str, name of metric - must be column in dataframe
	results_num: int, number of top and bottom results to display
	"""

	df = df_main[df_main["news_site"] == True].copy()
	df.sort_values(metric, inplace = True, ascending = False)
	display_columns = df[["domain", metric]]

	print_results(display_columns.head(results_num), metric, f"Top {results_num}")
	print_results(display_columns.tail(results_num), metric, f"Bottom {results_num}")

def get_rank(df, metrics, metric_sort_ascending):
	"""
	Gets ordinal rank for each domain in dataframe based on specific metric

	Parameters
	----------
	df: Pandas dataframe, dataframe to display results from - must have domain column
	metric: str array, array of metric_names - must be column in dataframe
	metric_sort_ascending: bool array, sort metric ascending

	Returns
	-------
	df: Pandas dataframe, dataframe to display results from - must have domain column
	"""
	for metric, metric_sort in zip(metrics, metric_sort_ascending):
		df = df.sort_values(metric, ascending = metric_sort)
		df = df.reset_index().drop("index", axis = 1).reset_index()
		df.rename(columns = {"index":f"{metric}_ordinal_rank"}, inplace = True)
	return df

def get_lin_model_residual(X, y, log_X = True, log_y = True, reversal = True):
	"""
	Calculates linear model residual of selected columns

	Parameters
	----------
	X: numpy array, feature array
	y: numpy array, outcome array
	log_X: bool, take log of X
	log_y: bool, take log of y
	reversal: bool, reverse signs of residual

	Returns
	-------
	residual: numpy array, residual of each value
	"""
	model = LinearRegression()
	X_train = np.log(X) if log_X else X
	y_train = np.log(y) if log_y else y

	X_train = X_train.values.reshape(-1, 1)
	y_train = y_train.values.reshape(-1, 1)

	model.fit(X_train, y_train)
	y_pred = model.predict(X_train)
	residual = y_pred - y_train

	if reversal:
		residual *= -1

	return residual

def get_metric_data():
	"""
	Gets dataframes with data aggregated at the domain level

	Returns
	-------
	metrics_full: Pandas DataFrame, aggregated metrics for all domains
	metrics_news: Pandas DataFrame, aggregated metrics for news domains
	"""

	connection = get_db_connection()

	db_query = """
	SELECT domains.*, link_count FROM 
		(SELECT domain, SUM(num_links) AS link_count FROM 
			(SELECT processed_link, COUNT(*) AS num_links FROM citations 
			WHERE processed_link NOT LIKE '%#%' GROUP BY 1) AS top_links 
		INNER JOIN link_domain_map ON top_links.processed_link = link_domain_map.processed_link 
		GROUP BY 1) AS top_domains 
	INNER JOIN domains ON top_domains.domain = domains.domain ORDER BY link_count DESC
	"""

	metrics_full = pd.read_sql(db_query, connection)
	metrics_full = metrics_full[metrics_full["alexa_linksincount"].notnull()]

	metrics_news = metrics_full[metrics_full["news_site"] == True]

	return metrics_full, metrics_news

def print_metrics(results_num = 10, output_file = None):
	"""
	Calculates and prints various metrics

	Parameters
	----------
	results_num: int, number of top and bottom results to display
	output_to_file: str, filename of output file - must be .txt
	"""

	metrics_full, metrics_news = get_metric_data()

	metric_names = ["link_count", "alexa_linksincount", "alexa_rank"]
	metrics = {"Full Dataset":metrics_full, "News Dataset":metrics_news}

	metric_border = "\n=======================\n"

	if output_file:
		original_stdout = sys.stdout
		file = open(output_file, 'w')
		sys.stdout = file

	for metric in metrics:
		print(f"\n************\n{metric}\n************\n")
		data = metrics[metric]
		data = get_rank(data, metric_names, [False, False, True])

		print(f"{metric_border}Gross Rank Differential - Alexa Linksin{metric_border}")

		data["links_differential"] = data["alexa_linksincount_ordinal_rank"] - data["link_count_ordinal_rank"]
		results_quick_view(data, "links_differential", results_num)

		print(f"{metric_border}Gross Rank Differential - Alexa Rank{metric_border}")

		data["rank_differential"] = data["alexa_rank_ordinal_rank"] - data["link_count_ordinal_rank"]
		results_quick_view(data, "rank_differential", results_num)

		print(f"{metric_border}Residual - Alexa Linksin Log{metric_border}")
		data["alexa_residual"] = get_lin_model_residual(data["alexa_linksincount"], data["link_count"])
		results_quick_view(data, "alexa_residual", results_num)

		print(f"{metric_border}Residual - Alexa Linksin{metric_border}")
		data["alexa_residual_no_log"] = get_lin_model_residual(data["alexa_linksincount"], data["link_count"], False, False)
		results_quick_view(data, "alexa_residual_no_log", results_num)

	if output_file:
		sys.stdout = original_stdout
		file.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-r', '--results_num', nargs = '?', type = int, default = 10)
	parser.add_argument('-o', '--output_file', nargs = '?', type = str, default = None)

	args = parser.parse_args()
	params = {}
	params["results_num"] = args.results_num
	params["output_file"] = args.output_file

	print_metrics(**params)