import requests
import sys
import os
import time
import concurrent.futures

from header import title
from threading import Lock
from pathlib import Path
from bs4 import BeautifulSoup as soup

title()


class wallpaper_scraper:

	def __init__(self):
	
		self.executor = concurrent.futures.ThreadPoolExecutor(100)
		self.search_query = input('Enter Search Query: ')
		self.number_of_pages = input('Enter Number of pages: ')
		self.path = str(Path(__file__).parent) + '/downloaded/'
		self.mutex = Lock()
		self.image_file_number = 0
		self.image_links =[]
		self.image_download_page = []
		self.images = []
		self.page_number = 0
		self.item = 0
		self.item_two = 0
		
	def scraper(self):
	
		os.makedirs(self.path, exist_ok=True)
		while self.page_number < int(self.number_of_pages):			
			page='https://www.wallpaperflare.com/search?wallpaper='+ self.search_query + '&page=' + str(self.page_number)
			request = requests.get(page)
			if request.status_code == 404:
				break
			parse = soup(request.content,'html.parser')
			fetch = parse.find_all('a',attrs={'itemprop':'url'})
			for i in fetch:
				self.image_links.append(i['href'])
			self.page_number += 1
			sys.stdout.write('Scraping Page {}, Found {} Links'.format(self.page_number, len(self.image_links)))
			sys.stdout.flush()
			if self.page_number != int(self.number_of_pages):
				sys.stdout.write('\033[2K\033[1G')
			

	def URL_scraper(self, image_links, i):
		request = requests.get(image_links[i])
		parse = soup(request.content,'html.parser')
		fetch = parse.find('a',{'class':'link_btn aq mt20'})
		self.image_download_page.append(fetch['href'])
		
	def Image_Link_Scraper(self, image_download_page, i):
		
		request = requests.get(image_download_page[i])
		parse = soup(request.content,'html.parser')
		fetch = parse.find('img',attrs={'itemprop':'contentUrl'})
		self.images.append(fetch['src'])

	def download_image(self, path, number, url, index):		
		downloaded_image = requests.get(url[index]).content
		with open(path + 'image' + str(number) + '.jpg','wb') as image:			
			print('Downloading: ' + url[index])
			image.write(downloaded_image)
		image.close()
	
	def progress_indicator(self, future):
		self.item +=1
		print('\rScraping {} of {}'.format(str(self.item), len(self.image_links)), end='')
		
	def scraper_indicator(self, future):
		self.item_two +=1
		print('\rAcquiring Image {} of {}'.format(str(self.item), len(self.image_links)), end='')
		
	def threaded_download(self):
		self.scraper()
		futures_list = []
		image_link_thread = []
		
		futures_list = [self.executor.submit(self.URL_scraper, self.image_links, image_link) for image_link in range(len(self.image_links))]
		
		image_link_thread = [self.executor.submit(self.Image_Link_Scraper, self.image_download_page, page_index) for page_index in range(len(self.image_download_page))]
		
		for future in futures_list:			
			result = future.result()
			
		for future in image_link_thread:
			future.add_done_callback(self.scraper_indicator)
		
start = wallpaper_scraper()
start.threaded_download()
#start.print_list()
