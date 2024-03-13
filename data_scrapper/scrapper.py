from pathlib import Path
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from settings import ORIGIN_URL, SOURCE_HTML_NAME, ORIGIN_ROOT, DOWNLOAD_DIRECTORY

SP_GN = 'sp_gn'
GN_SP = 'gn_sp'

def get_origin_source_response(origin_url):
	request_result = requests.get(origin_url)
	return request_result.text

def save_result_to_disk(text, where_to_save):
	with open(where_to_save, mode='w', encoding='UTF-8') as file:
		file.write(text)

def read_html_source(html_source_name):
	source_text = ''
	with open(html_source_name, mode='r', encoding='UTF-8') as file:
		source_text = file.read()
	return source_text

def filter_li(tag, language_prefix):
	"""
	This function return the li tag we are interested

	We are interested to extract the url from the 'a' tag corresponding to the following block of code in source.html

	<li class="first">
		<span class="item-title"><a href="/2012/index.php/diccionario-guarani/599-guarani-espanol/tai-a">
			Tai A</a>
		</span>
		<dl><dt>
			Article Count:</dt>
			<dd>1</dd>
		</dl>
		
	</li>

	"""
	return tag.name == 'a' and tag.has_attr('href') and tag['href'] != '#' and tag['href'] != '' and tag.string and language_prefix in tag.string.lower()

def create_dictionary_to_store_urls(url_tags, lang_prefix):
	url_dict = {'language_order': [], 
				'letter': [], 
				'title': [], 
				'url': [],
				'dir_path': [],
				'downloaded_already': []
				}

	for tag_a in url_tags:
		url_dict['language_order'].append(lang_prefix)
		url_dict['letter'].append(tag_a.string.lower().strip().split(' ')[1])
		url_dict['title'].append(tag_a.string.lower().strip())
		url_dict['url'].append(tag_a['href'])
		url_dict['dir_path'].append('')
		url_dict['downloaded_already'].append(False)

	return url_dict

def get_urls_and_save_them_to_csv_file(html_source_text, where_to_save):
	# parse it with beautiful soup
	soup = BeautifulSoup(html_source_text, 'html.parser')
	
	all_a_gn = soup.find_all(lambda x: filter_li(x, 'tai '))
	all_a_sp = soup.find_all(lambda x: filter_li(x, 'letra '))

	url_dict_gn = create_dictionary_to_store_urls(all_a_gn, GN_SP)
	url_dict_sp = create_dictionary_to_store_urls(all_a_sp, SP_GN)
	merged_dict = {}

	for k in url_dict_gn.keys():
		merged_dict.setdefault(k, [])
		merged_dict[k] = url_dict_gn[k]+url_dict_sp[k]

	# create csv to store URLs of interest
	urls_df = pd.DataFrame(merged_dict)
	urls_df.to_csv(where_to_save, index=False)

	return urls_df

def check_directory_and_create_it(dir_path):
	if dir_path.is_dir():
		print(f"{dir_path} exists. No need to create one!")
	else:
		print(f"{dir_path} does not exist. Creating it...")
		dir_path.mkdir(parents=True, exist_ok=False)
		print(f"{dir_path} created!")

def main():
		# check whether we already downloaded origin source
		if Path(SOURCE_HTML_NAME).is_file():
			print(f'{SOURCE_HTML_NAME} already downloaded, proceed to next steps')
		else:
			print(f'Downloading html source from {ORIGIN_URL} and saving it to local file {SOURCE_HTML_NAME}')
			response_text = get_origin_source_response(ORIGIN_URL)
			save_result_to_disk(response_text, where_to_save=SOURCE_HTML_NAME)

		# at this point, we should already have our source.html downloaded so let's load it and open it with bs4
		source_text = read_html_source(SOURCE_HTML_NAME)
		urls_df = get_urls_and_save_them_to_csv_file(source_text, where_to_save='urls.csv')

		# get each url and read the html from each, in this new pages we are going to find the actual dictionary where we need to populate data from 
		# we are going to download the files locally so we can process it without any network issues
		dir_path = Path(DOWNLOAD_DIRECTORY)
		spanish_path = dir_path.joinpath(SP_GN)
		guarani_path = dir_path.joinpath(GN_SP)

		check_directory_and_create_it(spanish_path)
		check_directory_and_create_it(guarani_path)

		for i, url in enumerate(urls_df['url']):
			lang_order = urls_df.loc[i, 'language_order']
			html_name = urls_df.loc[i, 'title']
			print(i, lang_order, url)
			if lang_order == GN_SP:
				# GET THE DATA AND STORE IT TO THE CORRESPONDING FOLDER
				response = get_origin_source_response(f'{ORIGIN_ROOT}{url}')
				save_result_to_disk(response, where_to_save=guarani_path.joinpath(f'{html_name}.html'))
				urls_df.loc[i, 'dir_path'] = guarani_path.joinpath(f'{html_name}.html')
				urls_df.loc[i, 'downloaded_already'] = True
			elif lang_order == SP_GN:
				# GET THE DATA AND STORE IT TO THE CORRESPONDING FOLDER
				response = get_origin_source_response(f'{ORIGIN_ROOT}{url}')
				save_result_to_disk(response, where_to_save=spanish_path.joinpath(f'{html_name}.html'))
				urls_df.loc[i, 'dir_path'] = guarani_path.joinpath(f'{html_name}.html')
				urls_df.loc[i, 'downloaded_already'] = True

		# rewrite urls_df
		urls_df.to_csv('urls.csv', index=False)

if __name__ == '__main__':

	# check if urls.csv file exists and if the files where already downloaded
	if Path('urls.csv').is_file():
		urls_df = pd.read_csv('urls.csv')
		if False in urls_df['downloaded_already']:
			main()
		else:
			print('No need to perform any action, all necessary data has been already downloaded. Proceed to processing...')
	else:
		main()


		
	    


	



