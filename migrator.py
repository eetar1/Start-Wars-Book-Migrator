import requests
from bs4 import BeautifulSoup
import pymongo


def defGetPage():
    resp = requests.get('https://starwars.fandom.com/wiki/Timeline_of_Legends_books')
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.findAll("table")[4]
    rows = list()

    # Initial inits these vars sometimes have to be used from previous rows
    author = ''
    timeline = ''
    title = ''
    released = ''

    for row in table.findAll("tr")[2:]:
        # Get the txt from the bs4 object
        rowContents = str(row.getText())
        rowContents = rowContents.split("\n")
        rowContents = [x for x in rowContents if len(x) > 0]

        # Normal row with all 4 properties
        if len(rowContents) > 3:
            timeline = rowContents[0]
            title = rowContents[1]
            author = rowContents[2]
            released = rowContents[3]
            dateLen = len(released.split("-"))

            # Fix weird dates missing month and day
            while dateLen < 3:
                released += '-01'
                dateLen += 1

        # Row is missing time line or author
        elif len(rowContents) > 2:
            # Fix weird dates
            released = rowContents[-1]
            dateLen = len(released.split("-"))
            while dateLen < 3:
                released += '-01'
                dateLen += 1
            #  Check if the author or timeline is the missing use the previous values
            if 'BBY' in rowContents[0] or 'ABY' in rowContents[0]:
                title = rowContents[1]
                timeline = rowContents[0]
            else:
                title = rowContents[0]
                author = rowContents[1]

        # Both author and timeline are missing use the previous values
        elif len(rowContents) > 1:
            title = rowContents[0]
            released = rowContents[-1]
            released = str(released)
            dateLen = len(released.split("-"))
            while dateLen < 3:
                released += '-01'
                dateLen += 1

        # Non title row means it a book append it to the list
        if len(rowContents) > 1:
            book = dict(timeline=timeline, title=title, author=author, released=released)
            rows.append(book)
    return rows


def putToDb(data, mycol):
    mycol.insert_many(data)



def main():
    # Get books from https://starwars.fandom.com/wiki/Timeline_of_Legends_books
    data = defGetPage()
    # Connect to mysql db
    myclient = pymongo.MongoClient("<URI>")

    mydb = myclient["Cluster0"]
    mycol = mydb["starwarsBooks"]
    putToDb(data, mycol)


if __name__ == '__main__':
    main()
