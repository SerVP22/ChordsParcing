import json

from bs4 import BeautifulSoup
import requests
import re, os
# from GUITK import MyTkApp
import time
import tkinter as tk
from tkinter import ttk


def get_dict_liters(url):
    """
    url: ссылка на главную страницу ресурса AmDm.ru для парсинга
    возвращает словарь {"Символ":"Ссылка", ...} для всех символов на главной странице ресурса
    """
    req = requests.get(url)
    send = BeautifulSoup(req.text, "html.parser")
    div = send.find_all("div", class_="alphabet g-margin")
    bs_div = BeautifulSoup(str(div), "html.parser")
    search = bs_div.find_all("a")
    dict_liters = {i.text: url + i.get("href") for i in search}
    return dict_liters



def get_artists_on_page(url):
    """
    url: ссылка на страницу со списком исполнителей
    возвращает словарь {"Исполнитель":"Ссылка", ...} для всех исполнителей на странице
    """
    req = requests.get(url)
    send = BeautifulSoup(req.text, "html.parser")
    all_a = send.find_all("a", class_="artist")
    artists_dict = {}
    for i in all_a:
        # print(i.text, i.get("href"))
        artists_dict[i.text] = i.get("href")
    return artists_dict

def item_selected(self, event, tree):
    # print(event.widget)
    # print(tree.selection(), tree.index(tree.selection()))
    # print(tree.item(tree.selection(), option="values"))
    if tree.item(tree.selection(), option="values")[1] == "-":
        val = "Добавлено"
    else:
        val = "-"
    tree.set(tree.selection(), column="#2", value=val)

def in_db_gen(self, value):
    if value:
        return "Загружено"
    else:
        return "-"

def get_progress_bar_link(self):
    return self.pr_bar1

#def get_page_text(url="https://amdm.ru/akkordi/ddt/166093/prosvistela/"):
#     try:
#         req = requests.get(url)
#     except Exception as msg:
#         print(msg)
#         return
#     send = BeautifulSoup(req.text, "html.parser")
#     print(temp_dir_list := url.split("/")[-5:-1])  # ["akkordi", "ddt", "166093", "prosvistela"]
#     print(path := "\\".join(temp_dir_list[:-1]))  # akkordi\ddt\166093\
#     if not os.path.isdir(path):
#         os.makedirs(path)
#     file_name = os.path.join(path, temp_dir_list[-1]) + ".txt"
#     print(file_name)
#     with open(file_name, "w", encoding="cp1251") as f:
#         search = send.find("h1")
#         print(search.text)
#         f.write(search.text)
#         print("\n" + "*" * 60 + "\n")
#         f.writelines("\n\n")
#         f.write("*" * 60)
#         f.writelines("\n\n")
#         search = send.find_all("pre")
#         for i in search:
#             print(i.text)
#             f.write(i.text)
#             print("\n" + "*" * 60 + "\n")
#             f.writelines("\n\n")
#             f.write("*" * 60)
#             f.writelines("\n\n")

def reload_artists(pr_bar, url):
    main_dict = {}
    dict_liters = get_dict_liters(url) # получаем все литеры с ресурса в виде словаря {А: link, B: ...}
    #print(dict_liters)
    dict_liters_len = len(dict_liters) # вычисляем количество литер
    count = 0

    for ident, link_lit in dict_liters.items():  # проходимся по словарю символов
        artist_dict = get_artists_on_page(link_lit)
        #print(artist_dict)

        lit_lib = {}
        for artist, link_art in artist_dict.items():  # проходимся по списку артистов
            lit_lib[artist] = [False, link_art]
            # {artist1: [False, link_art1], artist2: [...], ...}

        main_dict[ident] = [link_lit, lit_lib]
        # {A:[link, {artist1: [False, link_art1], artist2: [False, link_art2], ...}], B:[...], ... }

        del lit_lib
        count += 1
        v = int(count / dict_liters_len * 100)
        #print(v)
        pr_bar.configure(value=v)
        pr_bar.update()

        time.sleep(0.5)

    with open("main_data.json", "w") as f:
        json.dump(main_dict, f)
    print("Файл JSON создан")


url = "https://amdm.in"
# get_dict_liters(url)
# print(get_artists_on_page())
# get_page_text()
app = tk.Tk()

app.title("Chords Parcing")
app.geometry("800x600")
string_1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
string_2 = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
string_3 = "0..9"
with open("main_data.json", "r") as f:
    main_data = json.load(f)

test_dict = main_data["А"][1]
#    ПАНЕЛЬ ОПЦИЙ
up_frame = ttk.LabelFrame(app, text="Опции")
up_frame.pack(fill=tk.BOTH, expand=False)
# self.upfr_label_pic = tk.Label(self.up_frame, height=3)
# self.upfr_label_pic.pack(side="left")
pr_bar1 = ttk.Progressbar(up_frame, length=100)
pr_bar1.pack(side="left")
btn1 = ttk.Button(up_frame,
                  text="Обновить список артистов",
                  command=lambda: reload_artists(pr_bar=pr_bar1, url=url))
btn1.pack(side="left")
#     ПАНЕЛЬ НАВИГАЦИИ
down_frame = ttk.LabelFrame(app, text="Исполнители", )
down_frame.pack(fill=tk.BOTH, expand=True)
main_book = ttk.Notebook(down_frame, padding=5)
main_book.pack(expand=True, fill=tk.BOTH)
frame1 = ttk.Frame(main_book)
frame2 = ttk.Frame(main_book)
frame3 = ttk.Frame(main_book)
frame1.pack(fill=tk.BOTH, expand=True)
frame2.pack(fill=tk.BOTH, expand=True)
frame3.pack(fill=tk.BOTH, expand=True)
main_book.add(frame2, text="    Русские буквы (А..Я)    ")
if len(string_2) > 0:
    rus_book = ttk.Notebook(frame2)
    rus_book.enable_traversal()
    rus_book.pack(expand=True, fill=tk.BOTH)
    for i in string_2:
        temp_frame = ttk.Frame(rus_book)
        temp_frame.pack(fill=tk.BOTH, expand=True)
        rus_book.add(temp_frame, text=i, underline=0)
        ttk.Label(temp_frame, text=f"test for {i} letter").pack()
        if i == "А":
            tree = ttk.Treeview(temp_frame,
                                columns=("name", "check", "in_db", "link"),
                                show="headings",
                                # image=img
                                )
            tree.heading("name", text="Исполнитель", anchor=tk.W)
            tree.heading("check", text="Добавить", anchor=tk.W)
            tree.heading("in_db", text="В базе", anchor=tk.W)
            tree.heading("link", text="Ссылка", anchor=tk.W)
            tree.column("#1", stretch=tk.NO, width=200)
            tree.column("#2", stretch=tk.NO, width=100)
            tree.column("#3", stretch=tk.NO, width=70)
            tree.column("#4", stretch=tk.NO, width=400)
            for char, data in test_dict.items():
                if i == char:
                    for artist, data_art in data[1].items():
                        tree.insert("", tk.END, values=(artist,
                                                             "-",
                                                             in_db_gen(data_art[0]),
                                                             data_art[1]))
            scroll = ttk.Scrollbar(temp_frame, command=tree.yview)
            tree.configure(yscrollcommand=scroll.set)
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(expand=True, fill=tk.BOTH)
            tree.bind("<<TreeviewSelect>>", lambda event, tree=tree: item_selected(event, tree))
main_book.add(frame1, text="    Английские буквы (A..Z)    ")
if len(string_1) > 0:
    eng_book = ttk.Notebook(frame1)
    eng_book.enable_traversal()
    eng_book.pack(expand=True, fill=tk.BOTH)
    for i in string_1:
        temp_frame = ttk.Frame(eng_book)
        temp_frame.pack(fill=tk.BOTH, expand=True)
        eng_book.add(temp_frame, text=i, underline=0)
        ttk.Label(temp_frame, text=f"test for {i} letter").pack()
main_book.add(frame3, text="    Цифровые символы (0..9)    ")
if len(string_3) > 0:
    digit_book = ttk.Notebook(frame3)
    digit_book.enable_traversal()
    digit_book.pack(expand=True, fill=tk.BOTH)
    temp_frame = ttk.Frame(digit_book)
    temp_frame.pack(fill=tk.BOTH, expand=True)
    digit_book.add(temp_frame, text=string_3, underline=0)
    ttk.Label(temp_frame, text=f"test for digits").pack()

app.mainloop()


"""

class MyTkApp(tk.Tk):

    def __init__(self):



    

class ChPar(MyTkApp):

    def __init__(self, main_page):
        self.main_page = main_page
        self.main_dict = {"А":
                        [
                            "https://amdm.ru/chords/1/",
                            {
                                # словарь исполнителей
                                "TestArtist": [True, "TestURL"]
                            }
                        ]
                     }

        #self.GUI = super().__init__(self.main_dict)
        self.GUI = MyTkApp()
        self.GUI.mainloop()
        self.GUI.test_dict = self.main_dict


    

    

"""


