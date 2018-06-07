import cv2
import glob
import imagehash
import json
import numpy as np
from PIL import Image, ImageFilter


def call_hash_img():
    return hash_imgs(glob.glob("resources/some-pics/*.jpg"))


def hash_imgs(img_paths):
    hashes = list(map(lambda img: imagehash.average_hash(Image.open(img)), img_paths))
    names = map(get_img_name_from_path, img_paths)
    return dict(zip(hashes, names))


def get_img_name_from_path(img_path):
    img_name = img_path.split("/")[-1]
    return img_name.split(".")[0]


# TODO use 'imagehash.hex_to_hash' to convert the hexstr back to hashes (two dimensional binary arrays)
def img_hash_dict_to_json(img_hash_dict):
    # convert the key hashes to hex strings for JSON encoding
    d = {str(k): v for (k, v) in img_hash_dict.items()}
    return json.dumps(d, sort_keys=True, indent=4)


def some_test():
    names = glob.glob("resources/pics/*.jpg")
    print(names[1])

    # img = cv2.imread("/home/conrad/workspace/pycube/resources/pics/Abrade.jpg", cv2.IMREAD_GRAYSCALE)
    img1 = cv2.imread(names[1], cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(names[2], cv2.IMREAD_GRAYSCALE)
    img3 = cv2.imread(names[3], cv2.IMREAD_GRAYSCALE)
    p_rat = cv2.imread("resources/ref-pics/Pack Rat.png", cv2.IMREAD_GRAYSCALE)

    hash1 = imagehash.average_hash(Image.fromarray(img1))
    hash2 = imagehash.average_hash(Image.fromarray(img3))
    # hash1 = imagehash.average_hash(Image.open(names[1]))
    # hash2 = imagehash.average_hash(Image.open(names[2]))
    print("hash-1: {}, hash-2: {}, diff: {}".format(hash1, hash2, hash2 - hash1))

    img = Image.open(names[1])
    img.filter(ImageFilter.BLUR)
    # PIL image to cv image
    imcv = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)

    pack_rat = Image.open("resources/ref-pics/Pack Rat.jpg")
    pack_rat = pack_rat.resize((620, 460))
    # pack_rat = pack_rat.convert('RGB')
    # rat_hash = imagehash.average_hash(pack_rat)l
    rat_hash = imagehash.average_hash(
        # Image.fromarray(p_rat).resize((620, 460))
        pack_rat
    )
    print("hash-1: {}, rat-hash: {}, diff: {}".format(hash1, rat_hash, hash1 - rat_hash))
    # pack_rat = pack_rat.filter(ImageFilter.BLUR)
    pr = cv2.cvtColor(np.asarray(pack_rat), cv2.COLOR_RGB2GRAY)

    cv2.imshow("frame", p_rat)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



