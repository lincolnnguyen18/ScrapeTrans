# ScrapeTrans

A personal project I worked on months ago to scrape novels from Syosetu then merge, clean, and split them for DeepL translation. To use, simply add a new line under "To Read" and above "Reading" in library.txt in the following format:

```plain
[nCode] [English title]
```

Example:

```plain
n9350eg The reincarnated nobleman has great ambitions! You're in good company, give it to me.
```

After that (you may have to install the requests Python library), run

```bash
python3 fetchNovels.py
```

to fetch the Japanese raws into a toTranslate folder. The files have to be submitted to DeepL.com for translation. Place the translated files into the created translated folder then run

```bash
python3 mergeNovels.py
```

this will merge the English and Japanese line by line for easier cross referencing when reading and place the merged novel text files into either the ncode or novel18 folders.

Initial fetches will only fetch up to 100,000 characters of chapters. Any fetches afterwards will fetch how ever many chapters remain. Fetching of chapters will update the current chapter counter in the library.txt file.

Remove temporary files after confirming merging completed successfully by running

```bash
python3 cleanup.py
```

To check if there are any new chapters based on the counter stored in your library.txt file, run

```bash
python3 checkForUpdates.py
```
