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

def writeChapterTitleAndProgress(soup):
	section = soup.find(['p'], class_=["chapter_title"])
	title = soup.find(['p'], class_=["novel_subtitle"])
	progress = soup.find(['div'], id=["novel_no"])
	if section:
		print(f"セクション：{section.get_text().strip()}")
	print(f"章題：{title.get_text().strip()}")
	print(f"章番号：{progress.get_text().strip()}")

url = f"https://ncode.syosetu.com/n8856gp/"
response = requests.get(url, headers=headers, cookies=cookies)
soup = BeautifulSoup(response.text, 'html.parser')
chapters = soup.find_all(['div', 'dl'], class_=["chapter_title", "novel_sublist2"])
for chapter in chapters:
	lines = chapter.get_text().strip().split("\n")
	lines = [line.strip() for line in lines if len(line.strip()) > 0]
	if len(lines) == 1:
		continue
	else:
		chapterUrl = f"https://ncode.syosetu.com/{chapter.find('a', href=True)['href']}"
		chapterResponse = requests.get(chapterUrl, headers=headers, cookies=cookies)
		chapterSoup = BeautifulSoup(chapterResponse.text, 'html.parser')
		writeChapterTitleAndProgress(chapterSoup)
		print(f"日付：{lines[1]}")
