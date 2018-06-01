from typing import List, Dict

import requests
import shutil


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


def get_modern_cube_cards() -> List[object]:
    """
    Get all the cards in the Modern Cube via the scryfall API
    """
    # https://api.scryfall.com/cards/search?q=cube%3Amodern
    url = "https://api.scryfall.com/cards/search"  # type: str
    return get_card_list(url,
                         get_card_names,
                         # lambda x: x,
                         {"q": "cube:modern", "order": "color"})


def get_card_list(url: str, f, parameter: Dict[str, str] = {}, found: List[object] = []) -> List[object]:
    """
    Recursive rest call to srcyfall API, paging through multiple result pages.
    :param url:
    :param f:
    :param parameter:
    :param found:
    :return:
    """
    req = requests.get(url, params=parameter)
    print("Query scryfall API via {}. Status {}.".format(req.url, req.status_code))
    response = req.json()
    has_more = response.get("has_more")
    # print("total_cards : {}\nhas_more : {}".format(cards.get("total_cards"), has_more))
    data = response.get("data")
    result = found + f(data)
    if has_more:
        return get_card_list(response.get("next_page"), f, found=result)
    else:
        return found


def get_card_names(cards):
    names = []
    for card in cards:
        name = card.get("name")
        names.append(name)
    return names


def read_cards_file(file):
    return open(file).read()  # type: str
