import cv2


img = cv2.imread("/home/conrad/workspace/pycube/resources/pics/Abrade.jpg", cv2.IMREAD_GRAYSCALE)
cv2.imshow("frame", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
