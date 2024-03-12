import requests
import pathlib
from bs4 import BeautifulSoup
from settings import ORIGIN_URL, SOURCE_HTML_NAME

print(ORIGIN_URL)

# grab the web page we are going to extract data from


def get_origin_source_response(origin_url):
	request_result = requests.get(origin_url)
	return request_result.text

def save_result_to_disk(text,where_to_save):
	with open(where_to_save, mode='w', encoding='UTF-8') as file:
		file.write(text)


if __name__ == '__main__':
	# check whether we already downloaded origin source
	if pathlib.Path(SOURCE_HTML_NAME).is_file():
		print(f'{SOURCE_HTML_NAME} already downloaded proceed to next steps')
	else:
		print(f'Downloading html source from {ORIGIN_URL} and saving it to local file {SOURCE_HTML_NAME}')
		response_text = get_origin_source_response(ORIGIN_URL)
		save_result_to_disk(response_text,where_to_save=SOURCE_HTML_NAME)

