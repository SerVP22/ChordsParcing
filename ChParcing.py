# python 3.10

import json

from log import logger, level_filter
from time import sleep
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import os
import ttkbootstrap as ttk_bs # Современная надстройка над ttk и tkinter
from tkinter import messagebox as mes_box
# from PIL import Image, ImageTk


def get_dict_liters_from_main_url(url):
    """
    url: ссылка на главную страницу ресурса AmDm.ru для парсинга
    возвращает словарь {"Символ":"Ссылка", ...} для всех символов на главной странице ресурса
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(url, headers=headers)
        logger.info(f"App is get response: {req}")
        send = BeautifulSoup(req.text, "html.parser")
        div = send.find_all("div", class_="alphabet g-margin")

        bs_div = BeautifulSoup(str(div), "html.parser")
        search = bs_div.find_all("a")
        dict_liters = {i.text: url + i.get("href") for i in search}
        return dict_liters
    except Exception as msg:
        logger.error(f"App is get Exception: {msg}")
        return


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
        logger.error(f"App is get Exception: {msg}")
        return


def get_all_songs_for_artist(app, url) -> dict | None:
    """
    url: ссылка на страницу исполнителя
    возвращает словарь {"Песня":"Ссылка", ...} для всех песен
    """

    def parse_error(msg):
        """
        Функция извлекает из текста ошибки новый URL страницы исполнителя
        :param msg: объект текста ошибки исключения
        :return:str
        """
        msg = str(msg)
        start = msg.find("/")
        end = msg.rfind("/", start) + 1
        return msg[start:end]

    def get_str_for_num(num):
        """
        Добавляет в название песни нули к номеру песни по порядку ( 1 -> 0001 )

        :param num: int
        :return: str
        """
        if num > 9999:
            logger.error(f"Превышено количество песен для директории")
            return ""
        else:
            str_num = str(num)
            if len(str_num) == 4:
                return str_num
            elif len(str_num) == 3:
                return "0" + str_num
            elif len(str_num) == 2:
                return "00" + str_num
            else:
                return "000" + str_num

    # url = check_url_and_main_url(app, url)

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    try:
        req = requests.get(url, headers=headers, allow_redirects=True)
    except Exception as msg:
        new_url = app.my_main_url + parse_error(msg)
        try:
            req = requests.get(new_url, headers=headers, allow_redirects=True)
        except:
            logger.error(f"App is get Exception:\n{msg}")
            return

    send = BeautifulSoup(req.text, "html.parser")
    table = send.find("table", id="tablesort")
    all_a = table.find_all("a")
    song_dict = {}
    count = 0
    for i in all_a:
        count += 1
        song_dict[get_str_for_num(count) + " " + i.text] = i.get("href")
    return song_dict


def item_selected(event, tree, app):

    def invert_item_state():
        if stat_queue == "-":
            val = "В очереди"
            app.queue_on_download[artist] = (link, parent)
            logger.info(f"Исполнитель \"{artist}\" добавлен в очередь скачивания")
        else:
            val = "-"
            if artist in app.queue_on_download.keys():
                app.queue_on_download.pop(artist)
                logger.info(f"Исполнитель \"{artist}\" удалён из очереди скачивания")
        tree.set(tree.selection(), column="#2", value=val)


    # Получаем значения из таблицы
    artist, stat_queue, _, link, parent = tree.item(tree.selection(), option="values")

    if artist != "Нет исполнителей":
        if app.resave_data_option.get() == 0:          # Если отключена опция "Перезапись данных",
            if artist not in app.saved_data:    # то проверяем наличие исполнителя в списке загруженных
                invert_item_state()
        elif app.resave_data_option.get() == 1:
            invert_item_state()


def load_artists_from_json():
    try:
        with open("main_data.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError as msg:
        logger.error(f"Ошибка доступа к файлу: {msg}")


def reload_artists_button_press(app):
    if mes_box.askyesnocancel("Обновление списка исполнителей", "Начать обновление списка исполнителей?"):
        reload_artists(app)


def reload_artists(app):
    main_dict = {}
    dict_liters = get_dict_liters_from_main_url(app.my_main_url)  # получаем все литеры с ресурса
                                                                  # в виде словаря {А: link, B: ...}
    if dict_liters:
        dict_liters_len = len(dict_liters)  # вычисляем количество литер
        count = 0
        for ident, link_lit in dict_liters.items():  # проходимся по словарю символов
            artist_dict = get_all_artists_on_page(link_lit)  # получаем список исполнителей для каждой литеры
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
                app.percent_label.configure(text=f"[{v:3}%]")
                app.my_pr_bar.update()
                app.my_st_bar.configure(text=f'[ОБНОВЛЕНИЕ СПИСКА ИСПОЛНИТЕЛЕЙ] Обновление "{ident}\"')
                app.my_st_bar.update()
                # time.sleep(0.5)
        try:
            with open("main_data.json", "w") as f:
                json.dump(main_dict, f)
            logger.info(f"Файл JSON создан")
        except Exception as msg:
            logger.error(f"App is get Exception (Не могу записать в файл): {msg}")

        reload_app(app)
        mes_box.showinfo("Информация", "Обновление списка исполнителей завершено")

    else:
        logger.error(f"Невозможно получить данные с ресурса: {app.my_main_url}")

def load_data_to_sheets(string_of_characters, frame, app):

    def create_sheet_for_characters(book, txt):
        temp_frame = ttk_bs.Frame(book)
        temp_frame.pack(fill=ttk_bs.BOTH, expand=True)
        book.add(temp_frame, text=txt, )
        tree = ttk_bs.Treeview(temp_frame,
                            columns=("name", "check", "in_db", "link", "parent"),
                            displaycolumns=("name", "check", "in_db", "link"),
                            show="headings",
                            selectmode=ttk_bs.BROWSE
                            # image=img
                            )
        tree.heading("name", text="Исполнитель", anchor=ttk_bs.W)
        tree.heading("check", text="Добавить", anchor=ttk_bs.W)
        tree.heading("in_db", text="В базе", anchor=ttk_bs.W)
        tree.heading("link", text="Ссылка", anchor=ttk_bs.W)
        tree.heading("parent", text="Родитель", anchor=ttk_bs.W)
        tree.column("#1", stretch=ttk_bs.NO, width=200)
        tree.column("#2", stretch=ttk_bs.NO, width=100)
        tree.column("#3", stretch=ttk_bs.NO, width=70)
        tree.column("#4", stretch=ttk_bs.NO, width=400)

        try:
            for art in app.my_main_data[txt][1]:
                tree.insert("", ttk_bs.END, values=(art,
                                                "-",
                                                "Загружен" if art in app.saved_data else "--",
                                                app.my_main_data[txt][1][art][0], # ссылка
                                                app.my_main_data[txt][1][art][1]  # родитель
                                                )
                            )
        except Exception as msg:
            tree.insert("", ttk_bs.END, values=("Нет исполнителей", "", "", "", ""))
            logger.info(f"Загрузка локальных данных. Нет данных для: {msg}")

        scroll = ttk_bs.Scrollbar(temp_frame, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=ttk_bs.RIGHT, fill=ttk_bs.Y)
        tree.pack(expand=True, fill=ttk_bs.BOTH)
        tree.bind("<<TreeviewSelect>>", lambda event: item_selected(event, tree, app))
        book.update()

    if len(string_of_characters) > 0:
        book = ttk_bs.Notebook(frame, bootstyle="dark")
        book.enable_traversal()
        book.pack(expand=True, fill=ttk_bs.BOTH)
        if string_of_characters == "0..9":
            create_sheet_for_characters(book, string_of_characters)
        else:
            for i in string_of_characters:
                create_sheet_for_characters(book, i)
    else:
        logger.error("[load_data_to_sheets]: нет строки на входе")

def reload_app(app):
    if app:
        for i in app.pack_slaves():
            i.destroy()
        app.my_main_data = load_artists_from_json()
        init_widgets(app)


def clear_file_name(file_name: str) -> str:
    """
    Удаляет из входной строки символы, запрещённые в именах файлов
    :param file_name: str
    :return: str
    """
    bad_ch = """:"><*?|\n\t"""
    new_str = ""
    for ch in file_name:
        if ch in "\/":
            new_str += "-"
        else:
            if ch not in bad_ch:
                new_str += ch
    return new_str


def check_lenght_name(path):
    return len(path)<=255


def save_song_on_disk(app, art: str, song_dict: tuple, parent: str, dir: str) -> None:
    """

    :param app: Ссылка на объект приложения
    :param art: Название исполнителя
    :param song_dict: кортеж (название песни, ссылка на песню)
    :param parent: Литера, к которой относится исполнитель
    :param dir: Название директории для сохранения базы файлов
    :return: None
    """

    logger.info(f"Запись на диск: {song_dict}")
    artist = clear_file_name(art.strip())
    dir_name = os.path.join(dir, parent, artist)

    # создаём папку под исполнителя
    try:
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
    except OSError as msg1: # недопустимая длина пути
        logger.error(f"App is get Exception OSError: {msg1}")
        dir_name = os.path.join(dir, parent, artist.split()[0]) # Обрезаем название исполнителя.
                                                                # Новое название - первое слово названия
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        # Создаём файл с информацией об исходном имени исполнителя
        try:
            info_file_name = os.path.join(dir_name, "[INFO].txt")
            with open(info_file_name, "w", encoding="utf-8") as f:
                f.writelines(f"Исходное название исполнителя: {artist}")
        except Exception as msg2:
            logger.error(f"App is get Exception: {msg2}")
    # проверка на длину имени файла
    song_name = clear_file_name(str(song_dict[0]))
    file_name = artist + " - " + song_name
    app.my_st_bar.configure(text=f"[ЗАГРУЗКА ПЕСЕН] {file_name}")
    app.my_st_bar.update()
    path = os.path.join(dir_name, file_name + ".txt")
    work_dir = os.getcwd()
    modify_artist = artist
    while not check_lenght_name(os.path.join(work_dir + path)):
        splitted_name_artist = modify_artist.split()
        modify_artist = " ".join(splitted_name_artist[0:-1])
        file_name = modify_artist + " - " + song_name
        path = os.path.join(dir_name, file_name + ".txt")
        if len(splitted_name_artist)<2:
            logger.error(f"[СЛИШКОМ ДЛИННОЕ ИМЯ ФАЙЛА] {path}")
            return

    # получаем текст песни
    url_song = song_dict[1]  # check_url_and_main_url(app, song_dict[1])
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(url_song, headers=headers)
    except Exception as msg3:
        logger.error(f"App is get Exception [Ошибка запроса по адресу песни] {msg3}")
        return
    send = BeautifulSoup(req.text, "html.parser")

    # пишем текст песни в файл
    try:
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
    except Exception as msg4:
        logger.error(f"App is get Exception [Ошибка записи файла песни]: {msg4}")
        logger.error(f"[DEBUG] {work_dir + path}")
        return


def load_saved_data_from_json():
    try:
        with open("saved_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError as msg:
        logger.error(f"App is get Exception [Ошибка чтения файла saved_data.json]: {msg}")
        return


def load_settings_from_json():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError as msg:
        logger.error(f"App is get Exception [Ошибка чтения файла settings.json]: {msg}")
        return {}
    except Exception as msg:
        logger.error(f"App is get Exception [Нет данных из файла settings.json]: {msg}")
        return {}

def update_saved_data_file(app):
    try:
        with open("saved_data.json", "w") as f:
            json.dump(list(app.saved_data), f)
    except Exception as msg:
        logger.error(f"App is get Exception [Ошибка записи в файл saved_data.json]: {msg}")

def save_settings_to_json(data):
    try:
        with open("settings.json", "w") as f:
            json.dump(data, f)
    except Exception as msg:
        logger.error(f"App is get Exception [Ошибка записи файла settings.json]: {msg}")


# def errors_count_

def download_songs(app, dir):

    # def save_last_artist(artist):
    #     data = load_settings_from_json()
    #     data["last_artist"] = artist
    #     save_settings_to_json(data)


    queue_len = len(app.queue_on_download)
    if queue_len:
        logger.info(f"Очередь загрузки: {app.queue_on_download}")
        logger.info(f"ЗАГРУЗКА ОЧЕРЕДИ НАЧАТА")
        if queue_len == 1: #  если в очереди только 1 элемент, значение ProgressBar устанавливаем в 50%
            app.my_pr_bar.configure(value=50)
            app.percent_label.configure(text="[ 50%]")
            app.my_pr_bar.update()
        count = 0
        for artist, artist_list in app.queue_on_download.items():         # ПРОХОДИМ ПО ИСПОЛНИТЕЛЯМ

            # save_last_artist(art) # сохранение текущего исполнителя в качестве последнего
            url_artist = artist_list[0]
            parent_char = artist_list[1]

            songs_dict = get_all_songs_for_artist(app, url_artist)
            if songs_dict:
                for item in songs_dict.items():                # ПРОХОДИМ ПО ПЕСНЯМ
                    save_song_on_disk(app=app, art=artist, song_dict=item, parent=parent_char, dir=dir)
                    if app.my_delay:
                        sleep(app.my_delay)
            else:
                app.queue_on_download.pop(artist)
                queue_len -= 1
            # Обновление значения ProgressBar
            count += 1
            v = int(count / queue_len * 100)
            app.my_pr_bar.configure(value=v)
            app.percent_label.configure(text=f"[{v:3}%]")
            app.my_pr_bar.update()

        app.saved_data.update(set(app.queue_on_download.keys()))  # Добавляем в множество сохранённых исполнителей
        update_saved_data_file(app)
        app.queue_on_download.clear()
        # Обновляем окно, если пользователь не закрывает приложение
        if not app.destroy_flag:
            reload_app(app)
        logger.info(f"ЗАГРУЗКА ОЧЕРЕДИ ЗАВЕРШЕНА")
        mes_box.showinfo("Информация", "Загрузка песен завершена")
    else:
        logger.error("ОЧЕРЕДЬ ЗАГРУЗКИ ПУСТА!")


def download_all_data_button_press(app):
    if mes_box.askyesnocancel("Загрузка всего архива песен",
                              "Загрузка всего архива песен занимает продолжительное время. Продолжить операцию?"):
        download_all_data(app)


def check_artist_in_base(download_dir, parent, artist):
    artist_path = os.path.join(download_dir, parent, artist)
    return True if os.path.isdir(artist_path) else False

def download_all_data(app):

    def get_all_data_queue(main_data):
        queue = {}
        for list_dict_ch in main_data.values():  # [{artist: [url, parent]}, ]
            for artist, (link, parent) in list_dict_ch[1].items():
                if parent == "К": # ТЕСТ
                    if app.resave_data_option.get():
                        queue[artist] = (link, parent)
                    else:
                        if not check_artist_in_base(download_dir, parent, artist):
                            queue[artist] = (link, parent)
                # print(artist, link, parent)
        return queue


    download_dir = "AmDm_Data"
    logger.info("Загрузка всех данных. Начало операции")
    start_time = datetime.now()

    # В очередь закачки добавляем всех исполнителей из main_data
    app.queue_on_download.clear()
    app.queue_on_download = get_all_data_queue(app.my_main_data)
    # print(app.queue_on_download)
    download_songs(app, dir=download_dir)

    delta = datetime.now() - start_time
    logger.info(f"Загрузка всех данных. Конец операции. Продолжительность (сек.): {delta.total_seconds()}")
    app.queue_on_download.clear()


def invert_resave_data(app):
    app.resave_data_option = not app.resave_data_option


def save_settings_to_disk(app):
    data = load_settings_from_json()
    data["delay"] = app.my_delay
    data["main_url"] = app.my_main_url
    save_settings_to_json(data)


def save_settings_button_press(app, set_top, entry_url, entry_delay):

    def check_url(url):
        # проверка существования адреса
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            requests.get(url, headers=headers)
        except Exception as msg:
            logger.error(f"App is get Exception [Ошибка запроса при проверке URL]: {msg}")
            return
        return url

    def check_delay(delay):
        # проверка задержки. delay - число вещественное, диапазон от 0 до 5
        try:
            result = float(delay)
            if not 0<=result<=5:
                result = None
        except ValueError:
            result = None
        return result

    result_check_url = check_url(entry_url.get())
    result_check_delay = check_delay(entry_delay.get())

    if result_check_url and not result_check_delay is None:
        app.my_delay = result_check_delay
        app.my_main_url = result_check_url
        save_settings_to_disk(app)
        set_top.destroy()
    elif result_check_url and result_check_delay is None:
        mes_box.showerror("Ошибка значения",
                          "Задержка может быть только в диапазоне от 0 до 5 сек",
                          parent=set_top)
        entry_delay.focus()
    elif not result_check_url and not result_check_delay is None:
        mes_box.showerror("Ошибка значения", "Указанный адрес не существует", parent=set_top)
        entry_url.focus()
    elif not result_check_url and result_check_delay is None:
        mes_box.showerror("Ошибка значений",
                          "Указанный адрес не существует. \nЗадержка может быть только в диапазоне от 0 до 5 сек",
                          parent=set_top)
        entry_url.focus()


def init_widgets_toplevel(set_top, app):

    frame1 = ttk_bs.LabelFrame(set_top)
    frame1.pack(expand=True, fill="both")
    # Установка URL
    label_url = ttk_bs.Label(frame1, text="URL главной страницы AmDm.ru:", anchor="e", width=40)
    label_url.grid(column=0, row=0, columnspan=3, padx=10, pady=10)
    entry_url = ttk_bs.Entry(frame1, width=30)
    entry_url.insert(0, str(app.my_main_url))
    entry_url.grid(column=4, row=0, columnspan=3, padx=10, pady=10)
    # Установка задержки при запросах на сервер
    label_delay = ttk_bs.Label(frame1, text="Задержка при запросах на сервер (сек):", anchor="e", width=40)
    label_delay.grid(column=0, row=1, columnspan=3, padx=10, pady=10)
    entry_delay = ttk_bs.Entry(frame1, width=30)
    entry_delay.insert(0, str(app.my_delay))
    entry_delay.grid(column=4, row=1, columnspan=3, padx=10, pady=10)

    frame2 = ttk_bs.LabelFrame(set_top)
    frame2.pack(expand=True, fill="both")
    # Кнопка "Сохранить параметры)

    btn_save = ttk_bs.Button(frame2, text="Сохранить параметры", width=25, padding=5,
                             command=lambda: save_settings_button_press(app, set_top, entry_url, entry_delay))
    btn_save.pack(anchor="center", pady=10)


def settings_button_press(app:ttk_bs.Window):
    if "Toplevel" not in str(app.winfo_children()):

        set_top = ttk_bs.Toplevel(title="Настройки", topmost=True, resizable=(False,False))
        init_widgets_toplevel(set_top, app)

        set_top.update_idletasks()
        t_height = set_top.winfo_height()
        t_width = set_top.winfo_width()
        a_height = app.winfo_height()
        a_width = app.winfo_width()
        xpos = app.winfo_x() + ((a_width - t_width) // 2)
        ypos = app.winfo_y() + ((a_height - t_height) // 2)
        set_top.geometry(f'+{xpos}+{ypos}')
        set_top.attributes("-topmost", True)

def exec_dir_errors(event):
    try:
        path = os.getcwd() + "/logs/errors/"
        os.startfile(path)
    except Exception as msg:
        logger.error("App is get Exception: [Ошибка открытия директории] ", msg)

def init_widgets(app):
    # if not logger.id_error:
    #     logger.remove(1)
    #     logger.add("logs/errors/errors_{time}.log",
    #                format="{time} | {level} | {message}",
    #                filter=level_filter(level="ERROR"))

    string_1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string_2 = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    string_3 = "0..9"
    # with Image.open("img/dnld.png") as img_d:
    #     dnld_img = ImageTk.PhotoImage(image=img_d, size=(16, 16))




    #    ПАНЕЛЬ ОПЦИЙ
    up_frame = ttk_bs.LabelFrame(app, text="Опции", padding=5)
    up_frame.pack(fill=ttk_bs.BOTH, expand=False)

    btn2 = ttk_bs.Button(up_frame,
                         text="Загрузить песни",
                         # image=dnld_img,
                         command=lambda: download_songs(app, dir="DataLib")
                         )
    btn2.pack(side="left", padx=5, pady=5)

    btn1 = ttk_bs.Button(up_frame,
                         text="Обновить список артистов",
                         command=lambda: reload_artists_button_press(app)
                         )
    btn1.pack(side="left", padx=5, pady=5)

    btn3 = ttk_bs.Button(up_frame,
                         text="Скачать весь архив с сайта",
                         command=lambda: download_all_data_button_press(app)
                         )
    btn3.pack(side="left", padx=5, pady=5)

    btn3 = ttk_bs.Button(up_frame,
                         text="Настройки",
                         command=lambda: settings_button_press(app)
                        )
    btn3.pack(side="right", padx=5, pady=5)

    ch_but = ttk_bs.Checkbutton(up_frame,
                                text="Перезапись исполнителей",
                                variable=app.resave_data_option,
                                offvalue=0,
                                onvalue=1
                                )
    ch_but.pack(side="right", padx=5, pady=5)

    #     ПАНЕЛЬ НАВИГАЦИИ ПО ИСПОЛНИТЕЛЯМ
    middle_frame = ttk_bs.LabelFrame(app, text="Исполнители", )
    middle_frame.pack(fill=ttk_bs.BOTH, expand=True)
    main_book = ttk_bs.Notebook(middle_frame, padding=5, bootstyle="dark")
    main_book.pack(expand=True, fill=ttk_bs.BOTH)
    frame1 = ttk_bs.Frame(main_book)
    frame2 = ttk_bs.Frame(main_book)
    frame3 = ttk_bs.Frame(main_book)

    frame2.pack(fill=ttk_bs.BOTH, expand=True)
    main_book.add(frame2, text="    Русские буквы (А..Я)    ")
    load_data_to_sheets(string_2, frame2, app)
    frame1.pack(fill=ttk_bs.BOTH, expand=True)
    main_book.add(frame1, text="    Английские буквы (A..Z)    ")
    load_data_to_sheets(string_1, frame1, app)
    frame3.pack(fill=ttk_bs.BOTH, expand=True)
    main_book.add(frame3, text="    Цифровые символы (0..9)    ")
    load_data_to_sheets(string_3, frame3, app)

    #     СТРОКА СОСТОЯНИЯ
    status_bar_text = "[Выберите исполнителей для скачивания и нажмите кнопку \"Загрузить песни\"]"
    status_bar = ttk_bs.Frame(app)
    app.my_st_bar = ttk_bs.Label(status_bar, text=status_bar_text, borderwidth=10, foreground="yellow")
    status_bar.pack(fill=ttk_bs.BOTH, expand=False, padx=10)
    app.my_st_bar.pack(side="left")
    app.my_pr_bar = ttk_bs.Progressbar(status_bar, bootstyle="success-striped", length=200)
    app.my_pr_bar.pack(side="right", padx=5)
    app.percent_label = ttk_bs.Label(status_bar, text="[  0%]", borderwidth=10, foreground="white")
    app.percent_label.pack(side="right")
    app.errors_count = ttk_bs.Label(status_bar, text="[Ошибок: 0]", borderwidth=10, foreground="red", cursor="hand2")
    app.errors_count.pack(side="right")
    app.errors_count.bind("<ButtonPress>", exec_dir_errors)

def destroy_app(app):
    if app.queue_on_download:  # Срабатывает, если в очереди есть хотя бы один исполнитель
        res = mes_box.askyesnocancel("Загрузить очередь скачивания?",
                                     """Окно приложения закроется. \nСкачать выбранных исполнителей?""")
        if res is True:  # Пользователь нажал "Да"
            app.destroy_flag = True
            download_songs(app, dir="DataLib")
    app.destroy()
    logger.info("Приложение ЗАКРЫТО")
def first_start(app):

    def ask(app):
        mes_box_text = f"Начать загрузку исполнителей c ресурса {app.my_main_url}?"
        if mes_box.askyesnocancel("Загрузка исполнителей", mes_box_text) and app.my_main_url:
            reload_artists(app)

    up_frame = ttk_bs.Frame(app)
    up_frame.pack(anchor="n", fill=ttk_bs.BOTH, expand=True, padx=10)

    # Страница ABOUT

    #     СТРОКА СОСТОЯНИЯ
    status_bar_text = "[Вы зашли в программу в первый раз. Необходимо загрузить исполнителей]"
    status_bar = ttk_bs.Frame(app)
    app.my_st_bar = ttk_bs.Label(status_bar, text=status_bar_text, borderwidth=10, foreground="yellow")
    status_bar.pack(anchor="n", fill=ttk_bs.BOTH, expand=False, padx=10)
    app.my_st_bar.pack(side="left")

    app.my_pr_bar = ttk_bs.Progressbar(status_bar, bootstyle="success-striped", length=200)
    app.my_pr_bar.pack(side="right", padx=5)


    ttk_bs.Button(status_bar, text="Начать загрузку", command=lambda: ask(app)).pack(side="right", padx=5)

    ask(app)


def init_gui(main_url, main_data, delay):
    app = ttk_bs.Window(themename="superhero")
    app.my_main_url = main_url
    app.my_main_data = main_data
    app.destroy_flag = False
    app.resave_data_option = ttk_bs.IntVar(value=0)
    app.my_delay = delay  # Задержка при цикличном обращении к сайту
    app.queue_on_download = {}
    try:
        app.saved_data = set(load_saved_data_from_json())
    except:
        app.saved_data = set()


    app.title("Chords Parcing")
    app.geometry("1000x800")
    app.protocol("WM_DELETE_WINDOW", lambda: destroy_app(app))

    if main_data is None:
        first_start(app)
    else:
        init_widgets(app)

    app.mainloop()


def main():
    logger.info("Приложение ЗАПУЩЕНО")
    # DEFAULT

    delay = 0.1
    main_url = "https://amdm.ru"

    settings = load_settings_from_json()
    if settings:
        delay = settings["delay"]
        main_url = settings["main_url"]
    main_data = load_artists_from_json()
    init_gui(main_url, main_data, delay)


if __name__ == "__main__":
    main()
