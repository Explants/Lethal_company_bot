""" Identifies centroid of player and view """

import numpy as np
import cv2
import diplib as dip
from scipy.ndimage import rotate
import pyautogui
import time
import math
import keyboard


def make_mask(image, low, high, low1=None, high1=None, red=False):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    if red is True:
        mask1 = cv2.inRange(hsv, low1, high1)
        mask = cv2.bitwise_or(mask, mask1)
    result = cv2.bitwise_and(image, image, mask=mask)
    return result


def get_relative_angle(player, view, enemy):
    x_ab = view[0] - player[0]
    y_ab = view[1] - player[1]
    x_bc = enemy[0] - player[0]
    y_bc = enemy[1] - player[1]

    viewing_angle = (90 - np.degrees(np.arctan2(y_ab, x_ab))) % 360
    bc_angle = (90 - np.degrees(np.arctan2(y_bc, x_bc))) % 360

    rotation = bc_angle - viewing_angle
    if rotation > 180:
        rotation -= 360
    elif rotation < -180:
        rotation += 360
   
    return viewing_angle, rotation

def get_entities(mask, red=False, items=False, player=False):
    enemies, view_centroid, player_centroid, triangles = [], [], [], []
    shapes = []
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    mask = cv2.GaussianBlur(mask, (9, 9), 2)

    thresh_type = cv2.THRESH_BINARY + cv2.THRESH_OTSU
    _, binary = cv2.threshold(mask, 0, 255, thresh_type)

    kernel = np.ones((3,3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

    n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary,connectivity=4)

    for label in range(0, n_labels):
        shape = (labels==label).astype(np.uint8)* 255
        shapes.append(shape)

    for idx, shape in enumerate(shapes):
        labels = dip.Label(shape[:,:] > 0)
        msr = dip.MeasurementTool.Measure(labels, features=["Perimeter", "Size", "Roundness", "Circularity"])

        roundness = msr[1]['Roundness'][0]
        area = msr[1]['Size'][0]
        perimeter = msr[1]['Perimeter'][0]
        if roundness == 1.0:
            continue
        if items is True:
            contours, _ = cv2.findContours(shape, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                epsilon = 0.04 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                area = float(area)
                if area > 4000:
                    centroid = centroids[idx]
                    triangles.append(centroids[idx])
        elif player is True:
            if roundness < .80:
                view_centroid = centroids[idx]
            elif roundness < 1.00 and roundness > .80:
                player_centroid = centroids[idx]
        if red is True:
            x, y = int(centroids[idx][0]), int(centroids[idx][1])
            if roundness > .80 and roundness < .97 and area > 850:
                enemies.append(centroids[idx])

    return view_centroid, player_centroid, enemies, triangles

def get_clock(shapes, player_centroid, view_centroid):
    times = []
    for shape in shapes:
        _, rotation = get_relative_angle(player_centroid, view_centroid, shape)
        rotation = rotation % 360
        times.append(int(rotation) // 30)

    return times

def get_distance(player, entities):
    distances = []
    for entity in entities:
        player = player.astype(np.uint64)
        entity = entity.astype(np.uint64)

        player_x, player_y = int(player[0]), int(player[1])
        entity_x, entity_y= int(entity[0]), int(entity[1])

        height = player_y - entity_y
        length = player_x - entity_x

        hypotenuse = (height ** 2) + (length ** 2)
        hypotenuse = math.sqrt(hypotenuse)
        distances.append(hypotenuse)

    distance_labels = {'Close' : lambda d : d < 110, 'Medium' : lambda d: 110 < d < 220, 'Far' : lambda d: d > 220}

    words = []
    for distance in distances:
        for label, condition in distance_labels.items():
            if condition(distance):
                words.append(label)
                break
    return words

def alert_player(enemies, items, enemy_distance, object_distance):

    number = 0
    for idx, _ in enumerate(items[:]):
        number += 1 
        items.insert(idx + number % len(items), object_distance[idx])
    number = 0
    for idx, _ in enumerate(enemies[:]):
        number += 1 
        enemies.insert(idx + number % len(enemies), enemy_distance[idx])

    time.sleep(0.5)
    keyboard.press_and_release('esc')
    time.sleep(0.5)
    keyboard.press_and_release('/')
    time.sleep(0.5)
    keyboard.write(f'Enemies at {enemies}')
    time.sleep(0.5)
    keyboard.press_and_release('enter')
    time.sleep(0.5)
    keyboard.press_and_release('/')
    time.sleep(0.5)
    keyboard.write(f'Items at {items}')
    time.sleep(0.5)
    keyboard.press_and_release('enter')
    time.sleep(0.5)
    keyboard.press_and_release('e')


# image = pyautogui.screenshot()
# screenshot = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
screenshot = cv2.imread('images/enemies_lt.jpg')

player_mask = make_mask(screenshot, np.array([100, 140, 140]), np.array([170, 255, 255]))
enemy_mask = make_mask(screenshot, np.array([0, 150, 50]), np.array([9, 255, 255]), np.array([170, 150, 50]), np.array([180, 255, 255]), red=True)
object_mask = make_mask(screenshot, np.array([36, 230, 230]), np.array([70, 255, 255]))
view_centroid, player_centroid , _, _= get_entities(player_mask, player=True)

_,_, enemies,_ = get_entities(enemy_mask, red=True)
print(enemies)

_,_,_, objects = get_entities(object_mask, items=True)

screenshot[int(view_centroid[1]), int(view_centroid[0])] = [255,255,255]
screenshot[int(player_centroid[1]), int(player_centroid[0])] = [255,255,255]
enemy_times = get_clock(enemies, player_centroid, view_centroid)
print(enemy_times)
object_times = get_clock(objects, player_centroid, view_centroid)

enemy_distances = get_distance(player_centroid, enemies)
print(enemy_distances)