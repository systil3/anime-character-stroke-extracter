import cv2
import numpy as np

def apply_filter(imgpath, sobelw, cannyw, lapw):
    img = cv2.imread(imgpath, 0).astype(np.uint8)


    dst1_sobel = cv2.Sobel(img, ddepth=-1,
                           dx=1, dy=1,
                           borderType=cv2.BORDER_DEFAULT)
    dst1_canny = cv2.Canny(img, threshold1=100, threshold2=255)
    dst1_lap = cv2.Laplacian(img, ksize=3, ddepth=-1, borderType=0)

    return dst1_sobel * sobelw + dst1_canny * cannyw + dst1_lap * lapw

def apply_gate(target, thresh):
    target[target<thresh] = 0
    return target

def apply_denoise(target, strength, thresh):
    print("---")
    res = cv2.fastNlMeansDenoising(target, None, strength, strength, 5, 21)
    ker_sharpen = np.array([
        [1, -2, 1],
        [-2, 4, -2],
        [1, -2, 1]])
    #res = cv2.filter2D(target, -1, ker_sharpen)
    res[res<thresh] = 0
    return res