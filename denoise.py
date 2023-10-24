import cv2
import numpy as np
img = cv2.imread('96308619_p0_filtered.jpg')
res = cv2.fastNlMeansDenoising(img, None, 30, 5, 21)
cv2.imwrite('96308619_p0_filtered_denoised.jpg', res)