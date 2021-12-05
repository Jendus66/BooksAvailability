import json
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from lxml import html
import os
import config



class Bookmarks():
    def __init__(self, path, bookmark_folder):
        self.path = path
        self.bookmark_folder = bookmark_folder
        if config.verbose:
            print("Chrome bookmarks file path")
            print(self.path)
    
    def get_books_urls(self):
        json_data = json.loads(open(self.path, encoding='utf-8').read())
        urls = []
        for child in json_data["roots"]["bookmark_bar"]["children"]:
            if child["name"].lower() == self.bookmark_folder:
                for j in child["children"]:
                    if j["type"] == "url":
                        urls.append(j["url"])
        if config.verbose:
            print("URLs from Chrome bookmarks")
            print(urls)
        return urls



class DatabazeKnih():
    def __init__(self, books_urls):
        self.books_urls = books_urls
        self.books_data = []
    
    def get_books_data(self):
        for i in self.books_urls:
            if "databazeknih" in i:
                dict_temp = {}
                r = requests.get(i)
                soup = BeautifulSoup(r.content, "html.parser")
                title = soup.find("h1", attrs={"itemprop": "name"}).get_text()
                author = soup.find("span", attrs={"itemprop": "author"}).get_text()
                url = i
                dict_temp["nazev"] = unidecode(title)
                dict_temp["autor"] = unidecode(author)
                dict_temp["url"] = url
                self.books_data.append(dict_temp)
        if config.verbose:
            print(f"Books data from DatabazeKnih")
            print(self.books_data)

        return self.books_data



class kkVysociny():
    def __init__(self, books_data):
        self.books_data = books_data
        self.library_data = []
    
    def get_data(self):
        for book in self.books_data:
            #print("dohledávám data v katalogu kk Vysočiny - " + book["nazev"])
            nazev = str(book["nazev"]).replace(" ", "+")
            autor = str(book["autor"]).replace(" ", "+")
            url = f"https://tritius.kkvysociny.cz/advanced?area=87&rows%5B0%5D.searchFieldItem=-13&rows%5B0%5D.value={autor}" \
                f"&rows%5B1%5D.searchFieldItem=-32&rows%5B1%5D.value={nazev}" \
                "&rows%5B2%5D.searchFieldItem=-30&rows%5B2%5D.value=&rows%5B3%5D.searchFieldItem=-71&rows%5B3%5D.value=&allsrc=on&_" \
                "csrf=1b9850dc-f2c2-4e7b-b14f-a4d45259ef4c"
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            try:
                vysledky = soup.select_one(".pagination-info").text
                pocet_vysledku = int(vysledky.split(" ")[-1][0:-1])
                if pocet_vysledku > 20:
                    pocet_vysledku = 20
                for i in range(1, (pocet_vysledku + 1)):
                    dict_vysledky = {}
                    try:
                        cizo = soup.select_one(
                            f"div.result:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(8) > span:nth-child(1) > span:nth-child(2) > a:nth-child(1)").text
                        if unidecode(cizo) != "cizojazycne texty":
                            raise AttributeError("Tento vysledek je relevantni.")
                    except AttributeError:
                        dict_vysledky["Nazev"] = soup.select_one(
                            f"div.result:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1) > a:nth-child(1) > span:nth-child(1) > span:nth-child(1)").text
                        stav = unidecode(soup.select_one(
                            f"div.result:nth-child({i}) > div:nth-child(2) > div:nth-child(1) > span:nth-child(2)").text)
                        href = soup.select_one(
                            f"div.result:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1) > a:nth-child(1)")[
                            "href"]
                        dict_vysledky["Odkaz"] = "https://tritius.kkvysociny.cz" + href
                        if stav == "Vypujcene":
                            url = "https://tritius.kkvysociny.cz" + href
                            termin = self.get_end_of_book_loan(url)
                            dict_vysledky["Stav"] = stav
                            dict_vysledky["Termin"] = termin
                        else:
                            stav = "K dispozici"
                            termin = ["Dnes"]
                            dict_vysledky["Stav"] = stav
                            dict_vysledky["Termin"] = termin
                        self.library_data.append(dict_vysledky)
            except AttributeError:
                dict_vysledky = {"Nazev": str(book["nazev"]) + " / " + str(book["autor"]), "Stav": "Nenalezeno",
                                "Termin": ["Nenalezeno"], "Odkaz": "Nenalezeno"}
                self.library_data.append(dict_vysledky)
        
        if config.verbose:
            print(f"Books and their availability in library")
            print(self.library_data)

        return self.library_data

    @staticmethod
    def get_end_of_book_loan(url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        pocet_svazku = int(soup.select_one("a.mark:nth-child(1)").text)
        tree = html.fromstring(r.content)
        terminy = []
        for i in range(1, pocet_svazku + 1):
            vypujcka_text = tree.xpath(
                f"/html/body/div[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div/div/table/tbody/tr/td/div/div/div[1]/table/tbody/tr[{i}]/td[5]//text()")[
                0]
            vypujcka = str(vypujcka_text).split(" ")[-1]
            terminy.append(vypujcka)
        return terminy



if __name__ == "__main__":
    path = "~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks"
    path = os.path.expanduser(path)
    bookmarks_urls = Bookmarks(path, config.bookmarks_folder).get_books_urls()
    books_data = DatabazeKnih(bookmarks_urls).get_books_data()
    library_data = kkVysociny(books_data).get_data()