import json

from bs4 import BeautifulSoup
import requests
#import re, os
# from GUITK import MyTkApp
#import time
#import tkinter as tk
import ttkbootstrap as tk
from tkinter import ttk


def get_dict_liters_from_main_url(url):
    """
    url: ссылка на главную страницу ресурса AmDm.ru для парсинга
    возвращает словарь {"Символ":"Ссылка", ...} для всех символов на главной странице ресурса
    """
    try:
        req = requests.get(url)
        send = BeautifulSoup(req.text, "html.parser")
        div = send.find_all("div", class_="alphabet g-margin")
        bs_div = BeautifulSoup(str(div), "html.parser")
        search = bs_div.find_all("a")
        dict_liters = {i.text: url + i.get("href") for i in search}
        return dict_liters
    except:
        return None



def get_all_artists_on_page(url):
    """
    url: ссылка на страницу со списком исполнителей
    возвращает словарь {"Исполнитель":"Ссылка", ...} для всех исполнителей на странице
    """
    try:
        req = requests.get(url)
        send = BeautifulSoup(req.text, "html.parser")
        all_a = send.find_all("a", class_="artist")
        artists_dict = {}
        for i in all_a:
            artists_dict[i.text] = i.get("href")
        return artists_dict
    except:
        return None

def get_all_songs_for_artist(url = "https://amdm.in/akkordi/aleksandr_marshal/"):
    """
    url: ссылка на страницу исполнителя
    возвращает словарь {"Песня":"Ссылка", ...} для всех песен
    """
    def get_str_for_num(num):
        if num>999:
            print("Ого! Не может быть такого количества песен!")
        else:
            str_num = str(num)
            if len(str_num) == 3:
                return str_num
            elif len(str_num) == 2:
                return "0" + str_num
            else:
                return "00" + str_num

    try:
        req = requests.get(url)
        send = BeautifulSoup(req.text, "html.parser")
        table = send.find("table", id="tablesort")
        all_a = table.find_all("a")
        song_dict = {}
        count = 0
        for i in all_a:
            count+=1
            song_dict[get_str_for_num(count) + " " + i.text] = i.get("href")
        return song_dict
    except Exception as msg:
        print(msg)
        return None

def item_selected(event, tree, queue_on_download):
    # artist = tree.item(tree.selection(), option="values")[0]
    # stat_queue = tree.item(tree.selection(), option="values")[1]
    # link = tree.item(tree.selection(), option="values")[3]
    artist, stat_queue, _, link = tree.item(tree.selection(), option="values")

    if stat_queue == "-":
        val = "В очереди"
        queue_on_download[artist] = link
    else:
        val = "-"
        queue_on_download.pop(artist)
    tree.set(tree.selection(), column="#2", value=val)
    print(queue_on_download)

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

def load_artists_from_JSON():
    try:
        with open("main_data.json", "r") as f:
            data = json.load(f)
        # print(data)
        return data
    except FileNotFoundError as msg:
        print("Не могу прочитать файл. ", msg)
        return None
def reload_artists(pr_bar, url):
    main_dict = {}
    dict_liters = get_dict_liters_from_main_url(url) # получаем все литеры с ресурса в виде словаря {А: link, B: ...}
    if dict_liters:
        dict_liters_len = len(dict_liters) # вычисляем количество литер
        count = 0
        for ident, link_lit in dict_liters.items():  # проходимся по словарю символов
            artist_dict = get_all_artists_on_page(link_lit)
            if artist_dict:
                lit_lib = {}
                for artist, link_art in artist_dict.items():  # проходимся по списку артистов
                    lit_lib[artist] = [link_art]
                    # {artist1: [link_art1], artist2: [...], ...}
                main_dict[ident] = [link_lit, lit_lib]
                # {A:[link, {artist1: [False, link_art1], artist2: [False, link_art2], ...}], B:[...], ... }
                del lit_lib
                count += 1
                v = int(count / dict_liters_len * 100)
                pr_bar.configure(value=v)
                pr_bar.update()
                # time.sleep(0.5)
        try:
            with open("main_data.json", "w") as f:
                json.dump(main_dict, f)
        except Exception as msg:
            print("Не могу записать в файл. ", msg)


        print("Файл JSON создан")
    else:
        print("Невозможно получить данные с ресурса:", url)


def load_data_to_sheets(work_string, frame, main_data, queue_on_download):

    def create_sheet_for_literas(book, txt):
        temp_frame = ttk.Frame(book)
        temp_frame.pack(fill=tk.BOTH, expand=True)
        book.add(temp_frame, text=txt, )
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

        try:
            for art in main_data[txt][1]:
                tree.insert("", tk.END, values=(art, "-", "--", main_data[txt][1][art][0]))
        except Exception as msg:
            print("Нет данных:", msg)

        scroll = ttk.Scrollbar(temp_frame, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(expand=True, fill=tk.BOTH)
        tree.bind("<<TreeviewSelect>>",
                  lambda event, tree=tree, q=queue_on_download: item_selected(event, tree, q))
        book.update()

    if len(work_string) > 0:
        book = ttk.Notebook(frame)
        book.enable_traversal()
        book.pack(expand=True, fill=tk.BOTH)
        if work_string == "0..9":
            create_sheet_for_literas(book, work_string)
        else:
            for i in work_string:
                create_sheet_for_literas(book, i)
    else:
        print("ОШИБКА! load_data_to_sheets: нет строки на входе")

def init_GUI(main_url, main_data, queue_on_download):
    app = tk.Window(themename="superhero")
    app.title("Chords Parcing")
    app.geometry("1000x800")
    string_1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string_2 = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    string_3 = "0..9"

    #    ПАНЕЛЬ ОПЦИЙ
    up_frame = ttk.LabelFrame(app, text="Опции")
    up_frame.pack(fill=tk.BOTH, expand=False)
    pr_bar1 = ttk.Progressbar(up_frame, length=100)
    pr_bar1.pack(side="left")
    btn1 = ttk.Button(up_frame,
                      text="Обновить список артистов",
                      command=lambda: reload_artists(pr_bar=pr_bar1, url=main_url))
    btn1.pack(side="left")

    #     ПАНЕЛЬ НАВИГАЦИИ
    middle_frame = ttk.LabelFrame(app, text="Исполнители", )
    middle_frame.pack(fill=tk.BOTH, expand=True)
    main_book = ttk.Notebook(middle_frame, padding=5)
    main_book.pack(expand=True, fill=tk.BOTH)
    frame1 = ttk.Frame(main_book)
    frame2 = ttk.Frame(main_book)
    frame3 = ttk.Frame(main_book)
    frame1.pack(fill=tk.BOTH, expand=True)
    frame2.pack(fill=tk.BOTH, expand=True)
    frame3.pack(fill=tk.BOTH, expand=True)
    main_book.add(frame2, text="    Русские буквы (А..Я)    ")
    load_data_to_sheets(string_2, frame2, main_data, queue_on_download)
    main_book.add(frame1, text="    Английские буквы (A..Z)    ")
    load_data_to_sheets(string_1, frame1, main_data, queue_on_download)
    main_book.add(frame3, text="    Цифровые символы (0..9)    ")
    load_data_to_sheets(string_3, frame3, main_data, queue_on_download)

    #     СТРОКА СОСТОЯНИЯ
    status_bar_text = "Загрузка данных из собственной базы данных..."
    status_bar = ttk.Frame(app)
    status_bar_label = ttk.Label(status_bar, text=status_bar_text, borderwidth=10)
    status_bar.pack(fill=tk.BOTH, expand=False)
    status_bar_label.pack(side="left")

    app.mainloop()

def main():
    main_url = "https://amdm.in"
    queue_on_download = {}

    try:
        main_data = load_artists_from_JSON()
        init_GUI(main_url, main_data, queue_on_download)
    finally:
        print("Сохранение данных на диск")
        for art, link in queue_on_download.items():
            for i in get_all_songs_for_artist(link).items():
                print(i)

if __name__ == "__main__":
    main()
