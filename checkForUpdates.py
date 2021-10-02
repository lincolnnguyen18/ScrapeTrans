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

def checkForNewChapters(novel):
    # if novel.title not in alreadyDownloaded:
    #     print(f"\"{novel.title}\" missing. Cannot check for updates.")
    #     return
    if novel.status == "Short":
        return
    url = f"https://ncode.syosetu.com/{novel.code}/"
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser')
    start = int(novel.status.split('/')[0])
    storedEnd = int(novel.status.split('/')[1])
    fetchedEnd = int(list(filter(lambda piece: len(piece) > 0, getChapterUrls(soup)[-1].strip().split('/')))[-1])
    if fetchedEnd == start:
        return
    else:
        print(f"\"{novel.title}\" has {fetchedEnd - start} new chapter(s)!")

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

pool = ThreadPool(3)
pool.map(checkForNewChapters, reading)