import cv2
import numpy as np
from copy import deepcopy

def apply_filter(imgpath, sobelw, cannyw, lapw):
    img = cv2.imread(imgpath, 0).astype(np.uint8)

    dst1_sobel = cv2.Sobel(img, ddepth=-1,
                           dx=1, dy=1, ksize=5,
                           borderType=cv2.BORDER_DEFAULT)
    dst1_canny = cv2.Canny(img, threshold1=100, threshold2=255)
    dst1_lap = cv2.Laplacian(img, ksize=3, ddepth=-1, borderType=0)

    return dst1_sobel * sobelw + dst1_canny * cannyw + dst1_lap * lapw

def apply_gate(target, thresh):
    target[target<thresh] = 0
    return target

def apply_denoise(target, strength, thresh):

    res = cv2.fastNlMeansDenoising(target, None, strength, 5, 21)
    res_copied = deepcopy(res)
    non_zero_indices = np.argwhere(res_copied != 0)
    for i, j in non_zero_indices:
        if (res_copied[i-1:i+2, j-1:j+2] == 0).all():
            res[i,j] = 0

    ker_sharpen = np.array([
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]])

    return res

def convert_gray_to_rgb_matrix(target):
    width, height = target.shape
    ctarget = np.zeros((width, height, 3), dtype=np.uint8)
    ctarget[:, :, 0] = target
    ctarget[:, :, 1] = target
    ctarget[:, :, 2] = target
    return ctarget

def set_stroke(target, hexcode):
    r, g, b = tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
    print(r,g,b)
    width, height, channel = target.shape
    ctarget = np.zeros((width, height, 3), dtype=np.uint8)
    ctarget[:, :, 0] = (target[:, :, 0] * b)
    ctarget[:, :, 1] = (target[:, :, 1] * g)
    ctarget[:, :, 2] = (target[:, :, 2] * r)
    return ctarget