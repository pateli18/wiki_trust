import boto3, botocore, os
from get_domain_data import generate_filename, initiate_s3_object, initiate_awis_object, get_alexa_data, store_alexa_data
from db_helpers import get_list_from_custom_query, update_domain_record
from bs4 import BeautifulSoup

def retrieve_object(domain, s3_object):
	"""
	Creates xml object that can be parsed from alexa data saved in s3
	
	Parameters
	----------
	domain: str, full domain string (eg. www.wikipedia.org)
	s3_object: boto client, object that interfaces with Amazon S3
	
	Returns
	-------
	soup, BeautifulSoup, object that can be parsed with BeautifulSoup library
	"""
	filename = generate_filename(domain)
	file_object = s3_object.get_object(Bucket='wiki-trust-bucket', Key=filename)
	file_raw = file_object["Body"].read().decode()
	soup = BeautifulSoup(file_raw, 'html.parser')
	return soup

def process_alexa_data(soup):
	"""
	Gets rank and linksincount of domain

	Parameters
	----------
	soup, BeautifulSoup, object that can be parsed with BeautifulSoup library

	Returns
	-------
	rank: int, domain's alexa rank
	linksincount: int, number of sites linking into domain
	"""
	rank = soup.find('aws:rank').text
	linksincount = soup.find('aws:linksincount').text

	rank = 'NULL' if rank == '' else rank
	linksincount = 'NULL' if linksincount == '' else linksincount

	return rank, linksincount

def process_domain_data(bucket_name = 'wiki-trust-bucket'):
	"""
	Extract data from alexa files and add to domains table in db

	Parameters
	----------
	bucket_name: str, name of S3 bucket
	"""
	
	# query links to get domain data for
	domains_query = """
	SELECT domain FROM domains WHERE alexa_linksincount IS NULL
	"""
	domains = get_list_from_custom_query(domains_query, 0)

	# initiate s3 object
	s3_object = initiate_s3_object(bucket_name)

	# loop through each domain, retreive data, and update in db
	for domain in domains:
		
		# attempt to get data file from s3
		try:
			soup = retrieve_object(domain, s3_object)

		# if file does not exist, query file from awis and save to s3
		except botocore.exceptions.ClientError as e:

			if e.response['Error']['Code'] == 'NoSuchKey':

				# retrieve awis data
				print(f"Retrieving data file for {domain}...")
				awis_object = initiate_awis_object()
				alexa_data, _ = get_alexa_data(awis_object, domain)

				# store alexa data in s3 bucket
				store_alexa_data(s3_object, bucket_name, alexa_data, domain)

				soup = retrieve_object(domain, s3_object)

			else:

				print(e)
				break


		# update data in db
		rank, linksincount = process_alexa_data(soup)
		print(domain, rank, linksincount)
		update_domain_record(domain, rank, linksincount)

if __name__ == "__main__":
	process_domain_data()

