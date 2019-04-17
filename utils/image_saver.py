
import cv2
import os
import datetime
import csv

vehicle_count = [0]
current_path = os.getcwd()


def save_image(source_image):
    fname = 'vehicle' + str(len(vehicle_count)) + "_" + \
                str(datetime.datetime.now().strftime("%m%d%Y%H%M%S%f")) + \
                '.jpg'
    cv2.imwrite(current_path + '\\static\\images\\' + fname, source_image)
    vehicle_count.insert(0, 1)
    #AddToCSV
    fields = [fname]
    with open('fname.csv', mode='w') as img_fileName:
        csv_writer = csv.writer(img_fileName, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(fields)
    return fname

def crop_center(img,cropx,cropy): # to crop and get the center of the given image
    y,x, channels = img.shape
    startx = x//2-(cropx//2)
    starty = y//2-(cropy//2)

    return img[starty:starty+cropy,startx:startx+cropx]


