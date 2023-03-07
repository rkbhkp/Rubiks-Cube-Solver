from itertools import groupby
import cv2
import numpy as np
import math
from PIL import Image
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000
import os

side_number = 0#global argument for debugging

#returns a list of 9 LAB (3-tuple) colors for each color in the cube
def get_squares(clean_image):
    sq_list = []
    for row in range(3):
        for col in range(3):
            sample_size = 42
            sq_width = 42
            assert(sample_size <= sq_width)
            sample_seperation = 73
            x_start = 46+col*sample_seperation + ((sq_width-sample_size)//2)
            y_start = 26+row*sample_seperation + ((sq_width-sample_size)//2)

            square = clean_image[y_start:y_start+sample_size, x_start:x_start+sample_size]
            cv2.imwrite(f'photos/squares/{side_number}_{row}_{col}.jpg', square)

            r,g,b = get_dom_color(Image.open(f'photos/squares/{side_number}_{row}_{col}.jpg'))

            d = 1
            detectedColor = np.array([[(b,g,r)for i in range(d)] for i in range(d)])
            cv2.imwrite(f'photos/squares/{side_number}_{row}_{col}_det_color.jpg', detectedColor)

            lab_img = cv2.imread(f'photos/squares/{side_number}_{row}_{col}_det_color.jpg')
            sticker_LAB = cv2.cvtColor(lab_img, cv2.COLOR_BGR2LAB)[0][0]

            #x = (x[0]*100/255, x[1]-128, x[2]-128)

            sq_list.append((sticker_LAB[0]*100/255, sticker_LAB[1]-128, sticker_LAB[2]-128))
    return sq_list

# gets the most dominant color from an image, palette_size is how sensitive it is lower is more sensitive
def get_dom_color(pil_img, palette_size=1):
    img = pil_img.copy()
    img = img.quantize(colors=4, kmeans=4).convert('RGB')
    color_counts = sorted(img.getcolors(4), reverse=True)
    return color_counts[0][1]

#computes the distance to the centers given a square with a certain LAB value. returns an array
# 6 long, representing the distance to all of the different colors
def distance(centers, square):
    distances = []
    for center in centers:
        distance = delta_e_cie2000(LabColor(square[0], square[1], square[2]), LabColor(center[0], center[1], center[2]))
        distances.append(distance)
    return distances

#given a list [6][9][6] of sides, squares, and distances to colors, normalizes the distances based upon the
# largest distance that is observed for a particular color. So, centers get a distance of 0 to one color,
# and it goes up to one from there.
def normalize_distances(distances):
    MAX_DIST = [0 for _ in range(6)]
    for color_index in range(6):
        for side_num in range(6):
            for square_num in range(9):
                if distances[side_num][square_num][color_index] > MAX_DIST[color_index]:
                    MAX_DIST[color_index] = distances[side_num][square_num][color_index]
    for side_num in range(6):
        for square_num in range(9):
            for color_index in range(6):
                distances[side_num][square_num][color_index] /= MAX_DIST[color_index]

#modifies the passed diistance array so that it is instead a likelyhood array
# for each square, initially, there are six values between 0 and 1 representing the distance of the square to
# each color. This calculates the likelyhood of each square being a certain color (and not another) and puts it
# between 0 and 1.
def get_likelyhood(distances):
    for side in range(6):
        for square in range(9):
            new_square = [1 - x for x in distances[side][square]]
            
            total = sum(new_square)
            #print(new_square)
            for color in range(6):
                new_square[color] = (new_square[color])/total
            distances[side][square] = new_square

#calculates which bucket each square is in based upon the passed likelyhood list for each color.]
# returns a [6][9] list containing (0-6] values representing the various colors
# ensures that only 4 edges of each color occur, as well as 4 corners.
def calculate_bucket(likely):
    num_edges = [4 for i in range(6)]
    num_corners = [4 for i in range(6)]
    CIND = [0,2,6,8]#corner indeces
    EIND = [1,3,5,7]#edge indeces

    all_sides = [[-1 for x in range(9)] for y in range(6)]

    #first sort the centers
    for side in range(6):
        all_sides[side][4] = likely[side][4].index(max(likely[side][4]))

    #calculate the discrepency for each square (how much the top probablility is greater than the 2nd top)
    discrepencies = []# a list of tuples, (side #, square #, discrepency)
    for side in range(6):
        for square in range(9):
            m1 = 0
            m2 = 0
            for c in range(6):
                if likely[side][square][c] > m1:
                    m2 = m1
                    m1 = likely[side][square][c]
                elif likely[side][square][c] > m2:
                    m2 =likely[side][square][c]
            disc = m1 - m2
            discrepencies.append((side, square, disc))
    #sort the corners and edges in order of discrepencies
    discrepencies.sort(key=lambda x: x[2], reverse=True)
    #print(discrepencies)
    for sticker_index in range(54):
        sticker = discrepencies[sticker_index]
        if sticker[1] != 4: #it is not a center
            #pick the biggest value out as the color
            available_colors = []
            if sticker[1] in EIND:
                for i in range(6):
                    if num_edges[i] > 0:
                        available_colors.append(i)
            else:
                for i in range(6):
                    if num_corners[i] > 0:
                        available_colors.append(i)
            color_index = 0
            for i in range(len(available_colors)):
                if likely[sticker[0]][sticker[1]][available_colors[i]] > likely[sticker[0]][sticker[1]][available_colors[color_index]]:
                    color_index = i
            color = available_colors[color_index]
            #rempove one from that color
            if sticker[1] in EIND:
                num_edges[color] -= 1
            else:
                num_corners[color] -= 1
            
            all_sides[sticker[0]][sticker[1]] = color
    return all_sides

#classifies the given cube based on the data in the six image files within the passed folder
# returns a list of six sides, each nine big, representing the different colors. Values are ints in the range [0-6)
def get_cube_classification_list(folder: str) -> list:
    if not os.path.exists(folder):
            raise Exception('Input directory for images does not exist.')
    if not os.path.exists(folder + '/cropped'):
            os.makedirs(folder + '/cropped')

    global side_number
    side_number = 0

    test =  "1.jpg"
    images = [f'{folder}/{i}.jpg' for i in range(6)]
    full_list = []
    colors = ['1','2','3','4','5','6']
    s_count = 0

    for image in images:
        #open each image
        img = Image.open(image)
        #resize to a smaller size so the image is not so large
        img1 = img.resize((500,500))
        #rotate to account for camera being 5 degrees crooked
        img1 = img1.rotate(5)
        # save cropped image to be opened with cv2
        img1.save(f"{folder}/cropped/{test}")
        #open image with cv2
        face = cv2.imread(f"{folder}/cropped/{test}")
        face = face[130:400, 120:400]
        #cv2.imshow('face', face)
        # main driver, takes in an image with a grid system and a clean image of the same size and finds the boxes on the image and find the 
        # most predominant color in the image and return it as a list of (l,a,b) for all 9 spots on the cube face
        sq_values = get_squares(face)
        # add face to cube list
        full_list.append(sq_values)
        side_number += 1
        s_count += 1
    
    #use the six centers as truth data
    centers = [side[4] for side in full_list]

    #get the distances of each square to each center
    distances = [[[] for i in range(9)] for i in range(6)]
    for side in range(6):
        for square in range(9):
            distances[side][square] = distance(centers, full_list[side][square])

    #normalize the distances for the cube
    normalize_distances(distances)

    #get the likelyhood each square is a certain color
    get_likelyhood(distances)

    '''
    for i, side in enumerate(distances):
        print(i)
        tab = ""
        for x, square in enumerate(side):
            print(tab, x, " ",square, sep="")
            tab = tab + "  "
    '''
    # can be used when testing to prevent the cv2.imshow from disapearing
    #cv2.waitKey(0)
    return calculate_bucket(distances) #calculate what color each square is and return it


if __name__ == "__main__":
    folder = 'photos/samples/0'
    finished_cube = get_cube_classification_list(folder)
    print("finishedcube",finished_cube)
    print("centers:", [side[4] for side in finished_cube])
    # can be used when testing to prevent the cv2.imshow from disapearing
    #cv2.waitKey(0)