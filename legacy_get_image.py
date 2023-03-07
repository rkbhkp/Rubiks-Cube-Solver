from typing import runtime_checkable

from sklearn.cluster import KMeans
from itertools import groupby

import cv2
import numpy as np
import math
from PIL import Image
import itertools
from imutils import contours
from colorthief import ColorThief as ct
from webcolors import rgb_to_name
import glob
#used to sort the contours


# HSV color code lower and upper bounds
COLOR_MIN = np.array([20, 100, 100],np.uint8)
# color yellow 
COLOR_MAX = np.array([30, 255, 255],np.uint8)

def callback(num):
    return
'''cv2.namedWindow('Settings', 0)

cv2.createTrackbar('Blob Area', 'Settings', 260, 1000, callback)
cv2.createTrackbar('Epsilon Percent', 'Settings', 6, 100, callback)
'''

colors = {
    'gray': (np.array([76, 0, 41], np.uint8), np.array([179, 255, 70], np.uint8)),        # Gray
    'blue': (np.array([69, 120, 100], np.uint8), np.array([179, 255, 255], np.uint8)),    # Blue
    'yellow': (np.array([20, 100, 125], np.uint8), np.array([30, 255, 255], np.uint8)),   # Yellow
    'red': (np.array([0, 110, 125], np.uint8), np.array([17, 255, 255], np.uint8)),     # Orange
    'green': (np.array([40, 40, 40], np.uint8), np.array([80, 255, 255], np.uint8)),        # green
    'black': (np.array([0, 0, 0], np.uint8), np.array([360, 255, 50], np.uint8)),       # black
    'white':  (np.array([0, 0, 200], np.uint8), np.array([255, 200, 255], np.uint8)),        # white
    'orange': (np.array([5, 50, 50], np.uint8), np.array([15, 255, 255], np.uint8))        # orange
    }

def getCube(image):
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    kernel = np.ones([2,2],dtype=np.uint8)
    cv2.imshow('orig', image)

    red = cv2.inRange(hsvImage, colors['red'][0],colors['red'][1])
    blue = cv2.inRange(hsvImage, colors['blue'][0],colors['blue'][1])
    yellow = cv2.inRange(hsvImage, colors['yellow'][0],colors['yellow'][1])
    green = cv2.inRange(hsvImage, colors['green'][0],colors['green'][1])
    orange = cv2.inRange(hsvImage, colors['orange'][0],colors['orange'][1])
    white = cv2.inRange(hsvImage, colors['white'][0],colors['white'][1])


    bwImage = red | blue | yellow | green | white
    contours_red = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue = cv2.findContours(blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_yellow = cv2.findContours(yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green = cv2.findContours(green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_white = cv2.findContours(white, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # needs work gets yellow
    contours_orange = cv2.findContours(orange, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # grabs red
    contours_new = cv2.findContours(bwImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(image)
    idx = contours_new[0]
    cv2.drawContours(mask, idx,-1,  (0,255,0), 2)
    out = np.zeros_like(image)
    out[mask == 255] = image[mask == 255]
    cv2.imshow('out', out)
    #edges = cv2.Canny(bwImage,100 ,200)
    return out
def computeContour(image, sigma=.55):
    cv2.imshow("orig", image)
    #import the image
    #convert the image HSV (sorta inverse color)
    #hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #set the thickness of the white lines
    kernel = np.ones([2,2],dtype=np.uint8)
    kernel2 = np.ones([3,3],dtype=np.uint8)
    kernel3 = np.array([[-1,-1,-1], [-1,10,-1], [-1,-1,-1]])
    #makes the image black and white
    bwImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Get colors
    # red = cv2.inRange(hsvImage, colors['orange'][0],colors['orange'][1])
    # blue = cv2.inRange(hsvImage, colors['blue'][0],colors['blue'][1])
    # yellow = cv2.inRange(hsvImage, colors['yellow'][0],colors['yellow'][1])
    # green = cv2.inRange(hsvImage, colors['green'][0],colors['green'][1])
    # black = cv2.inRange(hsvImage, colors['black'][0],colors['black'][1])
    # white = cv2.inRange(hsvImage, colors['white'][0],colors['white'][1])
    # clr_list = [red, blue, yellow, green]

    #bwImage = red | blue | yellow | green
    
    cv2.imshow('B&W', bwImage)
    v = np.median(bwImage)
    lower = int(max(0, (1.0-sigma)* v))
    upper = int(min(255, (1.0 + sigma)*v))

    #bwImage = cv2.GaussianBlur(bwImage, (4,4), 40, 40)
    #bwImage = cv2.filter2D(bwImage, -1, kernel3)

    #5, 5 works for stickered cube
    blurred = cv2.GaussianBlur(bwImage, (7,7),0)
    bwImage = cv2.Canny(blurred, lower,upper)
    cv2.imshow('canny', bwImage)
    #bwImage = yellow
    #remove some of the edges to make the specific cubes more distinct
    #bwImage = cv2.erode(bwImage, kernel2, iterations = 1)
    #cv2.imshow('erode', bwImage)
    #removes any white spaces floating in the void
    #bwImage = cv2.morphologyEx(bwImage, cv2.MORPH_OPEN, kernel2)
    #cv2.imshow('remove outside', bwImage)
    #gets the outline of the white section of the detected color
    #bwImage = cv2.morphologyEx(bwImage, cv2.MORPH_GRADIENT, kernel2)
    #cv2.imshow('remove inside', bwImage)
    #outlines the white boxes that are found  #RETR_EXTERNAL
    contours_new = cv2.findContours(bwImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    


    #cv2.imshow('findcontours', bwImage)
    idx = contours_new[0] if len(contours_new) == 2 else contours_new[1]
    #sort the contours into an order
    sorted_ctrs = sorted(idx, key=lambda ctr: cv2.boundingRect(ctr)[0] + cv2.boundingRect(ctr)[1] * image.shape[1])
    # make a list of all contours that are larger than a specific amount
    filter_small = [x for x in sorted_ctrs if cv2.contourArea(x) > 2000]
    filter_small = sorted_ctrs

    (cnts, _) = contours.sort_contours(filter_small, method="top-to-bottom")
    cube_rows = []
    row = []
    for (i, c) in enumerate(cnts, 1):
        row.append(c)
        if i % 3 == 0:
            (cnts, _) = contours.sort_contours(row, method="left-to-right")
            cube_rows.append(cnts)
            row = []
    number = 0
    test_im = image.copy()
    test_im2 = image.copy()
    color_h_list = []
    for row in cube_rows:
        for c in row:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(test_im2, (x, y), (x + w, y + h), (36,255,12), 2)
            #print(x, y, w, h)

            #cv2.imshow(f'cropped{number}', test_im[y:y+h, x:x+w])
            im = Image.fromarray(test_im[y:y+h, x:x+w])
            im.save('cube_slice.jpg')
            cv2.putText(test_im2, "#{}".format(number + 1), (x,y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            color_thief = ct('cube_slice.jpg')
            r,g,b = color_thief.get_color(quality=1)
            h,s,v = cv2.cvtColor(np.uint8([[[b,g,r]]]),cv2.COLOR_BGR2HSV)[0][0]
            color_h_list.append(h)
            number += 1
    
    
    cv2.drawContours(test_im, filter_small, -1, (0,255,0),-1)
    #create mask of black
    mask = np.zeros_like(bwImage, dtype='uint8')
    cv2.drawContours(mask, filter_small, -1, (255), -1)
    # apply mask
    res = np.zeros_like(image, dtype = 'uint8')
    cv2.imshow('mask',mask)
    cv2.imshow('small',test_im)
    cv2.imshow('count', test_im2)
    #masked = cv2.bitwise_and(test_im, test_im, mask=mask)
    res[(mask > 0)] = image[(mask > 0)]
    #put the outlines onto the original image
    #drawContours(image_you_want_to_change, list_of_contours, -1 for all or specify which contours,(0,255,0) (not sure ?), 2 (line thinckness?) )
    new_img = cv2.drawContours(image, filter_small ,-1,  (0,255,0), 2)
    cv2.imshow('mask', res)
    
    '''
    cv2.imshow('0red', red)
    cv2.imshow('1blue', blue)
    cv2.imshow('2yellow', yellow)
    cv2.imshow('3green', green)
    cv2.imshow('4black', black)
    cv2.imshow('5white', white)
    '''

    return color_h_list

def make_groups(data, n_groups):
    data = sorted(data)
    kmeans = KMeans(n_clusters=n_groups, random_state=0).fit(np.reshape(data,(-1,1)))

    return [[i[0] for i in list(d)] for g,d in groupby(list(zip(data,kmeans.labels_)), key=lambda x: x[1])]


def slice_when(predicate, iterable):
    i, x, size = 0, 0, len(iterable)
    while i < size-1:
        if predicate(iterable[i], iterable[i+1]):
            yield iterable[x:i+1]
        x = i + 1
        i += 1
    yield iterable[x:size]

def findEdges(image):
    LOWERTHRESH = 15
    UPPERTHRESH = LOWERTHRESH * 3
    DILATEITERATIONS = 2
    kernel_d = 3
    h, w, c = image.shape
    kernel = np.ones((kernel_d,kernel_d),np.uint8)
    wimage = image.copy()
    # convert to grayscale
    wimage = cv2.cvtColor(wimage, cv2.COLOR_BGR2GRAY)
    # add gaussian blur
    wimage = cv2.GaussianBlur(wimage, (5,5), 50, 50)
    wimage= cv2.Canny(wimage, LOWERTHRESH, UPPERTHRESH)
    wimage = cv2.dilate(wimage, kernel, iterations = DILATEITERATIONS)
    cv2.imshow('before fill', wimage)
    #wimage = cv2.morphologyEx(wimage, cv2.MORPH_DILATE,DILATEITERATIONS )
    cv2.floodFill(wimage, None, (0,0), 255)
    cv2.floodFill(wimage, None, (w-1,0), 255)
    cv2.floodFill(wimage, None, (0,h-1), 255)
    cv2.floodFill(wimage, None, (w-1,h-1), 255)
    cube_mask = 255 - wimage
    cv2.imshow('before dilate', cube_mask)
    cube_mask = cv2.dilate(cube_mask, kernel, iterations = 10)
    cube_mask = cv2.erode(cube_mask, kernel, iterations = 10)
    image[cube_mask] = (0,0,255)
    cv2.imshow('cube mask', cube_mask)
    masked = cv2.bitwise_and(image,image, mask=cube_mask)
    
    return masked;

def hardcodedBox(image):
    cv2.line(image)


# this is the working version of the function
def houghline(image, IMAGE_COUNT):
    kernel = np.ones((2,2),np.uint8)
    #copy the image
    wimage = np.copy(image)
    gdst = cv2.GaussianBlur(wimage, (5,5), 10,10)
    cv2.imshow("blurred", gdst)
    #get the canny lines from the image
    dst = cv2.Canny(gdst, 50,200, None, 3)
    cv2.imshow('canny', dst)

    ### create mask and crop image
    cimage = image.copy()
    h, w, c = image.shape
    cube_mask = make_mask(dst.copy(), h, w)

    # cuts the cube out of the original image using the mask created above
    isolated_cube = cv2.bitwise_and(cimage,cimage, mask=cube_mask)
    cv2.imshow("filled", isolated_cube)
    cv2.imshow("colors", computeContour(isolated_cube))
    return
    #get the canny lines from the image
    idst = cv2.Canny(isolated_cube, 50,200, None, 3)
    # make canny thicker
    #dilated = cv2.arcLength(30, idst, True) 
    cv2.imshow("before_arclen", idst)
    dilated = cv2.dilate(idst, kernel, iterations = 5)
    #dilated = cv2.erode(dilated, kernel, iterations = 3)    
    cv2.imshow("after_arclen", dilated)


    #convert the canny file to 3 channel
    cdst = cv2.cvtColor(idst, cv2.COLOR_GRAY2BGR)
    cv2.imshow("graytocolo", cdst)
    #copy the colored layer
    cdstP = np.copy(cdst)
    # perform standard hour tranform
    lines = cv2.HoughLines(idst, 1, np.pi / 180, 200, None, 0,0)
    #draw each line onto the file
    if lines is not None:
        for i in range(0,len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0+1000*(-b)), int(y0 + 1000*(a)))
            pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))

            cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)

    # perfrom probaliistic line transform
    linesP = cv2.HoughLinesP(idst, 1, np.pi / 180, 50, None, 50, 28)
    #draw each line onto the cdstP file
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
    cv2.imshow(f"Source{IMAGE_COUNT}", image)
    cv2.imshow(f"standard Hour Line{IMAGE_COUNT}", cdst)
    cv2.imshow(f"probabilistic line transform{IMAGE_COUNT}", cdstP)
    return
# takes in the canny lines of an image as fdst, the height of the original image as h, and the width as w
# returns a mask of the image to be used with cv2.bitwise_and(cimage,cimage, mask=cube_mask), to crop an image
def make_mask(fdst, h, w):
    kernel_d = 3
    DILATEITERATIONS = 2
    kernel = np.ones((kernel_d,kernel_d),np.uint8)
    fdst = cv2.dilate(fdst, kernel, iterations = DILATEITERATIONS)
    cv2.floodFill(fdst, None, (0,0), 255)
    cv2.floodFill(fdst, None, (w-1,0), 255)
    cv2.floodFill(fdst, None, (0,h-1), 255)
    cv2.floodFill(fdst, None, (w-1,h-1), 255)
    cv2.floodFill(fdst, None, (int(w/2),h-1), 255)
    cv2.floodFill(fdst, None, (int(w/2),0), 255)
    cv2.floodFill(fdst, None, (0,int(h/2)), 255)
    cv2.floodFill(fdst, None, (w-1,int(h/2)), 255)
    cube_mask = 255 - fdst
    cube_mask = cv2.dilate(cube_mask, kernel, iterations = 10)
    cube_mask = cv2.erode(cube_mask, kernel, iterations = 10)
    return cube_mask
folder = 'photos/stickered_sample'
images = glob.glob("photos/stickered_sample/1.jpg")
print(images)
full_list = []
for image in images:
    img = Image.open(image)
    print(img)
    img1 = img.resize((500,500))
    img1.save(f"{folder}/cropped/1.jpg")
    face = cv2.imread(f"{folder}/cropped/1.jpg")
    h_values = computeContour(face)
    full_list.append(h_values)
sorted_groups = make_groups(full_list, 6)
print(sorted_groups)

#computeContour(face)

#houghline(image2, 2)
#findEdges(image)
#new_frame  = computeContour(image)
#new_bottom = getCube(image)

#cv2.imshow('new_frame', new_frame)
#cv2.imshow('new_bottom', new_bottom)
cv2.waitKey(0)













#color ranges

'''
# reference to these operations here:
# https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html

gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
erosion = cv2.erode(img,kernel,iterations = 1)
dilation = cv2.dilate(img,kernel,iterations = 1)
opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
'''




#print(contours_new)
'''
cv2.imshow('edges', edges)
cv2.imshow('bwImage', bwImage)
cv2.imshow('Original image',image)
cv2.imshow('HSV image', hsvImage)'''
