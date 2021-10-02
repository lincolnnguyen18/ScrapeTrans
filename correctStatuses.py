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
category = [f"ncode" for file in ncode] + [f"novel18" for file in novel18]
alreadyDownloaded = [novel[:-4] for novel in ncode + novel18]
progress = 1

categoryForTitle = dict(zip(alreadyDownloaded, category))
# print(categoryForTitle)

for novel in novels:
    if novel.title not in alreadyDownloaded:
        # print(f"{novel.title} not found!")
        continue
    # print(novel.title)
    # print(categoryForTitle[novel.title])
    # print(novel)
    path = categoryForTitle[novel.title]
    filePath = f"{path}/{novel.title}.txt"
    file = codecs.open(filePath, 'r', "utf-8")
    for line in reversed(file.readlines()):
        if 'Chapter number:' in line:
            # print(novel.title)
            start = line.replace("Chapter number: ", "").split('/')[0].strip()
            end = line.replace("Chapter number: ", "").split('/')[1].strip()
            # print(line.strip())
            # print(start)
            # print(end)
            novel.status = f"{start}/{end}"
            break

updateLibrary(novels)