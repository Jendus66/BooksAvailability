import tkinter as tk
from tkinter import ttk
import webbrowser
import kkVysociny
import config



class MainApplication(tk.Frame):
    def __init__(self, parent, library_data):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.library_data = library_data
        self.scrollable_frame = ScrollableFrame(parent)
        self.window_settings()
        self.create_header()
        self.create_labels()
        self.scrollable_frame.pack()
        self.parent.focus_force()
    
    def window_settings(self):
        self.parent.title("Dostupnost knih")
        self.parent.geometry("625x625")
        self.parent.resizable(False,False)

    def create_labels(self):
        row = 1
        for book in self.library_data:
            book_name_raw = book["Nazev"].split(";")
            book_name, book_author = book_name_raw[0].split("/")
            book_author = book_author.strip()[0:20]
            book_name = book_name[0:40]
            book_url = book["Odkaz"]
            gap = 1

            for term in book["Termin"]:

                lbl_name = ttk.Label(self.scrollable_frame.scrollable_frame, text=book_name, background="#f6f0f5")
                lbl_name.grid(column=0, row = row, sticky="ew", padx=10, pady=gap)

                lbl_author = ttk.Label(self.scrollable_frame.scrollable_frame, text=book_author, background="#f6f0f5")
                lbl_author.grid(column=1, row = row, sticky="ew", padx=10, pady=gap)

                lbl_term = ttk.Label(self.scrollable_frame.scrollable_frame, text=term)
                lbl_term.grid(column=2, row = row, sticky="ew", padx=10, pady=gap)

                if term == "Dnes":
                    lbl_term.config(background="#d2f536")
                elif term == "Nenalezeno":
                    lbl_term.config(background="black", foreground="white")
                else:
                    lbl_term.config(background="#f77274")

                btn = ttk.Button(self.scrollable_frame.scrollable_frame, text="Odkaz do knihovny", command= lambda book_url=book_url: self.open_url(book_url))
                btn.grid(column=3, row = row, pady=gap)

                if book["Stav"] == "Nenalezeno":
                    btn["state"] = "disabled"

                row = row + 1
    
    def create_header(self):
        font=('Helvetica', 11, 'bold')
        bg = "#f6f0f5"
        lbl_name = ttk.Label(self.scrollable_frame.scrollable_frame, text="Kniha", font=font, background=bg)
        lbl_name.grid(column=0, row = 0, sticky="ew", padx=10)

        lbl_author = ttk.Label(self.scrollable_frame.scrollable_frame, text="Autor", font=font, background=bg)
        lbl_author.grid(column=1, row = 0, sticky="ew", padx=10)

        lbl_term = ttk.Label(self.scrollable_frame.scrollable_frame, text="Termín", font=font, background=bg)
        lbl_term.grid(column=2, row = 0, sticky="ew", padx=10)

    def open_url(self, url):
        webbrowser.open_new(url)



class IntroWindow(tk.Frame):
    def __init__(self, parent):
        self.frame = tk.Frame.__init__(self, parent)
        self.parent = parent
        self.window_settings()
        self.create_widgets()

    def call_app(self):
        data = kkVysociny.main()
        if data == -1:
            self.no_connection_window("Nejsi připojena k internetu")
        elif data:
            self.but.destroy()
            self.lbl_text.destroy()
            self.lbl_text2.destroy()
            MainApplication(self.parent, data).pack(side="top", fill="both", expand=True)
        elif not data:
            self.no_connection_window("Žádná data k zobrazení")
    
    def window_settings(self):
        self.parent.geometry("550x550")
        self.parent.title("Dostupnost knih")
        self.parent.resizable(False,False)

        self.background = tk.PhotoImage(file=config.gui_background)
        Lbl_background = tk.Label(self.frame,image=self.background)
        Lbl_background.place(x=0, y=0, relwidth=1, relheight=1)
        
    def create_widgets(self):
        self.lbl_text = tk.Label(self.frame, text=f"Záložky v Chrome musí být ve složce s názvem '{config.bookmarks_folder}'.", bg="#f2f5f3")
        self.lbl_text.pack()

        self.lbl_text2 = tk.Label(self.frame, text="Odkazy mimo databazeknih.cz nebudou dohledány.", bg="#f2f5f3")
        self.lbl_text2.pack()

        self.but = tk.Button(self.parent, text="Načíst data", command=self.call_app, bg="#f6f0f5", fg="#6e4f61", font=('Helvetica', 11, 'bold'))
        self.but.pack(pady=10)
    
    def no_connection_window(self, text):
        win = tk.Toplevel(self.parent)
        win.geometry("300x50")
        win.resizable(False,False)
        win.focus_force()
        lbl_text = tk.Label(win, text=text)
        lbl_text.pack(pady=10)



class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, height=600, width=600, bg="#f6f0f5")
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f6f0f5")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
