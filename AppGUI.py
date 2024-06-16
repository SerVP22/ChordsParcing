from loguru import logger
import sys
import os
import ttkbootstrap as ttk_bs # Современная надстройка над ttk и tkinter
from tkinter import messagebox as mes_box
import pyautogui
import tkinter.ttk
from ChParcing import *
# from Net import check_url
# from ChParcing import download_songs, save_settings_to_disk, reload_artists, \
#     load_artists_from_json, download_all_data, save_settings_button_press, \
#     change_url_button_press, load_settings_from_json, load_saved_data_from_json,\
#     exec_dir_errors, check_errors_count
#

def init_widgets(app):
    def level_filter(level):
        def is_level(record):
            return record["level"].name == level

        return is_level

    logger.remove()

    logger.add(sys.stdout)

    logger.add("logs/info/info_{time}.log",
               format="{time} | {level} | {message}",
               filter=level_filter(level="INFO"),
               # rotation="callable"
               )
    logger.add("logs/errors/errors_{time}.log",
               format="{time} | {level} | {message}",
               filter=level_filter(level="ERROR"))

    logger.info("Приложение ЗАПУЩЕНО")


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

    btn4 = ttk_bs.Button(up_frame,
                         text="Проверить связь в порталом",
                         command=lambda: check_url_button_press(app)
                         )
    btn4.pack(side="left", padx=5, pady=5)

    btn10 = ttk_bs.Button(up_frame,
                         text="Настройки",
                         command=lambda: settings_button_press(app)
                        )
    btn10.pack(side="right", padx=5, pady=5)

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
    app.errors_count_label = ttk_bs.Label(status_bar, text="[Ошибок: 1]",borderwidth=10, foreground="red", cursor="hand2")

    if app.err_last_session:
        text = f"Предыдущая сессия была завершена с ошибками. \nКоличество ошибок: {app.err_last_session}. Хотите посмотреть логи?"
        if mes_box.askyesno("Внимание!", text):
            exec_dir_errors(None, app)


def settings_button_press(app:ttk_bs.Window):
    if "Toplevel" not in str(app.winfo_children()):

        set_top = ttk_bs.Toplevel(title="Настройки",
                                  topmost=False,
                                  resizable=(False,False))
        init_widgets_toplevel(set_top, app)

        set_top.update_idletasks()
        t_height = set_top.winfo_height()
        t_width = set_top.winfo_width()
        a_height = app.winfo_height()
        a_width = app.winfo_width()
        xpos = app.winfo_x() + ((a_width - t_width) // 2)
        ypos = app.winfo_y() + ((a_height - t_height) // 2)
        set_top.geometry(f'+{xpos}+{ypos}')
        # set_top.attributes("-topmost", True)


def destroy_app(app):
    if app.queue_on_download:  # Срабатывает, если в очереди есть хотя бы один исполнитель
        res = mes_box.askyesnocancel("Загрузить очередь скачивания?",
                                     """Окно приложения закроется. \nСкачать выбранных исполнителей?""")
        if res is True:  # Пользователь нажал "Да"
            app.destroy_flag = True
            download_songs(app, dir="DataLib")
    save_settings_to_disk(app)
    # app.quit()
    app.destroy()
    logger.info("Приложение ЗАКРЫТО")


def check_url_button_press(app):
    if check_url(app, app.my_main_url):
        mes_box.showinfo("Проверка связи", "Связь с порталом установлена успешно.")
    else:
        mes_box.showerror("Ошибка!",
                          "Связь с порталом не установлена!\nНеобходимо поменять главный URL в настройках программы")


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


def reload_artists_button_press(app):
    if mes_box.askyesnocancel("Обновление списка исполнителей", "Начать обновление списка исполнителей?"):
        reload_artists(app)


def notebook_tab_changed(event, book, app):
    pyautogui.moveTo(event.x_root, event.y_root)
    pyautogui.click()
    book.update()
    name = book.tab(book.select())["text"]
    if name[-1] == "*":
        name = name[:-2]
        app.completed_chars.discard(name)
    else:
        name += " *"
        app.completed_chars.add(name[:-2])
    book.tab(book.select(), text=name)
    # print(app.completed_chars)


def load_data_to_sheets(string_of_characters, frame, app):

    def create_sheet_for_characters(book: tkinter.ttk.Notebook, txt):
        temp_frame = ttk_bs.Frame(book)
        temp_frame.pack(fill=ttk_bs.BOTH, expand=True)

        if txt in app.completed_chars:
            sheet_name = txt + " *"
        else:
            sheet_name = txt

        book.add(temp_frame, text=sheet_name)
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
        # book.bind("<<NotebookTabChanged>>", lambda event: notebook_tab_changed(event, app))
        book.bind("<Button-3>", lambda event, book=book: notebook_tab_changed(event, book, app))
        book.pack(expand=True, fill=ttk_bs.BOTH)
        if string_of_characters == "0..9":
            create_sheet_for_characters(book, string_of_characters)
        else:
            for i in string_of_characters:
                create_sheet_for_characters(book, i)
    else:
        logger.error("[load_data_to_sheets]: нет строки на входе")
        check_errors_count(app)
        app.errors_count += 1



def download_all_data_button_press(app):
    if mes_box.askyesnocancel("Загрузка всего архива песен",
                              "Загрузка всего архива песен занимает продолжительное время. Продолжить операцию?"):
        download_all_data(app)


def init_widgets_toplevel(settings_window, app):

    frame1 = ttk_bs.LabelFrame(settings_window)
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

    frame2 = ttk_bs.LabelFrame(settings_window)
    frame2.pack(expand=True, fill="both")
    # Кнопка "Сохранить параметры)

    btn_save = ttk_bs.Button(frame2, text="Сохранить параметры", width=25, padding=5,
                             command=lambda: save_settings_button_press(app, settings_window, entry_url, entry_delay))
    btn_save.pack(anchor="center", pady=10)

    # Панель замены url в БД
    frame3 = ttk_bs.LabelFrame(settings_window, text=" Замена URL в базе данных ")
    frame3.pack(expand=True, fill="both", pady =10)
    entry_new_url = ttk_bs.Entry(frame3, width=30)
    update_url_btn = ttk_bs.Button(frame3, text="Подменить URL в БД на:", width=25, padding=5,
                                   command=lambda: change_url_button_press(app, entry_new_url, settings_window))
    update_url_btn.grid(column=0, row=0, columnspan=3, padx=50, pady=10)
    entry_new_url.grid(column=4, row=0, columnspan=3, padx=10, pady=10)


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


def init_app(main_data):
    DELAY = 0.1
    MAIN_URL = "https://amdm.ru"
    WINDOW_TITLE = "Chords Parcing"

    app = ttk_bs.Window(themename="superhero")

    app.completed_chars = set()
    app.my_main_data = main_data
    app.destroy_flag = False
    app.resave_data_option = ttk_bs.IntVar(value=0)
    app.queue_on_download = {}
    app.errors_count = 0
    app.window_title = WINDOW_TITLE

    settings = load_settings_from_json()
    if settings:
        app.my_delay = settings["delay"] # Задержка при цикличном обращении к сайту
        app.my_main_url = settings["main_url"]
        app.err_last_session = settings["errors-last-session"]
        app.completed_chars = set(settings["completed_chars"])
    else:
        app.my_delay = DELAY
        app.my_main_url = MAIN_URL

    try:
        app.saved_data = set(load_saved_data_from_json(app))
    except:
        app.saved_data = set()


    app.title(WINDOW_TITLE)
    app.geometry("1000x800")
    app.protocol("WM_DELETE_WINDOW", lambda: destroy_app(app))

    if main_data is None:
        first_start(app)
    else:
        init_widgets(app)


    app.mainloop()