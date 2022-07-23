import requests
import sys
import os
import time
import concurrent.futures
from threading import Lock
from pathlib import Path
from bs4 import BeautifulSoup as soup

print('\x1bc')

path = str(Path(__file__).parent) + '/downloaded/'
image_file_number = 0
image_links =[]
image_download_page = []
images = []
page_number = 0


os.makedirs(path, exist_ok=True)

search_query = input('Enter Search Query: ')

def URL_scraper(image_links, i):	
	request = requests.get(image_links[i])
	parse = soup(request.content,'html.parser')
	fetch = parse.find('a',{'class':'link_btn aq mt20'})
	print('Fetching URL: ' + image_links[i])
	return fetch['href']

def Image_Link_Scraper(image_download_page, i):	
	request = requests.get(image_download_page[i])
	parse = soup(request.content,'html.parser')
	fetch = parse.find('img',attrs={'itemprop':'contentUrl'})
	print('Scraping Image Link: ' + image_download_page[i])
	return fetch['src']

def download_image(path, number, url, index):
	downloaded_image = requests.get(url[index]).content	
	with open(path + 'image' + str(number) + '.jpg','wb') as image:			
		print('Downloading: ' + url[index])
		image.write(downloaded_image)
	image.close()
	

while page_number < 3:
	
	page='https://www.wallpaperflare.com/search?wallpaper='+ search_query + '&page=' + str(page_number)
	request = requests.get(page)
	if request.status_code == 404:
		break
	parse = soup(request.content,'html.parser')
	fetch = parse.find_all('a',attrs={'itemprop':'url'})
	for i in fetch:
		image_links.append(i['href'])
	page_number += 1
	sys.stdout.write('Scraping Page {}, Found {} Links'.format(page_number, len(image_links)))
	sys.stdout.flush()
	sys.stdout.write('\033[2K\033[1G')


futures_list = []
futures_images_list =[]
with concurrent.futures.ThreadPoolExecutor(100) as executor:

	print('\x1bc')
	for i in range(len(image_links)):
				
		thread = executor.submit(URL_scraper, image_links, i)
		futures_list.append(thread)
		
	for returned_value in futures_list:
		result = returned_value.result()
		image_download_page.append(result)
		
	print('\x1bc')
	for i in range(len(image_links)):		
		thread_two = executor.submit(Image_Link_Scraper, image_download_page, i)
		futures_images_list.append(thread_two)
		
	for returned_value in futures_images_list:
		image_results = returned_value.result()
		images.append(image_results)
		
	print('\x1bc')	
	for image in range(len(images)):
		executor.submit(download_image, path, str(image_file_number), images, image)
		image_file_number +=1
		
	executor. shutdown()
