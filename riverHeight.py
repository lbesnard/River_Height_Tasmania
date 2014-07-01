#!/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Laurent Besnard
# email address: laurent.besnard@utas.edu.au
# Website: https://github.com/lbesnard/River_Height_Tasmania
# May 2013; Last revision: 6-Jun-2014
#
# The script is distributed under the terms of the GNU General Public License 


import string, re, os, time, smtplib, sys, urllib2, csv, os.path, logging, requests, datetime
from subroutines.send_notification import *

# BOM STATIONS CHECKER
from subroutines.bom import *    
def check_river_height_bom():
    try:  
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # create a file handler
        
        handler = logging.FileHandler('riverHeight.log')
        handler.setLevel(logging.INFO)
        
        # create a logging format
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # add the handlers to the logger
        
        logger.addHandler(handler)

        pathname = os.path.dirname(sys.argv[0])        
        pythonScriptPath=os.path.abspath(pathname)
        # paddleable river heigts are written in a file on dropbox
        logger.info('Open river height BOM file on dropbox')
        csvFile = urllib2.urlopen('https://www.dropbox.com/s/g81irf5nhad8y8r/riverHeight_bom.csv?dl=1')
    

        
        # read river status from previous run
        riverStatusFile = pythonScriptPath + '/riverStatus_bom.csv'
        if os.path.isfile(riverStatusFile):
            with open(riverStatusFile, 'rb') as f:
                riverStatusdata = list(csv.reader(f))
        else :
            riverStatusdata  = []
            
        #write current river status for next run
        writerRiverStatus = open(riverStatusFile, 'w+')

        for line in csvFile:
            #initialise values for each river
            
            chgRiverStatus = False
            riverRunnable_now = False
            linelst = line.split(',') 
            isLineComment=line.strip().startswith("#")
            if not isLineComment:
                station_name = linelst[0]
                location = linelst[1]
                station_minFlow = float(linelst[2])
                riverName = linelst[3]
                stationNickname = linelst[4]
                paddleTasmaniaLink = linelst[5]
                paddleTasmaniaLink_short = linelst[6] #done with goo.gl
                BOM_chartlink = linelst[7] 
                BOM_chartlink_short = linelst[8] #done with goo.gl

                print station_name
            
                #find previous river status
                matching = [s for s in riverStatusdata if station_name in s]
                if not matching:
                    previousRiverStatus = 'steady'
                    riverRunnable_before = False
                elif matching:
                    previousRiverStatus = matching[0][1]
                    if matching[0][2] == 'True':
                        riverRunnable_before = True
                    elif matching[0][2] == 'False': 
                        riverRunnable_before = False
    
                [timeStr,height,currentRiverStatus] = station_info_bom(station_name,location)
                
                #write current river status for next run            
               
                if height>=station_minFlow:
                    riverRunnable_now = True
                    
                if riverRunnable_now == True and riverRunnable_before == False:
                    chgRiverStatus = True
                    writerRiverStatus.write(station_name +','+ currentRiverStatus  +',True\n')
                elif riverRunnable_now == True and riverRunnable_before == True:
                    writerRiverStatus.write(station_name +','+ currentRiverStatus  +',True\n')
                else :
                    chgRiverStatus = False
                    writerRiverStatus.write(station_name +','+ currentRiverStatus  + ',False\n')
                    
                    
                    
                if chgRiverStatus:
                    #send_email(msg)
                    msg = message_BOM(station_name,timeStr,height,currentRiverStatus,riverName,stationNickname,paddleTasmaniaLink_short,BOM_chartlink_short)
                    logger.info('TWEET:'+str(msg))
                    
                    successTweet = send_tweet(msg)
                    if successTweet == 1:
                        logger.info('WARNING : duplicate tweet')
                    elif successTweet == 0:
                        logger.info('Tweet sent')                
                
                elif not chgRiverStatus:
                    logger.info( 'NO CHANGE:' + station_name )
                 
        writerRiverStatus.close()

    except Exception, e:
        logger.error ("ERROR: " + str(e))

    #closes the handlers of the specified logger only    
    x = list(logger.handlers)
    for i in x:
        logger.removeHandler(i)
        i.flush()
        i.close()
   
# WIST STATIONS CHECKER   
from subroutines.dpipwe  import *
def check_river_height_dpipwe():

    try:  
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # create a file handler        
        handler = logging.FileHandler('riverHeight.log')
        handler.setLevel(logging.INFO)
        
        # create a logging format
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # add the handlers to the logger       
        logger.addHandler(handler)
        
        # paddleable river heigts are written in a file on dropbox
        logger.info('Open river height DPIPWE file on dropbox')
        csvFile_dpipwe = urllib2.urlopen('https://www.dropbox.com/s/hjp7hxsf2eatir5/riverHeight_dpipwe.csv?dl=1')
        
        # read river status from previous run        
        pathname = os.path.dirname(sys.argv[0])        
        pythonScriptPath=os.path.abspath(pathname)
        riverStatusFile_DPIPWE = pythonScriptPath + '/riverStatus_DPIPWE.csv'
        if os.path.isfile(riverStatusFile_DPIPWE):
            with open(riverStatusFile_DPIPWE, 'rb') as f:
                riverStatusdata = list(csv.reader(f))
        else :
            riverStatusdata  = []
            
        #write current river status for next run
        writerRiverStatus = open(riverStatusFile_DPIPWE, 'w+')
                
        for line in csvFile_dpipwe:
            #initialise values for each river
            chgRiverStatus = False
            riverRunnable_now = False
            
            linelst = line.split(',')
            isLineComment=line.strip().startswith("#")
            if not isLineComment:
                station_name = linelst[0]
                station_id = int(linelst[1])
                station_minFlow = float(linelst[2])
                riverName = linelst[3]
                stationNickname = linelst[4]
                paddleTasmaniaLink = linelst[5]
                paddleTasmaniaLink_short = linelst[6] #done with goo.gl

                print station_name

               
                dpipwe_data_stations_download(station_name,station_id)
                [station_name,lastdate,stationCurrentFlow,currentRiverStatus] = read_csvData(station_id)
                
                 #find previous river status
                matching = [s for s in riverStatusdata if station_name in s]
                if not matching:
                    previousRiverStatus = 'steady'
                    riverRunnable_before = False
                elif matching:
                    previousRiverStatus = matching[0][1]
                    if matching[0][2] == 'True':
                        riverRunnable_before = True
                    elif matching[0][2] == 'False': 
                        riverRunnable_before = False            
                
                #write current river status for next run            
                if stationCurrentFlow>=station_minFlow:
                    riverRunnable_now = True
                    
                if riverRunnable_now == True and riverRunnable_before == False:
                    chgRiverStatus = True
                    writerRiverStatus.write(station_name +','+ currentRiverStatus  +',True\n')
                elif riverRunnable_now == True and riverRunnable_before == True:
                    writerRiverStatus.write(station_name +','+ currentRiverStatus  +',True\n')
                else :
                    chgRiverStatus = False
                    writerRiverStatus.write(station_name +','+ currentRiverStatus  + ',False\n')
                    
                    
                    
                if chgRiverStatus:
                    #send_email(msg)
                    msg = message_dpipwe(station_name,lastdate,stationCurrentFlow,currentRiverStatus,riverName,stationNickname,paddleTasmaniaLink_short)
                    logger.info('TWEET:'+str(msg))
                    
                    successTweet = send_tweet(msg)
                    if successTweet == 1:
                        logger.info('WARNING : duplicate tweet')
                    elif successTweet == 0:
                        logger.info('Tweet sent')
                                    
                elif not chgRiverStatus:
                    logger.info( 'NO CHANGE:' + station_name )
                 
        writerRiverStatus.close()

    except Exception, e:
        logger.error ("ERROR: " + str(e))
    
    #closes the handlers of the specified logger only    
    x = list(logger.handlers)
    for i in x:
        logger.removeHandler(i)
        i.flush()
        i.close()
        
# Hydro Charts STATIONS CHECKER         
from subroutines.hydro_charts import *  
def check_river_height_hydroChart():
    try:  
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # create a file handler
        
        handler = logging.FileHandler('riverHeight.log')
        handler.setLevel(logging.INFO)
        
        # create a logging format
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # add the handlers to the logger
        
        logger.addHandler(handler)

        pathname = os.path.dirname(sys.argv[0])        
        pythonScriptPath=os.path.abspath(pathname)
        # paddleable river heigts are written in a file on dropbox
        logger.info('Open river height HydroChart file on dropbox')
        csvFile = urllib2.urlopen('https://www.dropbox.com/s/wkmc2db7muys8k8/riverHeight_hydroCharts.csv?dl=1')
    

        
        # read river status from previous run
        riverStatusFile = pythonScriptPath + '/riverStatus_hydroCharts.csv'
        if os.path.isfile(riverStatusFile):
            with open(riverStatusFile, 'rb') as f:
                riverStatusdata = list(csv.reader(f))
        else :
            riverStatusdata  = []
            
        #write current river status for next run
        writerRiverStatus = open(riverStatusFile, 'w+')

        for line in csvFile:
            #initialise values for each river
            
            chgRiverStatus = False
            riverRunnable_now = False
            linelst = line.split(',') 
            isLineComment=line.strip().startswith("#")
            if not isLineComment:
                riverName = linelst[0]                
                station_name = linelst[1]
                station_minValue = linelst[2]
                station_minValue_number = float(linelst[3])
                chartType = (linelst[4])
                hydroChartLink = linelst[5]
                boundingBox  = [int(linelst[6]),int(linelst[7]),int(linelst[8]),int(linelst[9])]
                colorTimeseries   = linelst[10]
                paddleTasmaniaLink = linelst[11]
                hydroChartLink_short = linelst[12] #done with goo.gl
                paddleTasmaniaLink_short = linelst[13] #done with goo.gl

                
                print riverName
            
                #find previous river status
                matching = [s for s in riverStatusdata if station_name in s]
                if not matching:
                    previousRiverStatus = 'steady'
                    riverRunnable_before = False
                elif matching:
                    previousRiverStatus = matching[0][1]
                    if matching[0][2] == 'True':
                        riverRunnable_before = True
                    elif matching[0][2] == 'False': 
                        riverRunnable_before = False
    
                #[timeStr,height,currentRiverStatus] = station_info_bom(station_name,location)
                pdfFile = download_hydroChart(hydroChartLink)
                [convertSuccess, jpgFile] = convert_chart_pdf_to_jpg(pdfFile)
                
                txt_chartFile = convert_chart_pdf_to_txt(pdfFile)
                
                # more comments are needed
                if chartType == 'Height':
                    allY_coordinates = find_min_max_y_axis_height_dam(txt_chartFile)                   
                elif chartType == 'Flow':                
                    allY_coordinates = find_min_max_y_axis_flow(txt_chartFile)
                    
                lowYpixelWhereToLookForData = define_y_pixel_range(allY_coordinates,boundingBox[3],boundingBox[2],station_minValue_number)                 
                boundingBox [3] = lowYpixelWhereToLookForData
                [riverRunnable_now,currentRiverStatus] = range_color_of_pixel_in_bounding_box(jpgFile,boundingBox,colorTimeseries)

                #write current river status for next run            
               
                   
                if riverRunnable_now == True and riverRunnable_before == False:
                    chgRiverStatus = True
                    writerRiverStatus.write(station_name +','+ currentRiverStatus  +',True\n')
                elif riverRunnable_now == True and riverRunnable_before == True:
                    writerRiverStatus.write(station_name +','+ currentRiverStatus  +',True\n')
                else :
                    chgRiverStatus = False
                    writerRiverStatus.write(station_name +','+ currentRiverStatus  + ',False\n')
                    
                    
                    
                if chgRiverStatus:
                    #send_email(msg)
                    msg = message_hydroChart(riverName,station_name,currentRiverStatus,station_minValue,paddleTasmaniaLink_short,hydroChartLink_short)
                    logger.info('TWEET:'+str(msg))
                    
                    successTweet = send_tweet(msg)
                    if successTweet == 1:
                        logger.info('WARNING : duplicate tweet')
                    elif successTweet == 0:
                        logger.info('Tweet sent')                
                
                elif not chgRiverStatus:
                    logger.info( 'NO CHANGE:' + station_name )
                 
        writerRiverStatus.close()

    except Exception, e:
        logger.error ("ERROR: " + str(e))

    #closes the handlers of the specified logger only    
    x = list(logger.handlers)
    for i in x:
        logger.removeHandler(i)
        i.flush()
        i.close()        
        
if __name__ == "__main__":
    try:
        check_river_height_bom()
        check_river_height_hydroChart()
        check_river_height_dpipwe()
    except Exception, e:
        print 
