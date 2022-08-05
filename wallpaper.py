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
	
		self.search_query = input('Enter Search Query: ')
		self.number_of_pages = input('Enter Number of pages: ')
		self.path = str(Path(__file__).parent) + '/downloaded/'
		self.mutex = Lock()
		self.image_links =[]
		self.image_download_page = []
		self.images = []
		self.page_number = 0
		
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
			print('\rScraping Page {}, Found {} Links'.format(self.page_number, len(self.image_links)),end='')
			
	def URL_scraper(self, pages, index):
		
		request = requests.get(pages[index])
		parse = soup(request.content,'html.parser')
		fetch = parse.find('a',{'class':'link_btn aq mt20'})
		print('\rScraping {} of {} URLs'.format(str(index+1), len(self.image_links)), end='')
		self.image_download_page.append(fetch['href'])
		
		
	def Image_Link_Scraper(self, pages, index):
			
		request = requests.get(pages[index])
		parse = soup(request.content,'html.parser')
		fetch = parse.find('img',attrs={'itemprop':'contentUrl'})			
		print('\rScraping {} of {} Image Links'.format(str(self.item), len(self.image_download_page)), end='')
		self.images.append(fetch['src'])
				

	def download_image(self, path, number, url, index):	

		downloaded_image = requests.get(url[index]).content
		with open(path + 'image' + str(number) + '.jpg','wb') as image:			
			print('Downloading: ' + url[index])
			image.write(downloaded_image)
		image.close()

	
	def threaded_URL_scraper(self):
		self.scraper()
		with concurrent.futures.ThreadPoolExecutor() as executor:
		
			for index in range(len(self.image_links)):
				executor.submit(self.URL_scraper, self.image_links, index)

			for index in range(len(self.image_download_page)):
				executor.submit(self.Image_Link_Scraper, self.image_download_page, index)
			print('test')

			for index in range(len(self.image_download_page)):
				executor.submit(self.download_image, self.path, index, self.image_download_page, index)
		
start = wallpaper_scraper()
start.threaded_URL_scraper()
#start.print_list()
