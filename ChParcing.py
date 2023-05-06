from bs4 import BeautifulSoup
import requests
import re

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



if __name__ == "__main__":
    url = "https://amdm.ru" #input("Input Url with playlists Youtube: ")
    # get_dict_liters(url)
    get_artists_on_page()