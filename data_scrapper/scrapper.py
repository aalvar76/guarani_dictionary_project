import requests
import pathlib
import re
from bs4 import BeautifulSoup
from settings import ORIGIN_URL, SOURCE_HTML_NAME

print(ORIGIN_URL)

# grab the web page we are going to extract data from


def get_origin_source_response(origin_url):
	request_result = requests.get(origin_url)
	return request_result.text

def save_result_to_disk(text, where_to_save):
	with open(where_to_save, mode='w', encoding='UTF-8') as file:
		file.write(text)

def find_all_tags_of_interest(soup):
	"""
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
	result = soup.find_all(filter_li)
	print(result)
	for r in result:
		print(r)

def filter_li(tag, language_prefix):
	"""
	This function return the li tag we are interested
	"""
	return tag.name == 'a' and tag.has_attr('href') and tag['href'] != '#' and tag['href'] != '' and tag.string and language_prefix in tag.string.lower()


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

	# parse it with beautiful soup
	soup = BeautifulSoup(source_text, 'html.parser')
	
	all_a_gn = soup.find_all(lambda x: filter_li(x, 'tai '))
	all_a_sp = soup.find_all(lambda x: filter_li(x, 'letra '))


	print(all_a_gn+all_a_sp)




