from bs4 import BeautifulSoup
import requests
import re, os

def get_dict_liters(url):
    req = requests.get(url)
    send = BeautifulSoup(req.text, "html.parser")
    div = send.find_all("div", class_="alphabet g-margin")
    bs_div = BeautifulSoup(str(div), "html.parser")
    search = bs_div.find_all("a")
    dict_liters = {i.text:url + i.get("href") for i in search}
    print(dict_liters)
    return dict_liters

def get_artists_on_page(url="https://amdm.ru/chords/3/"):
    req = requests.get(url)
    send = BeautifulSoup(req.text, "html.parser")
    all_a = send.find_all("a", class_="artist")
    for i in all_a:
        print(i.text, i.get("href"))

def get_page_text(url = "https://amdm.ru/akkordi/ddt/166093/prosvistela/"):
    try:
        req = requests.get(url)
    except Exception as msg:
        print(msg)
        return
    send = BeautifulSoup(req.text, "html.parser")

    print(temp_dir_list := url.split("/")[-5:-1]) # ["akkordi", "ddt", "166093", "prosvistela"]
    print(path := "\\".join(temp_dir_list[:-1])) #akkordi\ddt\166093\
    if not os.path.isdir(path):
        os.makedirs(path)
    file_name = os.path.join(path, temp_dir_list[-1]) + ".txt"

    print(file_name)

    with open(file_name, "w", encoding="cp1251") as f:
        search = send.find("h1")
        print(search.text)
        f.write(search.text)
        print("\n" + "*" * 60 + "\n")
        f.writelines("\n\n")
        f.write("*" * 60)
        f.writelines("\n\n")
        search = send.find_all("pre")
        for i in search:
            print(i.text)
            f.write(i.text)
            print("\n" + "*" * 60 + "\n")
            f.writelines("\n\n")
            f.write("*" * 60)
            f.writelines("\n\n")

if __name__ == "__main__":
    url = "https://amdm.ru" #input("Input Url with playlists Youtube: ")
    # get_dict_liters(url)
    # get_artists_on_page()
    get_page_text()