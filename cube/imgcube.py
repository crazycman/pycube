import cv2
import glob
import imagehash
import numpy as np
from PIL import Image, ImageFilter


names = glob.glob("resources/pics/*.jpg")
print(names[1])

# img = cv2.imread("/home/conrad/workspace/pycube/resources/pics/Abrade.jpg", cv2.IMREAD_GRAYSCALE)
img1 = cv2.imread(names[1], cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread(names[2], cv2.IMREAD_GRAYSCALE)
img3 = cv2.imread(names[3], cv2.IMREAD_GRAYSCALE)

hash1 = imagehash.average_hash(Image.fromarray(img1))
hash2 = imagehash.average_hash(Image.fromarray(img3))
# hash1 = imagehash.average_hash(Image.open(names[1]))
# hash2 = imagehash.average_hash(Image.open(names[2]))
print("hash-1: {}, hash-2: {}, diff: {}".format(hash1, hash2, hash2 - hash1))

img = Image.open(names[4])
img.filter(ImageFilter.BLUR)
# PIL image to cv image
imcv = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)

cv2.imshow("frame", imcv)
cv2.waitKey(0)
cv2.destroyAllWindows()
