# python 3.10

import json, os


# from Net import get_song_text, get_all_songs_for_artist, check_url, get_dict_liters_from_main_url, \
#     get_all_artists_on_page
#
# from AppGUI import logger, init_app, init_widgets

from Net import *
from AppGUI import *


from time import sleep
from datetime import datetime
from tkinter import messagebox as mes_box


# from PIL import Image, ImageTk


def reload_app(app):
    save_settings_to_disk(app)
    if app:
        for i in app.pack_slaves():
            i.destroy()
        app.my_main_data = load_artists_from_json()
        init_widgets(app)


def load_artists_from_json():
    try:
        with open("main_data.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError as msg:
        logger.error(f"Ошибка доступа к файлу: {msg}")


def save_main_data_to_json(app, main_dict):
    try:
        with open("main_data.json", "w") as f:
            json.dump(main_dict, f)
        logger.info(f"Файл JSON создан")
    except Exception as msg:
        logger.error(f"App is get Exception (Не могу записать в файл): {msg}")
        check_errors_count(app)
        app.errors_count += 1


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
        check_errors_count(app)
        app.errors_count += 1
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
            check_errors_count(app)
            app.errors_count += 1
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
            check_errors_count(app)
            app.errors_count += 1
            return

    # получаем текст песни
    send = get_song_text(app, song_dict)

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
        check_errors_count(app)
        app.errors_count += 1


def load_saved_data_from_json(app):
    try:
        with open("saved_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError as msg:
        logger.error(f"App is get Exception [Ошибка чтения файла saved_data.json]: {msg}")
        check_errors_count(app)
        app.errors_count += 1


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
        check_errors_count(app)
        app.errors_count += 1


def save_settings_to_json(app, data):
    try:
        with open("settings.json", "w") as f:
            json.dump(data, f)
    except Exception as msg:
        logger.error(f"App is get Exception [Ошибка записи файла settings.json]: {msg}")
        check_errors_count(app)
        app.errors_count += 1


def download_songs(app, dir):

    save_settings_to_disk(app)

    queue_len = len(app.queue_on_download)
    if queue_len:
        logger.info(f"Очередь загрузки: {app.queue_on_download}")
        logger.info(f"ЗАГРУЗКА ОЧЕРЕДИ НАЧАТА")
        if queue_len == 1: #  если в очереди только 1 элемент, значение ProgressBar устанавливаем в 50%
            app.my_pr_bar.configure(value=50)
            app.percent_label.configure(text="[ 50%]")
            app.my_pr_bar.update()
            app.title("[50%]" + app.window_title)
        count = 0
        black_list = []
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
                black_list.append(artist) # исполнители, которых не удалось сохранить
            # Обновление значения ProgressBar
            count += 1
            v = int(count / queue_len * 100)
            app.my_pr_bar.configure(value=v)
            app.percent_label.configure(text=f"[{v:3}%]")
            app.my_pr_bar.update()
            app.title(f"[{v:2}%]" + app.window_title)

        for artist in black_list:
            app.queue_on_download.pop(artist) # исключаем чёрный список из окончательной очереди

        app.saved_data.update(set(app.queue_on_download.keys()))  # Добавляем в множество сохранённых исполнителей
        update_saved_data_file(app)
        app.queue_on_download.clear()
        # Обновляем окно, если пользователь не закрывает приложение
        logger.info(f"ЗАГРУЗКА ОЧЕРЕДИ ЗАВЕРШЕНА")
        logger.info(f"ТЕКУЩАЯ СЕССИЯ ЛОГИРОВАНИЯ ЗАВЕРШЕНА")
        mes_box.showinfo("Информация", "Загрузка песен завершена")
        app.title(app.window_title)
        if not app.destroy_flag:
            reload_app(app)
    else:
        logger.error("ОЧЕРЕДЬ ЗАГРУЗКИ ПУСТА!")
        check_errors_count(app)
        app.errors_count += 1


def check_artist_in_base(download_dir, parent, artist):
    artist_path = os.path.join(download_dir, parent, artist)
    return True if os.path.isdir(artist_path) else False


def download_all_data(app):

    def get_all_data_queue(main_data):
        queue = {}
        for list_dict_ch in main_data.values():  # [{artist: [url, parent]}, ]
            for artist, (link, parent) in list_dict_ch[1].items():
                # if parent == "К": # ТЕСТ
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


def reload_artists(app):
    main_dict = {}
    dict_liters = get_dict_liters_from_main_url(app)  # получаем все литеры с ресурса
                                                                  # в виде словаря {А: link, B: ...}
    if dict_liters:
        dict_liters_len = len(dict_liters)  # вычисляем количество литер
        count = 0
        for ident, link_lit in dict_liters.items():  # проходимся по словарю символов
            artist_dict = get_all_artists_on_page(app, link_lit)  # получаем список исполнителей для каждой литеры
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
                app.title(f"[{v:2}%]" + app.window_title)
                # time.sleep(0.5)

        save_main_data_to_json(app, main_dict)

        app.title(app.window_title)
        reload_app(app)
        mes_box.showinfo("Информация", "Обновление списка исполнителей завершено")

    else:
        logger.error(f"Невозможно получить данные с ресурса: {app.my_main_url}")
        check_errors_count(app)
        app.errors_count += 1


def exec_dir_errors(event, app):
    try:
        path = os.getcwd() + "/logs/errors/"
        os.startfile(path)
    except Exception as msg:
        logger.error("App is get Exception: [Ошибка открытия директории] ", msg)
        check_errors_count(app)
        app.errors_count += 1


def check_errors_count(app):
    if app.errors_count:
        app.errors_count_label.configure(text=f"[Ошибок: {app.errors_count+1}]")
    else:
        app.errors_count_label.pack(side="right")
        app.errors_count_label.bind("<ButtonPress>", lambda event: exec_dir_errors(event, app))


def save_settings_to_disk(app):
    data = {}
    # data = load_settings_from_json()
    data["delay"] = app.my_delay
    data["main_url"] = app.my_main_url
    data["errors-last-session"] = app.errors_count
    data["completed_chars"] = list(app.completed_chars)
    save_settings_to_json(app, data)


def save_settings_button_press(app, set_top, entry_url, entry_delay):

    def check_delay(delay):
        # проверка задержки. delay - число вещественное, диапазон от 0 до 5
        try:
            result = float(delay)
            if not 0<=result<=5:
                result = None
        except ValueError:
            result = None
        return result

    result_check_url = check_url(app, entry_url.get())
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


def change_url(app, settings_window, new_url):
    # обрезаем последний слэш, если он есть
    if app.my_main_url[-1] == "/":
        cut_main_url = app.my_main_url[:-1]
    else:
        cut_main_url = app.my_main_url
    if new_url[-1] == "/":
        cut_new_url = new_url[:-1]
    else:
        cut_new_url = new_url

    new_main_data = {}
    for lit, lit_list in app.my_main_data.items():  # проходимся по словарю символов

        new_lit_list = []

        # замена в URL для букв
        new_lit_list.append(lit_list[0].replace(cut_main_url, cut_new_url))

        new_lit_dict = {}

        for art, art_list in lit_list[1].items(): # проходимся по словарю исполнителей
            new_art_list = []
            new_art_list.append(art_list[0].replace(cut_main_url, cut_new_url))      #замена в URL для исполнителей
            new_art_list.append(lit)
            new_lit_dict[art] = new_art_list

        new_lit_list.append(new_lit_dict)
        new_main_data[lit] = new_lit_list

    # dump main_data
    save_main_data_to_json(app, new_main_data)

    # change main_url
    app.my_main_url = new_url

    # reload app
    settings_window.destroy()
    reload_app(app)


def change_url_button_press(app, entry, settings_window):
    entry_value = entry.get()
    if check_url(app, entry_value):
        change_url(app, settings_window, entry_value)
    else:
        mes_box.showinfo("Внимание!", "Новый URL адрес недоступен. Операция отменена")
        if settings_window:
            settings_window.focus_set()


def main():
    main_data = load_artists_from_json()
    if main_data:
        init_app(main_data)


if __name__ == "__main__":
    main()
