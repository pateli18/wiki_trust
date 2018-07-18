import numpy as np
from sklearn.linear_model import LinearRegression

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