import requests
from chrome_classes import Bookmarks, DatabazeKnih, kkVysociny
import tkinter as tk
import chrome_gui
import config


def connection_check():
    try:
        requests.get("https://www.google.com/", timeout=1)
        return True
    except requests.ConnectionError:
        return False

def main():
    if connection_check():
        path = config.bookmarks_path
        bookmarks_urls = Bookmarks(path, "knihy").get_books_urls()
        books_data = DatabazeKnih(bookmarks_urls).get_books_data()
        library_data = kkVysociny(books_data).get_data()
        return library_data
    else:
        return -1


if __name__=="__main__":
    root = tk.Tk()
    chrome_gui.IntroWindow(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
