import requests
import pathlib
import re
import pandas as pd
from bs4 import BeautifulSoup
from settings import ORIGIN_URL, SOURCE_HTML_NAME, ORIGIN_ROOT

def get_origin_source_response(origin_url):
	request_result = requests.get(origin_url)
	return request_result.text

def save_result_to_disk(text, where_to_save):
	with open(where_to_save, mode='w', encoding='UTF-8') as file:
		file.write(text)

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
				'url': []
				}

	for tag_a in url_tags:
		url_dict['language_order'].append(lang_prefix)
		url_dict['letter'].append(tag_a.string.lower().strip().split(' ')[1])
		url_dict['title'].append(tag_a.string.lower().strip())
		url_dict['url'].append(tag_a['href'])

	return url_dict

def get_urls_and_save_them_to_csv_file(html_source_text, csv_file_name):
	# parse it with beautiful soup
	soup = BeautifulSoup(html_source_text, 'html.parser')
	
	all_a_gn = soup.find_all(lambda x: filter_li(x, 'tai '))
	all_a_sp = soup.find_all(lambda x: filter_li(x, 'letra '))

	url_dict_gn = create_dictionary_to_store_urls(all_a_gn, 'gn_sp')
	url_dict_sp = create_dictionary_to_store_urls(all_a_sp, 'sp_gn')
	merged_dict = {}

	for k in url_dict_gn.keys():
		merged_dict.setdefault(k, [])
		merged_dict[k] = url_dict_gn[k]+url_dict_sp[k]

	# create csv to store URLs of interest
	urls_df = pd.DataFrame(merged_dict)
	urls_df.to_csv(csv_file_name, index=False)

	return urls_df

if __name__ == '__main__':
	source_text = ''
	# check whether we already downloaded origin source
	if pathlib.Path(SOURCE_HTML_NAME).is_file():
		print(f'{SOURCE_HTML_NAME} already downloaded, proceed to next steps')
	else:
		print(f'Downloading html source from {ORIGIN_URL} and saving it to local file {SOURCE_HTML_NAME}')
		response_text = get_origin_source_response(ORIGIN_URL)
		save_result_to_disk(response_text, where_to_save=SOURCE_HTML_NAME)


	# at this point, we should already have our source.html downloaded so let's load it and open it with bs4
	with open(SOURCE_HTML_NAME, mode='r', encoding='UTF-8') as file:
		source_text = file.read()


	urls_df = get_urls_and_save_them_to_csv_file(source_text, 'urls.csv')

	# get each url and read it
	


	




