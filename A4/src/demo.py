'''
Author: Apoorv Agnihotri

Code samples from:
https://kushalvyas.github.io/stitching.html
'''
import cv2 as cv
import numpy as np
import sys
from src import *
import matplotlib.pyplot as plt
##########################################################
#Reading files
##########################################################
paths = ['I1']
for pathI in paths:
    path = '../data/normal/' + pathI + '/'
    imagesNames = ['a.jpg', 'b.jpg']#, 'c.jpg', 'd.jpg']#, 'e.jpg', 'f.jpg']
    scale = (0.05, 0.05)
    images = {} # will have 3 channel color imgs
    imageNos = len(imagesNames)
    imgB = 1
    width_epipolar = 10 # 20 combined width (pixels)

    ##########################################################
    #Rescaling
    ##########################################################
    images = {}
    for i in range(len(imagesNames)):
        img = imagesNames[i]
        print(path + img)
        temp = cv.imread(path + img)
        temp = cv.resize(temp, None, fx=scale[0], fy=scale[1], interpolation=cv.INTER_CUBIC)
        # plt.imshow(temp)
        # plt.show()
        images[i]=temp
    del temp

    ##########################################################
    #Finding KeyPoints and Discriptors
    ##########################################################
    print('finding keypoints and discriptors')
    imageKeyPoints, imageDescriptors = keyPoints(images)
    print('done keypoints and discriptors')
    # retured dictionaries with keys as imageNames

    ##########################################################
    #Finding matchings
    ##########################################################
    print('finding keymatches')
    lowsR = 0.85 # low's ratio
    goodMatchings={}
    for i in range(imageNos-1):
        imgA = i
        goodMatchings[(imgA,imgB)]= keyPointMatching(images, 
                                  imageKeyPoints, imageDescriptors, 
                                  imgA, imgB, lowsR)
    print('done keymatches')

    ##########################################################
    # Finding F the pair of image
    ##########################################################
    n = 1000 # iterations
    r = 8 # no of point to calc fundamental matrix
    t = 2 # pixel threashold
    Tratio = 0.95 # majority threashold
    print('finding Fundamentals')
    for i in range(imageNos -1):
        imgA = i
        list_kp = goodMatchings[(imgA, imgB)]
        # finding the fundamental matrices, using ransac
        F, S = cv.findFundamentalMat(np.array(list_kp[0]), np.array(list_kp[1]))
    print('done Fundamentals')
    print('Fundamental Matrix:', F)

    ##########################################################
    # Mannually selecting the interest points on I1, I2, I3
    ##########################################################
    # Points = {} #I4
    # Points[0] = np.array([[340, 294]])
    # Points[1] = np.array([[411, 300]])
    # Points[2] = np.array([[403, 284]])
    # Points[3] = np.array([[633, 262]]) # for testing
    # Points = {} #I1
    # Points[0] = np.array([[208, 243]])
    # Points[1] = np.array([[245, 272]])
    # print('imageKeyPoint:', imageKeyPoints[0][0].pt) 
    # # one of the key point for img0
    # print('imageDescriptor:', imageDescriptors[0][0]) 
    # # one of the key descriptor for img0
    # print(Points[0])
    # Points[2] = np.array([[434, 223]])
    # Points[3] = np.array([[500, 119]]) # for testing


    ##########################################################
    # Change to LAB if wanted
    ##########################################################


    ##########################################################
    # For each point in I1, find epiline
    ##########################################################
    print('Finding the epilines for each point')
    I1 = images[0]
    I2 = images[1]
    h, w, chl = I1.shape
    # make a list of all the points
    listOfPoints = []
    for y in range(h):
        for x in range(w):
            pt = (x, y)
            listOfPoints.append(pt)

    # compute epilines for each pt
    epilines = findEpilines(np.array(listOfPoints), F)
    print('done')
    # print('epilines', epilines)
    # print(epilines.shape)

    ##########################################################
    # For each point in I1, find the corresp I2 point
    ##########################################################
    print('Find the point corresp to every point in I1, please wait..')
    channel = 'RGB'
    width = 2
    h, w, chl = I2.shape
    Iout = np.zeros((h, w, chl))
    for i in range(len(epilines)):
        epiline = epilines[i]
        vPts = findValidPoints(epiline, (h, w), width)
        if len(vPts) == 0: # no valid point
            continue

        # returns discriptors in rows
        discriptors = findCustomDiscriptor(I2, vPts, channel=channel)
        if discriptors == None:
        	continue
        	# print('none aya')
        if discriptors != None:
            # print('discriptors',discriptors)
            ptI1 = listOfPoints[i]
            I1ptDiscriptor = findCustomDiscriptor(I1, [ptI1], channel=channel) # can return empty array
            if I1ptDiscriptor != None:
                # print('I1ptDiscriptor',I1ptDiscriptor)
                keys = list(discriptors.keys())
                dis = np.array([discriptors[key] for key in keys])
                # print('dis', dis, 'dis.shape', dis.shape) 
                # print(I1ptDiscriptor[ptI1])
                temp = dis - I1ptDiscriptor[ptI1].astype(float)
                # print(temp) # underflow happening
                temp = np.linalg.norm(temp, axis=1)
                min_index = np.argmin(temp)
                argminKey = keys[min_index]
                y_ = argminKey[1]
                x_ = argminKey[0]
                y = ptI1[1]
                x = ptI1[0]
                Iout[y_,x_] = I1[y,x]
    
    np.save('t', Iout)
    Iout = Iout.astype(np.uint8)
    cv.imshow('out', Iout)
    cv.waitKey(0)
    sys.exit()


    ##########################################################
    # find the equations of the parrellel lines
    ##########################################################
    # line parallel to lines[0] would be in newlines[0]
    newlines = {} # list of lines
    # print (lines)
    for i in range(-1,2):
        inx = -1*((2*i)+1)
        if inx == -3:
            inx = 0
        xy = intersection[i] # getting the correct intersection point
        # print(xy)
        c =  -(lines[inx][0][1]*xy[1,0] + lines[inx][0][0]*xy[0,0])
        newlines[inx] = [lines[inx][0][0]]
        newlines[inx].append(lines[inx][0][1])
        newlines[inx].append(c)
    # print ('newlines:', newlines)
    # printing the newlines on the image
    temp = drawlinesP(temp, newlines)
    plt.imshow(temp)
    plt.show()
    sys.exit()

    # make the lookup table

    # given temporal order return valid regions

    # color valid regions

    # exit