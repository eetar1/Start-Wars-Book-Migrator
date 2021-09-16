import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pymongo
from dotenv import load_dotenv

TITLE_IDX = 2
YEAR_IDX = 0
AUTHOR_IDX = 3
RELEASE_IDX = 4
TYPE_IDX = 1


def extractFromTable(table, era):
    eraBookList = []
    for row in table.findAll("tr")[1:]:
        # Get the txt from the bs4 object
        rowContents = str(row.getText()).split('\n')
        rowContents = [x for x in rowContents if len(x) > 0]
        if len(rowContents) > 5:
            rowContents.pop(3)

        # Add number so that improper dates can be formatted
        while len(rowContents[RELEASE_IDX].split("-")) < 3:
            rowContents[RELEASE_IDX] += '-01'

        released = datetime.strptime(rowContents[RELEASE_IDX], "%Y-%m-%d")

        book = dict(title=rowContents[TITLE_IDX], author=rowContents[AUTHOR_IDX], year=rowContents[YEAR_IDX],
                    type=rowContents[TYPE_IDX], era=era, releasedate=released, owned=False)
        eraBookList.append(book)
    return eraBookList


def defGetPage():
    resp = requests.get('https://starwars.fandom.com/wiki/Timeline_of_Legends_books')
    soup = BeautifulSoup(resp.text, 'html.parser')
    tables = soup.findAll("table")[4:11]

    # Pull the eras from the table of contents and remove the number
    eras = soup.find(id='toc').find("ul").findAll("li")
    eras = [x.getText()[2:] for x in eras]
    eraCnt = 0
    rows = list()

    for table in tables:
        rows += extractFromTable(table, eras[eraCnt])
        eraCnt += 1

    return rows


def putToDb(data, mycol):
    mycol.insert_many(data)


def main(URI):
    # Get books from https://starwars.fandom.com/wiki/Timeline_of_Legends_books
    data = defGetPage()
    # Connect to mysql db
    myclient = pymongo.MongoClient(URI)
    mydb = myclient.Cluster0
    mycol = mydb.starwarsbooks
    putToDb(data, mycol)


if __name__ == '__main__':
    load_dotenv()
    MONGO_URI = os.getenv('MONGO_URI')
    main(MONGO_URI)
