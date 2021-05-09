from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from natsort import natsorted
from pathlib import Path
from docx import Document
from docx.shared import Pt
import threading, codecs, requests, os, shutil, re
from multiprocessing.dummy import Pool as ThreadPool
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
		title = re.sub(r'[<>:\"/\\\|\?\*]',r'', title)
		self.title = title.encode("ascii", "ignore").decode()
	def __str__(self):
		if self.status == "Null":
			return f"{self.code} {self.title}"
		else:
			return f"{self.status} {self.code} {self.title}"

def countLine():
	return len('------------------------------\n')

def writeLine(file):
	file.write('------------------------------\n')
	return len('------------------------------\n')

def updateLibrary(novels):
	library = open('library.txt', 'w')
	print("To Read", file=library)
	for novel in novels:
		if novel.status == "Null":
			print(novel, file=library)
	print("\nReading", file=library)
	for novel in novels:
		if novel.status != "Null":
			print(novel, file=library)

def truncate(data):
	return (data[:50] + '..') if len(data) > 50 else data

def writeTitleAuthor(soup, file):
	count = 0
	title = soup.find_all('p', class_="novel_title")[0].get_text().strip()
	author = soup.find_all('div', class_="novel_writername")[0].get_text().split('：')[1].strip()
	file.write(f'タイトル: {title}\n')
	file.write(f'作者: {author}\n')
	return len(f'タイトル: {title}\n') + len(f'作者: {author}\n')

def writeChapterTitleAndProgress(soup, file):
	section = soup.find(['p'], class_=["chapter_title"])
	title = soup.find(['p'], class_=["novel_subtitle"])
	progress = soup.find(['div'], id=["novel_no"])
	count = 0
	if section:
		count += len(f"セクション：{section.get_text().strip()}")
		print(f"セクション：{section.get_text().strip()}", file=file)
	print(f"章題：{title.get_text().strip()}", file=file)
	print(f"章番号：{progress.get_text().strip()}", file=file)
	return count + len(f"章題：{title.get_text().strip()}") + len(f"章番号：{progress.get_text().strip()}")

def writeBody(soup, file):
	chapterP = soup.find(id='novel_p')
	count = 0
	if chapterP:
		file.write(f'{chapterP.get_text()}\n')
		count += len(f'{chapterP.get_text()}\n')
		count += writeLine(file)
	chapterHonbun = soup.find(id='novel_honbun')
	honbunParagraphs = chapterHonbun.select('p')
	for paragraph in honbunParagraphs:
		file.write(f'{paragraph.get_text()}\n')
		count += len(f'{paragraph.get_text()}\n')
		images = paragraph.find_all('img')
		if images:
			src = images[0]['src']
			file.write(f'Image: {src}\n')
			count += len(f'Image: {src}\n')
	chapterA = soup.find(id='novel_a')
	if chapterA:
		count += writeLine(file)
		file.write(f'{chapterA.get_text()}\n')
		count += len(f'{chapterA.get_text()}\n')
	return count

def countBody(soup):
	chapterP = soup.find(id='novel_p')
	count = 0
	if chapterP:
		count += len(f'{chapterP.get_text()}\n')
		count += countLine()
	chapterHonbun = soup.find(id='novel_honbun')
	honbunParagraphs = chapterHonbun.select('p')
	for paragraph in honbunParagraphs:
		count += len(f'{paragraph.get_text()}\n')
		images = paragraph.find_all('img')
		if images:
			src = images[0]['src']
			count += len(f'Image: {src}\n')
	chapterA = soup.find(id='novel_a')
	if chapterA:
		count += countLine()
		count += len(f'{chapterA.get_text()}\n')
	return count

def writeTableOfContents(soup, file):
	count = 0
	chapters = soup.find_all(['div', 'dl'], class_=["chapter_title", "novel_sublist2"])
	for index, chapter in enumerate(chapters):
		lines = chapter.get_text().strip().split("\n")
		lines = [line.strip() for line in lines if len(line.strip()) > 0]
		if len(lines) == 1:
			if index != 0:
				count += writeLine(file)
			print(f"{lines[0]}", file=file)
			count += writeLine(file)
			count += len(f"{lines[0]}")
		else:
			print(lines[0], file=file)
			print(lines[1], file=file)
			count += len(lines[0])
			count += len(lines[1])
	return count

def getChapterUrls(soup):
	urls = []
	chapters = soup.find_all(['div', 'dl'], class_=["chapter_title", "novel_sublist2"])
	for index, chapter in enumerate(chapters):
		lines = chapter.get_text().strip().split("\n")
		lines = [line.strip() for line in lines if len(line.strip()) > 0]
		if len(lines) == 1:
			continue
		else:
			urls.append(f"https://ncode.syosetu.com{chapter.find('a', href=True)['href']}")
	return urls

def writeChapters(soup, file, count):
	chapters = soup.find_all(['div', 'dl'], class_=["chapter_title", "novel_sublist2"])
	text = ""
	for index, chapter in enumerate(chapters):
		lines = chapter.get_text().strip().split("\n")
		lines = [line.strip() for line in lines if len(line.strip()) > 0]
		if len(lines) == 1:
			continue
		else:
			chapterUrl = f"https://ncode.syosetu.com/{chapter.find('a', href=True)['href']}"
			chapterResponse = requests.get(chapterUrl, headers=headers, cookies=cookies)
			chapterSoup = BeautifulSoup(chapterResponse.text, 'html.parser')
			section = chapterSoup.find(['p'], class_=["chapter_title"])
			title = chapterSoup.find(['p'], class_=["novel_subtitle"]).get_text().strip()
			progress = chapterSoup.find(['div'], id=["novel_no"]).get_text().strip()
			print(f"Words: {count}/100000 Progress: {progress}")
			if section:
				count += len(f"セクション：{section.get_text().strip()}")
			count += countLine() + len(f"章題：{title}") + len(f"章番号：{progress}") + len(f"日付：{lines[1]}")
			count += countBody(chapterSoup)
			if count > 100000:
				print(f"Last chapter: {progress}")
				return progress
			writeLine(file)
			writeChapterTitleAndProgress(chapterSoup, file)
			print(f"日付：{lines[1]}", file=file)
			writeBody(chapterSoup, file)

def getChapter(chapterUrl):
	chapterNum = int(chapterUrls[0].split()[0].split('/')[-1])
	date = dates[chapterNum]
	chapterResponse = requests.get(chapterUrl, headers=headers, cookies=cookies)
	chapterSoup = BeautifulSoup(chapterResponse.text, 'html.parser')
	section = chapterSoup.find(['p'], class_=["chapter_title"])
	title = chapterSoup.find(['p'], class_=["novel_subtitle"]).get_text().strip()
	progress = chapterSoup.find(['div'], id=["novel_no"]).get_text().strip()
	index = int(progress.split('/')[0])
	file = codecs.open(f"temp/{index}.txt", 'w+', "utf-8")
	chapters = os.listdir("temp")
	print(f"Progress: {len(chapters)}/{totalToDownload}")
	writeLine(file)
	writeChapterTitleAndProgress(chapterSoup, file)
	print(f"日付：{date}", file=file)
	writeBody(chapterSoup, file)

def splitTextToTranslate(textFile, code):
	

library = open('library.txt', 'r')
mode = "Null"
dates = []
novels = []
totalToDownload = 0
totalToUpdate = 0
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
			novels.append(Novel("Null", line[0], line[1]))
			totalToDownload += 1
		elif mode == "Reading":
			line = line.split(' ', 1)
			codeAndTitle = line[1].split(' ', 1)
			novels.append(Novel(line[0], codeAndTitle[0], codeAndTitle[1]))
			totalToUpdate += 1


Path("ncode").mkdir(parents=True, exist_ok=True)
Path("toTranslate").mkdir(parents=True, exist_ok=True)
Path("novel18").mkdir(parents=True, exist_ok=True)
ncode = os.listdir("ncode")
novel18 = os.listdir("novel18")
toRead = list(filter(lambda novel: novel.status == "Null", novels))
reading = list(filter(lambda novel: novel.status != "Null", novels))
alreadyDownloaded = ncode + novel18
alreadyDownloaded = [novel[:-4] for novel in alreadyDownloaded]
progress = 1

for novel in toRead:
	totalWords = 0
	if novel.code in alreadyDownloaded:
		print(f"\"{novel.code}\" already downloaded. Cannot download preview.")
		continue
	print(f"Downloading {progress}/{totalToDownload} previews: {novel.title}")
	url = f"https://ncode.syosetu.com/{novel.code}/"
	response = requests.get(url, headers=headers, cookies=cookies)
	soup = BeautifulSoup(response.text, 'html.parser')
	synopsis = soup.find(id='novel_ex')
	path = "Null"
	if "ncode" in response.url:
		path = f"ncode/{novel.code}.txt"
	elif "novel18" in response.url:
		path = f"novel18/{novel.code}.txt"
	else:
		print(f"response.url error: {response.url}")
	temp = codecs.open("temp.txt", 'w+', "utf-8")
	totalWords += writeTitleAuthor(soup, temp)
	print(f"Nコード: {response.url}", file=temp)
	if synopsis:
		temp.write(f'{synopsis.get_text().strip()}\n')
		totalWords += len(f'{synopsis.get_text().strip()}\n')
		totalWords += writeLine(temp)
		totalWords += writeTableOfContents(soup, temp)
		newStatus = writeChapters(soup, temp, totalWords)
		novel.status = newStatus
	else:
		totalWords += writeLine(temp)
		totalWords += writeBody(soup, temp)
		novel.status = "Short"
	progress += 1
	temp.close()
	temp = codecs.open('temp.txt', 'r', "utf-8")
	textFile = codecs.open(path, 'w+', "utf-8")
	for line in temp.readlines():
		line = line.strip()
		if len(line) <= 0:
			continue
		else:
			print(line, file=textFile)
	temp.close()
	textFile.close()
	os.remove("temp.txt")
	
	textFile = codecs.open(path, 'r', "utf-8")
	splittedFile = codecs.open(f'toTranslate/{novel.code} 0.txt', "w+", "utf-8")
	fileNum = 0
	charNum = 0
	for line in textFile.readlines():
	    charNum += len(line)
	    if charNum > 100000:
	        charNum = 0
	        fileNum += 1;
	        splittedFile = codecs.open(f'toTranslate/{novel.code} {fileNum}.txt', "w+", "utf-8")
	    splittedFile.write(line)
	textFile.close()
	splittedFile.close()

for novel in reading:
	os.mkdir("temp")
	if novel.title not in alreadyDownloaded:
		print(f"\"{novel.title}\" missing. Cannot update chapters.")
		continue
	url = f"https://ncode.syosetu.com/{novel.code}/"
	response = requests.get(url, headers=headers, cookies=cookies)
	soup = BeautifulSoup(response.text, 'html.parser')
	start = int(novel.status.split('/')[0])
	end = int(list(filter(lambda piece: len(piece) > 0, getChapterUrls(soup)[-1].strip().split('/')))[-1])
	if start == end:
		continue
	print(f"Downloading {progress}/{totalToUpdate} updates: {novel.title}")
	path = "Null"
	if "ncode" in response.url:
		path = f"ncode/{novel.code}.txt"
	elif "novel18" in response.url:
		path = f"novel18/{novel.code}.txt"
	else:
		print(f"response.url error: {response.url}")

	chapterUrls = [f"https://ncode.syosetu.com/{novel.code}/{i}" for i in range(start, end + 1)]
	dates = soup.find_all('dt', class_="long_update")
	dates = [date.get_text().strip() for date in dates][start - 1:]
	totalToDownload = end - start + 1
	pool = ThreadPool(3)
	pool.map(getChapter, chapterUrls)
	progress += 1

	chapters = natsorted([chapter for chapter in os.listdir("temp")])
	temp = codecs.open("temp.txt", 'w+', "utf-8")
	for chapter in chapters:
		file = codecs.open(f"temp/{chapter}", 'r', "utf-8")
		temp.write(file.read())
		file.close()
	temp.close()
	temp = codecs.open('temp.txt', 'r', "utf-8")
	textFile = codecs.open(path, 'a+', "utf-8")
	for line in temp.readlines():
		line = line.strip()
		if len(line) <= 0:
			continue
		else:
			print(line, file=textFile)
	temp.close()
	textFile.close()
	os.remove("temp.txt")
	shutil.rmtree("temp")

textFilesToConvertToDocX = [file for file in os.listdir("toTranslate")]
for file in textFilesToConvertToDocX:
	document = Document()
	font = document.styles['Normal'].font
	font.name = 'Yu Mincho'
	font.size = Pt(11)
	path = f"toTranslate/{file}"
	textFile = codecs.open(path, "r", "utf-8")
	lines = tuple(textFile)
	for line in lines:
		document.add_paragraph(line.strip())
	filename = file.rsplit(".", 1)[0] + ".docx"
	document.save(f"toTranslate/{filename}")
	textFile.close()
	os.remove(path)

updateLibrary(novels)