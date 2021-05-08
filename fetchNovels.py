import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import threading, codecs, requests, os
cookies = {
	'over18': 'yes',
}
headers = {
	'Connection': 'keep-alive',
	'sec-ch-ua': '^\\^Google',
	'sec-ch-ua-mobile': '?0',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'Sec-Fetch-Site': 'same-site',
	'Sec-Fetch-Mode': 'navigate',
	'Sec-Fetch-User': '?1',
	'Sec-Fetch-Dest': 'document',
	'Referer': 'https://nl.syosetu.com/',
	'Accept-Language': 'en-US,en;q=0.9',
}

class Novel:
	def __init__(self, status, code, title):
		self.status = status
		self.code = code
		self.title = re.sub(r'[<>:\"/\\\|\?\*]',r'', title)
	def __str__(self):
		if self.status == "Null":
			return f"{self.code} {self.title}"
		else:
			return f"{self.status} {self.code} {self.title}"

def updateLibrary(toRead, reading):
	library = open('library.txt', 'w')
	print("To Read", file=library)
	for novel in toRead:
		print(novel, file=library)
	print("\nReading", file=library)
	for novel in reading:
		print(novel, file=library)

def truncate(data):
	return (data[:50] + '..') if len(data) > 50 else data

library = open('library.txt', 'r')
mode = "Null"
toRead = []
reading = []
for line in library.readlines():
	line = line.strip()
	if line == "To Read":
		mode = "To Read"
		continue
	elif line == "Reading":
		mode = "Reading"
		continue
	elif line == "Done":
		mode = "Done"
		continue
	elif len(line) <= 0:
		continue
	else:
		if mode == "To Read":
			line = line.split(' ', 1)
			toRead.append(Novel("Null", line[0], line[1]))
		elif mode == "Reading":
			line = line.split(' ', 1)
			codeAndTitle = line[1].split(' ', 1)
			reading.append(Novel(line[0], codeAndTitle[0], codeAndTitle[1]))

# updateLibrary(toRead, reading)

ncode = os.listdir("ncode")
novel18 = os.listdir("novel18")
alreadyDownloaded = ncode + novel18
alreadyDownloaded = [novel[:-4] for novel in alreadyDownloaded]

for novel in toRead:
	if novel.title in alreadyDownloaded:
		print(f"\"{truncate(novel.title)}\" already downloaded. Cannot download preview.")
	url = f"https://ncode.syosetu.com/{novel.code}/"
	response = requests.get(url, headers=headers, cookies=cookies)
	if "ncode" in response.url:
		textFile = open(f"ncode/{novel.title}.txt", 'w+')
	elif "novel18" in response.url:
		textFile = open(f"novel18/{novel.title}.txt", 'w+')
	else:
		print(f"response.url error: {response.url}")
