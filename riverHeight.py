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
from subroutines.bom import *
from subroutines.send_notification import *
    
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
            station_name = linelst[0]
            location = linelst[1]
            
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
           
            if height>=float(linelst[2]):
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
                msg = message_BOM(station_name,timeStr,height,currentRiverStatus)
                logger.info('TWEET:'+str(msg[0]))
                
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
            station_name = linelst[0]
            station_id = int(linelst[1])
            station_minFlow = float(linelst[2])
            
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
                msg = message_dpipwe(station_name,lastdate,stationCurrentFlow,currentRiverStatus)
                logger.info('TWEET:'+str(msg[0]))
                
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
        check_river_height_dpipwe()
    except Exception, e:
        print 
