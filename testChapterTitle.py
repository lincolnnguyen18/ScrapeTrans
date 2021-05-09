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
url = f"https://novel18.syosetu.com/n6677dw/1"
response = requests.get(url, headers=headers, cookies=cookies)
soup = BeautifulSoup(response.text, 'html.parser')
section = soup.find(['p'], class_=["chapter_title"])
title = soup.find(['p'], class_=["novel_subtitle"])
progress = soup.find(['div'], id=["novel_no"])
if section:
	print(section.get_text().strip())
print(title.get_text().strip())
print(progress.get_text().strip())