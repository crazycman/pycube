from time import sleep
from typing import List, Dict

import requests
import shutil
import json


def get_abbot():
    p = {"exact": "Abbot of Keral Keep"}  # fuzzy
    r = requests.get("https://api.scryfall.com/cards/named", params=p)
    print(r.url)
    # r.status_code
    # r.text
    s = r.json()
    imgs = s.get("image_uris")
    # print(imgs)
    art_url = imgs.get("art_crop")
    art_req = requests.get(art_url, stream=True)
    if art_req.status_code == 200:
        with open("the_image.jpg", "wb") as f:
            art_req.raw.decode_content = True
            shutil.copyfileobj(art_req.raw, f)


# save image see https://stackoverflow.com/questions/13137817/how-to-download-image-using-request
# search for a named card
# https://api.scryfall.com/cards/named?fuzzy=aust+com

def get_card_scry(parameters, wait=False):
    """
    Query the scryfall API for a specific card.
    :param wait: Set to True, to insert a wait before a request; see https://api.scryfall.com/docs/api
    :param parameters: Dict of request parameters
    :return: Card as JSON (as returned by the scryfall API)
    """
    if wait:
        sleep(0.1)
    json = requests.get("https://api.scryfall.com/cards/named", params=parameters).json()
    print("{}".format(json.get("name")))
    return json


def get_cards_scry(card_names):
    return list(map(lambda x: get_card_scry({"fuzzy": x}, True), card_names))


def get_modern_cube_cards():
    card_names = read_cards_file("resources/modern-cube.txt").split(sep='\n')
    return get_cards_scry(card_names)


def get_modern_cube_cards_scry() -> List[object]:
    """
    Get all the cards in the Modern Cube via the scryfall API
    """
    # https://api.scryfall.com/cards/search?q=cube%3Amodern
    url = "https://api.scryfall.com/cards/search"  # type: str
    return get_card_list_scry(url,
                              get_card_names,
                              # lambda x: x,
                              {"q": "cube:modern", "order": "color"})


def get_card_list_scry(url: str, f, parameters: Dict[str, str] = {}, found: List[object] = []) -> List[object]:
    """
    Recursive rest call to srcyfall API, paging through multiple result pages.
    :param url:
    :param f:
    :param parameters:
    :param found:
    :return:
    """
    req = requests.get(url, params=parameters)
    print("Query scryfall API via {}. Status {}.".format(req.url, req.status_code))
    response = req.json()
    has_more = response.get("has_more")
    # print("total_cards : {}\nhas_more : {}".format(cards.get("total_cards"), has_more))
    data = response.get("data")
    result = found + f(data)
    if has_more:
        return get_card_list_scry(response.get("next_page"), f, found=result)
    else:
        return found


def get_card_names(cards):
    """
    :param cards: List of card JSONs.
    :return:
    """
    names = []
    for card in cards:
        name = card.get("name")
        names.append(name)
    return names


def read_cards_file(file):
    contents = open(file).read()  # type: str
    # contents.split(sep='\n')
    return contents


def get_cards_from_json(file="resources/modern-cube.json"):
    cards_str = read_cards_file(file)
    return json.loads(cards_str)


def card_img_uri(card, img_type="art_crop"):
    if card.__contains__("image_uris"):
        return [card.get("image_uris").get(img_type)]
    else:
        return flatten(list(map(card_img_uri, card.get("card_faces"))))


def flatten(xs):
    return [item for sublist in xs for item in sublist]


def get_card_image_uris(cards):
    return list(map(lambda x: (x.get("name"), card_img_uri(x)), cards))


def get_card_img_uris(url):
    req = requests.get(url, stream=True)
    if req.status_code == 200:
        with open("the_image.jpg", "wb") as f:
            req.raw.decode_content = True
            shutil.copyfileobj(req.raw, f)
