from bs4 import BeautifulSoup
import requests, re

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

chapterUrl = input('Chapter URL: ')
startChapter = int(input('Start Chapter: '))
endChapter = int(input('End Chapter: '))
file = None

for i in range(startChapter, endChapter + 1):
  url = f"{chapterUrl}{i}"
  res = requests.get(url, headers=headers, cookies=cookies)
  soup = BeautifulSoup(res.text, 'html.parser')
  title = soup.find(['p'], class_=["novel_subtitle"]).get_text().strip()
  progress = soup.find(['div'], id=["novel_no"]).get_text().strip()
  if i == startChapter:
    header = soup.find(['div'], class_=["contents1"])
    novelTitle = header.findAll(['a'])[0].get_text().strip()
    novelTitle = novelTitle[:40]
    author = header.findAll(['a'])[1].get_text().strip()
    file = open(f'{author}{startChapter}-{endChapter}:{novelTitle}.txt', 'w')
    file.write(chapterUrl + '\n')
    # test
  sectionTitle = soup.find(['div'], class_=["contents1"]).find(['p'])
  if sectionTitle:
    sectionTitle = sectionTitle.get_text().strip()
    file.write(f"{title}\n{sectionTitle}\n{progress}\n")
  else:
    file.write(f"{title}\n{progress}\n")
  chapterP = soup.find(id='novel_p')
  if chapterP:
    print(re.sub(r'\n+', '\n', chapterP.get_text()), file=file)
  paragraphs = soup.find(id='novel_honbun').select('p')
  for paragraph in paragraphs:
    print(re.sub(r'\n+', '\n', paragraph.get_text()), file=file)
    images = paragraph.find_all('img')
    if images:
      src = images[0]['src']
      print(f'Image: {src}', file=file)
  chapterA = soup.find(id='novel_a')
  if chapterA:
    print(re.sub(r'\n+', '\n', chapterA.get_text()), file=file)
  file.write('\n\n')
  print(f'Chapter {i} downloaded')