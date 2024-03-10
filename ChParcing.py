import json
import time

from bs4 import BeautifulSoup
import requests
import os
import ttkbootstrap as tk
from tkinter import ttk


def get_dict_liters_from_main_url(url):
    """
    url: ссылка на главную страницу ресурса AmDm.ru для парсинга
    возвращает словарь {"Символ":"Ссылка", ...} для всех символов на главной странице ресурса
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(url, headers=headers)
        print(req)
        send = BeautifulSoup(req.text, "html.parser")
        div = send.find_all("div", class_="alphabet g-margin")

        bs_div = BeautifulSoup(str(div), "html.parser")
        search = bs_div.find_all("a")
        dict_liters = {i.text: url + i.get("href") for i in search}
        return dict_liters
    except Exception as msg:
        print(msg)
        return None


def get_all_artists_on_page(url):
    """
    url: ссылка на страницу со списком исполнителей
    возвращает словарь {"Исполнитель":"Ссылка", ...} для всех исполнителей на странице
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(url, headers=headers)
        send = BeautifulSoup(req.text, "html.parser")
        all_a = send.find_all("a", class_="artist")
        artists_dict = {}
        for i in all_a:
            artists_dict[i.text] = i.get("href")
        return artists_dict
    except Exception as msg:
        print(msg)
        return None


def get_all_songs_for_artist(url) -> dict:
    """
    url: ссылка на страницу исполнителя
    возвращает словарь {"Песня":"Ссылка", ...} для всех песен
    """
    def get_str_for_num(num):
        if num > 999:
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
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(url, headers=headers)
        send = BeautifulSoup(req.text, "html.parser")
        table = send.find("table", id="tablesort")
        all_a = table.find_all("a")
        song_dict = {}
        count = 0
        for i in all_a:
            count += 1
            song_dict[get_str_for_num(count) + " " + i.text] = i.get("href")
        return song_dict
    except Exception as msg:
        print(msg)
        return None


def item_selected(event, tree, queue_on_download: dict):
    # artist = tree.item(tree.selection(), option="values")[0]
    # stat_queue = tree.item(tree.selection(), option="values")[1]
    # link = tree.item(tree.selection(), option="values")[3]
    artist, stat_queue, _, link, parent = tree.item(tree.selection(), option="values")

    if artist != "Нет исполнителей":
        if stat_queue == "-":
            val = "В очереди"
            queue_on_download[artist] = (link, parent)
        else:
            val = "-"
            if artist in queue_on_download.keys():
                queue_on_download.pop(artist)
        tree.set(tree.selection(), column="#2", value=val)
        print(queue_on_download)


def load_artists_from_json():
    try:
        with open("main_data.json", "r") as f:
            data = json.load(f)
        # print(data)
        return data
    except FileNotFoundError as msg:
        print("Не могу прочитать файл. ", msg)
        return None


def reload_artists(app, main_url, queue_on_download):
    main_dict = {}
    dict_liters = get_dict_liters_from_main_url(main_url)  # получаем все литеры с ресурса в виде словаря {А: link, B: ...}
    if dict_liters:
        dict_liters_len = len(dict_liters)  # вычисляем количество литер
        count = 0
        for ident, link_lit in dict_liters.items():  # проходимся по словарю символов
            artist_dict = get_all_artists_on_page(link_lit)
            if artist_dict:
                lit_lib = {}
                for artist, link_art in artist_dict.items():  # проходимся по списку артистов
                    lit_lib[artist] = [link_art, ident]
                    # {artist1: [link_art1, parent], artist2: [...], ...}
                main_dict[ident] = [link_lit, lit_lib]
                # {A:[link, {artist1: [False, link_art1], artist2: [False, link_art2], ...}], B:[...], ... }
                del lit_lib
                count += 1
                v = int(count / dict_liters_len * 100)
                app.my_pr_bar.configure(value=v)
                app.my_pr_bar.update()
                app.my_st_bar.configure(text=f'[ОБНОВЛЕНИЕ СПИСКА ИСПОЛНИТЕЛЕЙ] Обновление "{ident}\"')
                # time.sleep(0.5)
        try:
            with open("main_data.json", "w") as f:
                json.dump(main_dict, f)
        except Exception as msg:
            print("Не могу записать в файл. ", msg)

        app_reload(app=app, main_url=main_url, queue_on_download=queue_on_download)
        print("Файл JSON создан")

    else:
        print("Невозможно получить данные с ресурса:", main_url)


def load_data_to_sheets(string_of_characters, frame, main_data, queue_on_download):

    def create_sheet_for_characters(book, txt):
        temp_frame = ttk.Frame(book)
        temp_frame.pack(fill=tk.BOTH, expand=True)
        book.add(temp_frame, text=txt, )
        tree = ttk.Treeview(temp_frame,
                            columns=("name", "check", "in_db", "link", "parent"),
                            show="headings",
                            # image=img
                            )
        tree.heading("name", text="Исполнитель", anchor=tk.W)
        tree.heading("check", text="Добавить", anchor=tk.W)
        tree.heading("in_db", text="В базе", anchor=tk.W)
        tree.heading("link", text="Ссылка", anchor=tk.W)
        tree.heading("parent", text="Родитель", anchor=tk.W)
        tree.column("#1", stretch=tk.NO, width=200)
        tree.column("#2", stretch=tk.NO, width=100)
        tree.column("#3", stretch=tk.NO, width=70)
        tree.column("#4", stretch=tk.NO, width=400)

        try:
            for art in main_data[txt][1]:
                tree.insert("", tk.END, values=(art,
                                                "-",
                                                "--",
                                                main_data[txt][1][art][0], # ссылка
                                                main_data[txt][1][art][1]  # родитель
                                                )
                            )
        except Exception as msg:
            tree.insert("", tk.END, values=("Нет исполнителей", "", "", ""))
            print("Загрузка локальных данных. Нет данных для:", msg)

        scroll = ttk.Scrollbar(temp_frame, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(expand=True, fill=tk.BOTH)
        tree.bind("<<TreeviewSelect>>",
                  lambda event, tree=tree, q=queue_on_download: item_selected(event, tree, q))
        book.update()

    if len(string_of_characters) > 0:
        book = ttk.Notebook(frame)
        book.enable_traversal()
        book.pack(expand=True, fill=tk.BOTH)
        if string_of_characters == "0..9":
            create_sheet_for_characters(book, string_of_characters)
        else:
            for i in string_of_characters:
                create_sheet_for_characters(book, i)
    else:
        print("ОШИБКА! load_data_to_sheets: нет строки на входе")


def app_reload(app, main_url, queue_on_download):
    if app:
        for i in app.pack_slaves():
            i.destroy()
        main_data = load_artists_from_json()
        init_widgets(app=app, main_url=main_url, main_data=main_data, queue_on_download=queue_on_download)


def clear_file_name(file_name: str) -> str:
    """
    Удаляет из входной строки символы, запрещённые в именах файлов
    :param file_name: str
    :return: str
    """
    bad_ch = """:'";"""
    new_str = ""
    for ch in file_name:
        if ch not in bad_ch:
            new_str += ch
    return new_str


def save_song_on_disc(app, art: str, song_dict: tuple, parent: str) -> None:
    print(song_dict)
    dir_name = os.path.join("DataLib", parent, art)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)                            # создаём папку под исполнителя
    file_name = art + " - " + str(song_dict[0])
    if app:
        app.my_st_bar.configure(text=f"[ЗАГРУЗКА] {file_name}")

    path = clear_file_name(os.path.join(dir_name, file_name + ".txt"))

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(song_dict[1], headers=headers)
    except Exception as msg:
        print(msg)
        return
    send = BeautifulSoup(req.text, "html.parser")
    with open(path, "w", encoding="utf-8") as f:
        search = send.find("h1")
        f.write(search.text)
        f.writelines("\n\n")
        f.write("*" * 60)
        f.writelines("\n\n")
        search = send.find_all("pre")
        for i in search:
            f.write(i.text)
            f.writelines("\n\n")
            f.write("*" * 60)
            f.writelines("\n\n")

    time.sleep(2)


def download_songs(main_url, queue_on_download, app):
    queue_len = len(queue_on_download)
    if queue_len:
        count = 0
        for art, art_list in queue_on_download.items():         # ПРОХОДИМ ПО ИСПОЛНИТЕЛЯМ
            songs_dict = get_all_songs_for_artist(art_list[0])
            if songs_dict:
                for item in songs_dict.items():                # ПРОХОДИМ ПО ПЕСНЯМ
                    save_song_on_disc(app=app, art=art, song_dict=item, parent=art_list[1])
            # Обновление значения ProgressBar
            count += 1
            v = int(count / queue_len * 100)
            if app:
                app.my_pr_bar.configure(value=v)
                app.my_pr_bar.update()
        queue_on_download.clear()
        # Обновляем окно
        if app:
            app_reload(app=app, main_url=main_url, queue_on_download=queue_on_download)
    else:
        print("Очередь загрузки пуста!")


def init_widgets(app, main_url, main_data, queue_on_download):
    string_1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string_2 = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    string_3 = "0..9"

    #    ПАНЕЛЬ ОПЦИЙ
    up_frame = ttk.LabelFrame(app, text="Опции")
    up_frame.pack(fill=tk.BOTH, expand=False)

    btn1 = ttk.Button(up_frame,
                      text="Обновить список артистов",
                      command=lambda: reload_artists(app=app,
                                                     main_url=main_url,
                                                     queue_on_download=queue_on_download))
    btn1.pack(side="left", padx=5, pady=5)

    btn2 = ttk.Button(up_frame,
                      text="Загрузить песни",
                      command=lambda: download_songs(main_url=main_url,
                                                     app=app,
                                                     queue_on_download=queue_on_download)
                      )
    btn2.pack(side="left", padx=5, pady=5)

    # btn3 = ttk.Button(up_frame,
    #                   text="**Обновить окно**",
    #                   command=lambda: app_reload(app=app,
    #                                              main_url=main_url,
    #                                              main_data=main_data,
    #                                              queue_on_download=queue_on_download)
    #                   )
    # btn3.pack(side="left", padx=5, pady=5)

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
    status_bar_text = "[Выберите исполнителей для скачивания и нажмите кнопку \"Загрузить песни\"]"
    status_bar = ttk.Frame(app)
    app.my_st_bar = ttk.Label(status_bar, text=status_bar_text, borderwidth=10, foreground="yellow")
    status_bar.pack(fill=tk.BOTH, expand=False)
    app.my_st_bar.pack(side="left")
    app.my_pr_bar = ttk.Progressbar(status_bar, bootstyle="success-striped", length=200)
    app.my_pr_bar.pack(side="right", padx=5)


def init_gui(main_url, main_data, queue_on_download):
    app = tk.Window(themename="superhero")
    app.title("Chords Parcing")
    app.geometry("1000x800")

    init_widgets(app, main_url, main_data, queue_on_download)

    app.mainloop()


def main():
    main_url = "https://amdm.j118.ru"
    queue_on_download = {}

    try:
        main_data = load_artists_from_json()
        init_gui(main_url, main_data, queue_on_download)
    except Exception as msg:
        print("ERROR!", msg)
    finally:
        if queue_on_download:
            print("Сохранение данных на диск")
            download_songs(main_url=main_url, queue_on_download=queue_on_download, app=None)


if __name__ == "__main__":
    main()
