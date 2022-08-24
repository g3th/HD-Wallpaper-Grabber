import requests
import sys
import os
import time
import concurrent.futures
from header import title
from threading import Lock
from pathlib import Path
from bs4 import BeautifulSoup as soup

path = str(Path(__file__).parent) + '/downloaded/'
urls_list = []
image_download_page=[]
images =[]
os.makedirs(path, exist_ok=True)
title()		
def scraper():
	title()
	image_links =[]
	page_number = 0
	search_query = input('\nEnter Search Query or (q)uit: ')
	if search_query == 'q':
		exit()
	title()
	number_of_pages = input('\nEnter Number of pages: ')
	title()
	print('\rQuery = {} | Pages = {}'.format(search_query, number_of_pages))
	print('\n')
	while page_number < int(number_of_pages):	
		page='https://www.wallpaperflare.com/search?wallpaper='+ search_query + '&page=' + str(page_number)
		request = requests.get(page)
		if request.status_code == 404:
			break
		parse = soup(request.content,'html.parser')
		fetch = parse.find_all('a',attrs={'itemprop':'url'})
		for i in fetch:
			image_links.append(i['href'])
		page_number += 1
		print('\rScraping Page {}, Found {} Links'.format(page_number, len(image_links)),end='')
	return image_links
	
def URL_scraper(index, page):
	progress_bar = round(index / len(page) * 100,1)		
	request = requests.get(page[index])
	parse = soup(request.content,'html.parser')
	fetch = parse.find('a',{'class':'link_btn aq mt20'})
	print('\rScraping {} URLs: Progress {}              '.format(len(page), progress_bar), end='')
	image_download_page.append(fetch['href'])
	return image_download_page

def Image_Link_Scraper(index, page):
	progress_bar = round(index / len(page) * 100,1)
	request = requests.get(page[index])
	parse = soup(request.content,'html.parser')
	fetch = parse.find('img',attrs={'itemprop':'contentUrl'})	
	print('\rScraping {} Images: Progress {}            '.format(len(page), progress_bar), end='')
	images.append(fetch['src'])
	return images
			
def download_image(url, index, path, number):
	with open(path + 'image' + str(number) + '.jpg','wb') as image:
		progress_bar = round(index / len(url) * 100,1)
		print('\rDownloading {} Images - Progress: {}%'.format(len(url), progress_bar), end='')	
		downloaded_image = requests.get(url[index])	
		image.write(downloaded_image.content)
	

image_links = scraper()

with concurrent.futures.ThreadPoolExecutor(20) as executor:
	for index in range(len(image_links)):
		url_scraper = executor.submit(URL_scraper, index, image_links)
		urls_list = url_scraper.result()
	print('\n')
	for index in range(len(urls_list)):
		scraped_image_links = executor.submit(Image_Link_Scraper, index, urls_list)
		scraped_images = scraped_image_links.result()
	print('\n')
	for index in range(len(scraped_images)):
		executor.submit(download_image, scraped_images, index, path, index)

print('\n\nAll Done.\n')


