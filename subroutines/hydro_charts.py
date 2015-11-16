# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 13:31:10 2014

@author: lbesnard
"""
#hydroChartLink = 'http://www.hydro.com.au/system/files/water-storage/Web_Rivers_IrisRvLkGairdner.pdf'

def create_tmp_data_folder():
    global river_dataDir
    #import tempfile
    #river_dataDir = tempfile.mkdtemp()
    river_dataDir = '/tmp/riverData'

def download_hydroChart(hydroChartLink):
    # function to download the chart associated to a river
    import string, os, time,datetime,os.path
    import urllib2
    import shutil

    create_tmp_data_folder()
    if os.path.exists(river_dataDir):
        shutil.rmtree(river_dataDir)
        os.mkdir(river_dataDir)

    # download the chart to the tmp folder
    webFile                   = urllib2.urlopen(hydroChartLink)
    baseFile                  = os.path.basename(hydroChartLink)
    local_chart_file_location = os.path.join(river_dataDir,baseFile)
    localFile                 = open(local_chart_file_location, 'w')
    localFile.write(webFile.read())

    return local_chart_file_location

def convert_chart_pdf_to_jpg(local_chart_file_location):
    # this function requires imagemagick to convert the pdf to jpg
    import subprocess
    convertedFile = local_chart_file_location[0:-3]+'jpg'
    command       = 'convert %s %s' % (local_chart_file_location, convertedFile)
    success       = subprocess.call(command, shell=True)

    return success,convertedFile

def range_color_of_pixel_in_bounding_box(jpgFile,boundingBox,colorTimeseries):
    #boundingBox [pixelXmin,pixelXmax,pixelYmin,pixelYmax]
    #colorTimeseries string blue,red,green,black. nothing else
    # this function tries to see if there is the main color of the timeseries in
    # the bounding box of our choice in pixel. The bounding box is the last date
    # in axis X and the required Flow in axis Y.

    import Image
    im        = Image.open(jpgFile)
    pix       = im.load()
    imageSize = im.size #Get the width and hight of the image for iterating over

    nPixels=0
    for x in range(boundingBox[0],boundingBox[1]):
        for y in range(boundingBox[2],boundingBox[3]):

            pixelColor = pix[x,y] # RGB balue
            #print pixelColor
            if colorTimeseries == 'red':
                if (pixelColor[0] > 180) & (pixelColor[1] < 90 ) & (pixelColor[2] < 90):
                    nPixels=nPixels+1 #Get the RGBA Value of the a pixel of an image
            elif  colorTimeseries == 'green':
                if (pixelColor[0] < 90) & (pixelColor[1] > 180) & (pixelColor[2] < 90):
                    nPixels=nPixels+1 #Get the RGBA Value of the a pixel of an image
            elif  colorTimeseries == 'blue':
                if (pixelColor[0] < 90) & (pixelColor[1] < 90) & (pixelColor[2] > 180):
                    nPixels=nPixels+1 #Get the RGBA Value of the a pixel of an image
            elif  colorTimeseries == 'black':
                if (pixelColor[0] < 50) & (pixelColor[1] < 50) & (pixelColor[2] < 50):
                    nPixels=nPixels+1 #Get the RGBA Value of the a pixel of an image

    if nPixels > 5:
        riverStatus = 'very likely on'
        riverOn = True
    elif (nPixels > 0) & (nPixels <5):
        riverStatus = 'maybe on'
        riverOn = True
    elif (nPixels == 0):
        riverStatus = 'apparently not on'
        riverOn = False

    return riverOn,riverStatus


def message_hydroChart(riverName,station_name,currentRiverStatus,station_minValue,paddleTasmaniaLink_short,hydroChartLink_short):
    # create the string message which will be sent by email or twitter
    import datetime
    timetoday = datetime.datetime.now().strftime("%Y-%m-%d")

    msg       = riverName+' is ' + str(currentRiverStatus)  + ' at ' +station_name + '. Above '  + str(station_minValue) +' on '+timetoday+  '.See Chart: ' + hydroChartLink_short + ' Guide: ' +paddleTasmaniaLink_short
    if len(msg) > 140:
        logger.info('WARNING : Tweet size greater than 140')

    return msg

def convert_chart_pdf_to_txt(local_chart_file_location):
    import subprocess
    txt_chartFile = local_chart_file_location[0:-3]+'txt'
    command = 'pdf2txt.py -o %s %s' % ( txt_chartFile,local_chart_file_location)
    success = subprocess.call(command, shell=True)

    return txt_chartFile

def find_min_max_y_axis_flow(txt_chartFile):
    import glob
    lines           = tuple(open(txt_chartFile, 'r'))

    fin             = open(txt_chartFile)
    flow_line_index = 0
    for line in fin:
        if "Flow in ML/day" in line:
            break
        flow_line_index += 1
    fin.close()

    top_limit_y_axis_index = flow_line_index+2
    top_limit_y_axis       = int(lines[top_limit_y_axis_index])

    fin                    = open(txt_chartFile)
    zero_line_index        = 0
    for line in fin:
        if line == "0\n" :
            break
        zero_line_index += 1
    fin.close()

    nY_coordinates      = (zero_line_index- top_limit_y_axis_index)/2
    bottom_limit_y_axis = 0

    step                = top_limit_y_axis / nY_coordinates
    allY_coordinates    = range (bottom_limit_y_axis,top_limit_y_axis+step,step)

    return allY_coordinates

def define_y_pixel_range(allY_coordinates,pixel_Y_min,pixel_Y_max,minFlow):
    #ymin = bottom pixel
    #ymax = top pixel
    nPixelPerYCoordinate        = abs(pixel_Y_min - pixel_Y_max)*1.0 /(allY_coordinates[-1]-allY_coordinates[0] )*1.0
    lowYpixelWhereToLookForData = int(pixel_Y_min - (minFlow * nPixelPerYCoordinate))

    return lowYpixelWhereToLookForData

# more comments are needed
def find_min_max_y_axis_height_dam(txt_chartFile):
    import glob
    lines           = tuple(open(txt_chartFile, 'r'))

    fin             = open(txt_chartFile)
    flow_line_index = 0
    for line in fin:
        if "Metres from full - last 14 days" in line:
            break
        flow_line_index += 1
    fin.close()

    top_limit_y_axis_index = flow_line_index+2
    top_limit_y_axis       = float (lines[top_limit_y_axis_index])

    import datetime
    month_fortnight_ago    = datetime.date.fromordinal(datetime.date.today().toordinal()-14).strftime("%B")

    fin                    = open(txt_chartFile)
    zero_line_index        = 0
    for line in fin:
        if line[0:3] == month_fortnight_ago[0:3] :
            break
        zero_line_index += 1
    fin.close()

    nY_coordinates      = (zero_line_index  - top_limit_y_axis_index)/2
    bottom_limit_y_axis = float(lines[zero_line_index-2])
    step                = (top_limit_y_axis - bottom_limit_y_axis) / (nY_coordinates-1)
    allY_coordinates    = drange(bottom_limit_y_axis,top_limit_y_axis,step)
    allY_coordinates    = ["%f" % x for x in allY_coordinates]
    allY_coordinates    = map(float, allY_coordinates)

    return allY_coordinates

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step
