import boto3, os, argparse
from awis import myawis
from db_helpers import get_unique_set, get_list_from_custom_query, push_records_to_db

def generate_filename(domain):
	"""
	Creates alexa data filename from domain name

	Parameters
	----------
	domain: str, full domain string (eg. www.wikipedia.org)

	Returns
	-------
	filename: str, filename to save alexa xml in s3 bucket
	"""
	filename = f'alexa_data/{domain}.html'
	return filename

def create_bucket_if_not_exist(s3_object, bucket_name):
	"""
	Checks if Amazon S3 bucket exists, creates one if not
	
	Parameters
	----------
	s3_object: boto client, object that interfaces with Amazon S3
	bucket_name: str, name of the S3 bucket
	"""
	existing_buckets = s3_object.list_buckets()
	existing_bucket_names = {bucket["Name"] for bucket in existing_buckets["Buckets"]}
	if bucket_name not in existing_bucket_names:
		print("Creating new bucket...")
		_ = s3_object.create_bucket(Bucket=bucket_name)

def get_alexa_data(awis_object, processed_link):
	"""
	Gets alexa data and extracts specifc domain name

	Parameters
	----------
	awis_object: AWIS client, client that queries Alexa Web Information Services
	processed_link: str, link from wikipedia citation

	Returns
	-------
	alexa_data: xml, alexa data for specific domain
	domain: str, domain for wikipedia link
	"""

	alexa_data = awis_object.urlinfo(processed_link)
	domain = alexa_data.find('aws:contactinfo').find('aws:dataurl').text

	return alexa_data, domain

def store_alexa_data(s3_object, bucket_name, alexa_data, domain):
	"""
	Stores alexa data in an S3 bucket

	Parameters
	----------
	s3_object: boto client, object that interfaces with Amazon S3
	bucket_name: str, name of S3 bucket
	alexa_data: xml, alexa data for specific domain
	domain: str, domain for wikipedia link
	"""
	encoded_data = str(alexa_data).encode()
	filename = generate_filename(domain)
	_ = s3_object.put_object(Body=encoded_data, Bucket=bucket_name, Key=filename)
	return

def get_domain_data(num_links, bucket_name = 'wiki-trust-bucket'):
	"""
	Gets domain data for chosen number of links

	Parameters
	----------
	num_links: int, number of links to get domain data from, sorted by total presence in database
	bucket_name: str, name of S3 bucket
	"""

	# query links to get domain data for
	links_query = f"""
	SELECT * FROM 
	(SELECT processed_link, COUNT(*) AS num_links FROM citations 
	WHERE processed_link NOT LIKE '%#%' GROUP BY 1 ORDER BY 2 DESC LIMIT {num_links}) 
	AS top_links 
	WHERE processed_link NOT IN (SELECT processed_link FROM link_domain_map)
	"""
	links_no_domains = get_list_from_custom_query(links_query, 0)

	# get domains for which data already exist
	domains = get_unique_set("domains", "domain")	

	# initiate awis object
	awis_object = myawis.CallAwis(os.environ['AWSACCESSKEY'], os.environ['AWSSECRETKEY'])

	# initiate s3 object
	s3_object = boto3.client('s3',region_name='us-east-1',
		aws_access_key_id=os.environ["AWSACCESSKEY"],
		aws_secret_access_key=os.environ["AWSSECRETKEY"])
	create_bucket_if_not_exist(s3_object, bucket_name)

	# loop through each link and process it
	for counter, link in enumerate(links_no_domains):

		# get alexa data for specific link
		alexa_data, domain = get_alexa_data(awis_object, link)
		print(link, domain)

		# check if domain not already in dataset
		if domain not in domains:

			# add domain to database
			domain_data = {"domain":domain}
			push_records_to_db("domains", [domain_data])

			# store alexa data in s3 bucket
			store_alexa_data(s3_object, bucket_name, alexa_data, domain)

			# add domain to set of domains for which data already exists
			domains.add(domain)

		# add link domain mapping to db
		link_domain_map_data = {"processed_link":link, "domain":domain}
		push_records_to_db("link_domain_map", [link_domain_map_data])

		# print status counter
		if counter % 50 == 0:
			print(f"{counter + 1} out of {len(links_no_domains)} complete...")


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', '--num_links', nargs = '?', type = int, default = 1000)

	args = parser.parse_args()
	params = {}
	params["num_links"] = args.num_links

	get_domain_data(**params)
