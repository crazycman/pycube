from time import sleep
from typing import List, Dict, Tuple

import requests
import shutil
import json
import functools


def save_json_card_list(file, card_list="resources/some-cards.txt"):
    """
    Query the srcyfall API for a list of cards and
    save the returned list of (formatted) JSON card descriptions in a file.
    :param file: Path of the JSON file to save the cards
    :param card_list: List of card names
    :return: Nothing
    """
    write_to_file(file, get_json_card_list_formatted(card_list))


def get_json_card_list_formatted(card_list="resources/some-cards.txt"):
    card_list = get_json_card_list(card_list)
    return json.dumps(card_list, indent=2)


def get_json_card_list(card_list="resources/modern-cube.txt"):
    """
    Given a list of card names (with set specification, e.g. Cryptic Command : LRW),
    query the scryfall API for the JSON representation of the cards and return them in a list.
    :param card_list: Path to a list of card names
    :return: List of cards (cards are JSONs)
    """
    card_names = read_cards_file(card_list).split(sep='\n')
    return get_cards_scry(card_names)


def get_card_scry(parameters, wait=True, verbose=False):
    """
    Query the scryfall API for a specific card.
    :param wait: Set to True, to insert a wait before a request; see https://api.scryfall.com/docs/api
    :param parameters: Dict of request parameters
    :return: Card as JSON (as returned by the scryfall API)
    """
    if wait:
        sleep(0.1)
    req = requests.get("https://api.scryfall.com/cards/named", params=parameters)
    if verbose:
        print("Query {}, Status {}.".format(req.url, req.status_code))
    if req.status_code == 200:
        response = req.json()
        print("Receive response for: {}, Eur: {}".format(response.get("name"), response.get("eur")))
        return response
    else:
        raise ValueError(req.text)


def get_cards_scry(card_names: List[str]) -> list:
    """
    :param card_names: as list of strings.
    :return: List of cards as JSON, can be saved
    """
    return list(map(get_card_scry, map(create_q_param, card_names)))


def create_q_param(card_name: str) -> Dict[str, object]:
    card_info = map(lambda x: x.strip(), card_name.split(":"))
    return dict(zip(["fuzzy", "set"], card_info))


# -----------------------------------------------------------------------------
# Get cards (as JSON list) in the modern cube based on the scryfall curated list

def get_modern_cube_cards_scry() -> List[object]:
    """
    Get all the cards in the Modern Cube via the scryfall API
    :return List of cards as JSON
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
    :param url: URL to send the rest request to
    :param f: Function to apply to the request result (e.g. convert list of JSON to list of string)
    :param parameters: Query parameters
    :param found: List of already processed (i.e. found) results
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
    :param cards: List of card JSONs
    :return: List of card names (str)
    """
    names = []
    for card in cards:
        name = card.get("name")
        names.append(name)
    return names


# -----------------------------------------------------------------------------
# Download card images


def download_card_imgs(save_path="resources/pics/", wait=True):
    """
    Call this procedure to download all the images of cards that have image URIS in the JSON file.
    :param save_path: Path to store the pictures
    :param wait: Set this to true, to insert a 1/10 sec wait between queries (to respect scryfall etiquette).
    :return: Nothing, as a side effect all the card images are stored.
    """
    # TODO replace decode_json_file() with parameter (list_of_cards)
    cards_and_uris = get_card_image_uris(decode_json_file())
    for (name, url) in cards_and_uris:
        if wait:
            sleep(0.1)
        download_card_img(name, url, save_path)


def card_img_uri(card, img_type="art_crop") -> List[Tuple[str, str]]:
    """
    Given a card (as JSON) return a list of tuples with the card names and image URIs.
    List are returned because of of flip and split cards.
    :param card: Card as JSON
    :param img_type: String in ["large", "normal", "png", "border_crop", "art_crop", "small"]
    :return: List of tuples (card_name, image_uri)
    """
    if card.__contains__("image_uris"):
        return [(card.get("name"), card.get("image_uris").get(img_type))]
    else:
        return concat(list(map(card_img_uri, card.get("card_faces"))))


def get_card_image_uris(cards) -> List[Tuple[str, str]]:
    return concat(list(map(card_img_uri, cards)))


def download_card_img(name, url, save_path="resources/pics/"):
    print("Downloading: {}".format(name))
    req = requests.get(url, stream=True)
    if req.status_code == 200:
        # TODO image name should be: card_name_set.jpg?
        with open("{}{}.jpg".format(save_path, name.replace('//', '-')), "wb") as f:
            req.raw.decode_content = True
            shutil.copyfileobj(req.raw, f)


# -----------------------------------------------------------------------------
# General helper functions
# TODO move them to a general module

def decode_json_file(file="resources/modern-cube.json"):
    """
    Given a path to a JSON file, load the file and decode it.
    :param file: Path to JSON file that contains cards
    :return: List of JSONs (which represent cards)
    """
    cards_str = read_cards_file(file)
    return json.loads(cards_str)


def concat(xs):
    # return [item for sublist in xs for item in sublist]
    return functools.reduce(lambda x, y: x + y, xs, [])


def read_cards_file(file):
    """
    The syntax supported in the card list is:
    Card Name : Set (abbreviation), e.g.
    Cryptic Command : LRW
    see function 'create_q_param' above.
    :param file:
    :return: File contents as string
    """
    contents = open(file).read()  # type: str
    # contents.split(sep='\n')
    return contents.strip()


def write_to_file(file, content):
    with open(file, 'w') as the_file:
        the_file.write(content)
