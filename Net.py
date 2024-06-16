from bs4 import BeautifulSoup
import requests
# from AppGUI import logger
# from ChParcing import check_errors_count

def get_dict_liters_from_main_url(app):
    """

    возвращает словарь {"Символ":"Ссылка", ...} для всех символов на главной странице ресурса
    """
    url = app.my_main_url
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
        check_errors_count(app)
        app.errors_count +=1


def get_all_artists_on_page(app, url):
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
        check_errors_count(app)
        app.errors_count += 1


def get_all_songs_for_artist(app, url) -> dict | None:
    """
    url: ссылка на страницу исполнителя
    возвращает словарь {"Песня":"Ссылка", ...} для всех песен
    """

    def parse_error(app, msg):
        """
        Функция извлекает из текста ошибки новый URL страницы исполнителя
        :param msg: объект текста ошибки исключения
        :return:str
        """
        msg = str(msg)
        shift = 0
        if app.my_main_url[-1] == "/":
            shift = 1
        start = msg.find("/") + shift
        end = msg.rfind("/", start) + 1
        return msg[start:end]

    def get_str_for_num(app, num):
        """
        Добавляет в название песни нули к номеру песни по порядку ( 1 -> 0001 )

        :param num: int
        :return: str
        """
        if num > 9999:
            logger.error(f"Превышено количество песен для директории")
            check_errors_count(app)
            app.errors_count += 1
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
        new_url = app.my_main_url + parse_error(app, msg)
        print(new_url)
        try:
            req = requests.get(new_url, headers=headers, allow_redirects=True)
        except:
            logger.error(f"App is get Exception:\n{msg}")
            check_errors_count(app)
            app.errors_count += 1
            return

    send = BeautifulSoup(req.text, "html.parser")
    table = send.find("table", id="tablesort")
    if table:
        all_a = table.find_all("a")
        song_dict = {}
        count = 0
        for i in all_a:
            count += 1
            song_dict[get_str_for_num(app, count) + " " + i.text] = i.get("href")
        return song_dict
    else:
        logger.error("Ошибка содержимого на странице исполнителя. Список песен не найден")
        check_errors_count(app)
        app.errors_count += 1
        return


def get_song_text(app, song_dict):
    url_song = song_dict[1]  # check_url_and_main_url(app, song_dict[1])
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(url_song, headers=headers)
    except Exception as msg3:
        logger.error(f"App is get Exception [Ошибка запроса по адресу песни] {msg3}")
        check_errors_count(app)
        app.errors_count += 1
        return
    return BeautifulSoup(req.text, "html.parser")


def check_url(app, url):
    # проверка существования адреса
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        requests.get(url, headers=headers)
    except Exception as msg:
        logger.error(f"App is get Exception [Ошибка запроса при проверке URL]: {msg}")
        check_errors_count(app)
        app.errors_count += 1
        return
    return url