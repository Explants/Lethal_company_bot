import PIL.ImageGrab
import pyautogui
import numpy as np
from numpy import asarray
import cv2
from PIL import ImageGrab, Image
import time
import math
import cv2
from matplotlib import pyplot as plt
from matplotlib.transforms import Affine2D
from scipy.ndimage import rotate


screenshot = Image.open(r'images/enemies_lt2.jpg')
image = np.array(screenshot)

def orient(image):

    def get_angle(player, view):

        # Get adjacent and opposite of triangle
        height = abs(player[0] - view[0])
        
        length = abs(player[1] - view[1])
            
        # Get hipotanus of triangle
            
        hipotanus = (height ** 2) + (length ** 2)
        hipotanus = math.sqrt(hipotanus)
        
        # Get angle from radians

        cos_divisor = (hipotanus ** 2 + length ** 2 - height ** 2) / (2 * hipotanus * length)

        angle = math.acos(cos_divisor)
        angle = angle * 180/math.pi
        
        return angle, height, length

    angle, height, length = get_angle(player_median, view_median)
    print(angle)

    view_median = np.array(view_median).astype(np.int64)
    player_median = np.array(player_median).astype(np.int64)

    image[view_median[1], view_median[0]] = [255, 0, 0]
    image[player_median[1], player_median[0]] = [0, 255, 0]

    if player_median[1] > view_median[1] and player_median[0] > view_median[0]:
        print(player_median[1], view_median[1], player_median[0], view_median[0])
        rotated_image = rotate(image, -angle, reshape=True)
        print('1')
    if player_median[1] > view_median[1] and player_median[0] < view_median[0]:
        rotated_image = rotate(image, angle, reshape=True)
        print('2')
    if player_median[1] < view_median[1] and player_median[0] > view_median[0]:
        rotated_image = rotate(image, angle, reshape=True)
        print('3')
    if player_median[1] < view_median[1] and player_median[0] < view_median[0]:
        rotated_image = rotate(image, -angle, reshape=True)
        print('4')


    # Display the rotated image
 
    return rotated_image

rotated = orient(image)