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
        
        # to create a html page later on
        riverStatusFile_BOM_CSV_for_Webpage = pythonScriptPath + '/riverStatus_BOM_CSV_for_Webpage.csv'
        writerRiverStatus_BOM_CSV_for_Webpage = open(riverStatusFile_BOM_CSV_for_Webpage, 'w+')
        
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
                BOM_chartlink_short = linelst[8].rstrip('\n') #done with goo.gl

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
                    
                #create current BOM status text file to create later on a html page
                writerRiverStatus_BOM_CSV_for_Webpage.write(riverName +','+ station_name  +','+ paddleTasmaniaLink_short + ',' + BOM_chartlink_short + ',' + str(station_minFlow) + 'm' +  ',' + str(height) +'m' +','  + timeStr +  ',' + currentRiverStatus +',' + str(riverRunnable_now) + '\n')
    
                 
        writerRiverStatus.close()
        writerRiverStatus_BOM_CSV_for_Webpage.close()
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
        
        # to create a html page later on
        riverStatusFile_DPIPWE_CSV_for_Webpage = pythonScriptPath + '/riverStatus_DPIPWE_CSV_for_Webpage.csv'
        writerRiverStatus_DPIPWE_CSV_for_Webpage = open(riverStatusFile_DPIPWE_CSV_for_Webpage, 'w+')
                
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
                paddleTasmaniaLink_short = linelst[6].rstrip('\n') #done with goo.gl

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
                    
                 #create current BOM status text file to create later on a html page
                writerRiverStatus_DPIPWE_CSV_for_Webpage.write(riverName +','+ station_name  +','+ paddleTasmaniaLink_short + ',' + 'No Chart available' + ',' + str(station_minFlow) + 'Cumecs' +  ',' + str(stationCurrentFlow) +'Cumecs' +','  + lastdate.strftime("%Y-%m-%d %H:%M:%S") +  ',' + currentRiverStatus +',' + str(riverRunnable_now) + '\n')
        
                 
        writerRiverStatus.close()
        writerRiverStatus_DPIPWE_CSV_for_Webpage.close()

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

        # to create a html page later on
        riverStatusFile_HYDRO_CSV_for_Webpage = pythonScriptPath + '/riverStatus_HYDRO_CSV_for_Webpage.csv'
        writerRiverStatus_HYDRO_CSV_for_Webpage = open(riverStatusFile_HYDRO_CSV_for_Webpage, 'w+')

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
                paddleTasmaniaLink_short = linelst[13].rstrip('\n') #done with goo.gl

                
                print riverName
            
                #find previous river status
                matching = [s for s in riverStatusdata if riverName in s]
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
                    writerRiverStatus.write(riverName +','+ currentRiverStatus  +',True\n')
                elif riverRunnable_now == True and riverRunnable_before == True:
                    writerRiverStatus.write(riverName +','+ currentRiverStatus  +',True\n')
                else :
                    chgRiverStatus = False
                    writerRiverStatus.write(riverName +','+ currentRiverStatus  + ',False\n')
                    
                    
                    
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
                
                writerRiverStatus_HYDRO_CSV_for_Webpage.write(riverName +','+ station_name  +','+ paddleTasmaniaLink_short + ',' + hydroChartLink_short    + ',' + station_minValue  +  ',' + 'N.A.' +','  +  datetime.datetime.now().strftime("%Y-%m-%d") +  ',' + currentRiverStatus +',' + str(riverRunnable_now) + '\n')

                 
        writerRiverStatus.close()
        writerRiverStatus_HYDRO_CSV_for_Webpage.close()
        
    except Exception, e:
        logger.error ("ERROR: " + str(e))

    #closes the handlers of the specified logger only    
    x = list(logger.handlers)
    for i in x:
        logger.removeHandler(i)
        i.flush()
        i.close()        
        
        
def createStatus_webpage():
    # needs to be on the Public folder of Dropbox.
    # the DropboxPath value should be written in a config file

    pathname = os.path.dirname(sys.argv[0])        
    pythonScriptPath=os.path.abspath(pathname)  
    DropboxPath = '/home/lbesnard/Dropbox'

    text_file = open(DropboxPath +"/Public/RiverStatusTasmania.html", "w")
    text_file.write("<!DOCTYPE html>\n")
    text_file.write("<html>\n")
    text_file.write("<head>\n")
    text_file.write("<style>\n")
    text_file.write("table,th,td\n")
    text_file.write("{border:1px solid black;border-collapse:collapse;}\n")
    text_file.write("</style>\n")
    text_file.write("</head>\n")
    text_file.write("<body>\n")
    text_file.write("<p><font size=\"20\"><b>Tasmania River Status in near real time - Beta</b></font></p>\n\n\n")
    text_file.write("<p>Last page update at "+ datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") +"</p>\n\n\n")
    text_file.write("<table>\n")
    text_file.write("  <tr>\n")
    text_file.write("    <th>River Name</th>\n")
    text_file.write("    <th>Station Name</th>\n")
    text_file.write("    <th>PaddleTas Guide</th>\n")
    text_file.write("    <th>Chart</th>\n")
    text_file.write("    <th>Minimum Paddleable height/flow</th>\n")
    text_file.write("    <th>Current height/flow</th>\n")
    text_file.write("    <th>Time</th>\n")
    text_file.write("    <th>Steady/Rising/Droping</th>\n")
    text_file.write("    <th>Kayakable ?</th>\n")
    text_file.write("  </tr>\n")
    
    #BOM
    riverStatusFile_BOM_CSV_for_Webpage = pythonScriptPath + '/riverStatus_BOM_CSV_for_Webpage.csv'
    if os.path.isfile(riverStatusFile_BOM_CSV_for_Webpage):
        csvFile = open(riverStatusFile_BOM_CSV_for_Webpage)
        for line in csvFile:        
            linelst = line.split(',') 
            isLineComment=line.strip().startswith("#")
            if not isLineComment:
                river_name = linelst[0]
                station_name = linelst[1]
                paddleTas_guide = linelst[2]
                chart = linelst[3]
                minimum_PaddleableValue = linelst[4]
                currentValue = linelst[5]
                dataTime = linelst[6]
                riverStatus = linelst[7]
                kayakable  = linelst[8].rstrip('\n')
                
                text_file.write("  <tr>\n")
                text_file.write("<th>"+ river_name + "</th>\n")
                text_file.write("<th>"+ station_name  + "</th>\n")
                text_file.write("<th><a href=\"http:\\" +paddleTas_guide  +"\">Topo</a></th>\n")
                text_file.write("<th><a href=\"http:\\" +chart  +"\">Chart</a></th>\n")
                text_file.write("<th>"+ minimum_PaddleableValue + "</th>\n")
                text_file.write("<th>"+ currentValue + "</th>\n")
                text_file.write("<th>"+ dataTime + "</th>\n")
                text_file.write("<th>"+ riverStatus + "</th>\n")
                if kayakable == 'True':
                    text_file.write("<td bgcolor=\"#00ff00\">Yes</td>\n")
                if kayakable == 'False':
                    text_file.write("<td bgcolor=\"#ff0000\">No</td>\n")    
                
                text_file.write("</tr>\n")
                
    #DPIPWE
    riverStatusFile_DPIPWE_CSV_for_Webpage = pythonScriptPath + '/riverStatus_DPIPWE_CSV_for_Webpage.csv'
    if os.path.isfile(riverStatusFile_DPIPWE_CSV_for_Webpage):
        csvFile = open(riverStatusFile_DPIPWE_CSV_for_Webpage)
        for line in csvFile:        
            linelst = line.split(',') 
            isLineComment=line.strip().startswith("#")
            if not isLineComment:
                river_name = linelst[0]
                station_name = linelst[1]
                paddleTas_guide = linelst[2]
                chart = linelst[3]
                minimum_PaddleableValue = linelst[4]
                currentValue = linelst[5]
                dataTime = linelst[6]
                riverStatus = linelst[7]
                kayakable  = linelst[8].rstrip('\n')
                
                text_file.write("  <tr>\n")
                text_file.write("<th>"+ river_name + "</th>\n")
                text_file.write("<th>"+ station_name  + "</th>\n")
                text_file.write("<th><a href=\"http:\\" +paddleTas_guide  +"\">Topo</a></th>\n")
                text_file.write("<th> No Chart available</th>\n")
                text_file.write("<th>"+ minimum_PaddleableValue + "</th>\n")
                text_file.write("<th>"+ currentValue + "</th>\n")
                text_file.write("<th>"+ dataTime + "</th>\n")
                text_file.write("<th>"+ riverStatus + "</th>\n")
                if kayakable == 'True':
                    text_file.write("<td bgcolor=\"#00ff00\">Yes</td>\n")
                if kayakable == 'False':
                    text_file.write("<td bgcolor=\"#ff0000\">No</td>\n")    
                
                text_file.write("</tr>\n")                
              

    #HYDRO
    riverStatusFile_HYDRO_CSV_for_Webpage = pythonScriptPath + '/riverStatus_HYDRO_CSV_for_Webpage.csv'
    if os.path.isfile(riverStatusFile_HYDRO_CSV_for_Webpage):
        csvFile = open(riverStatusFile_HYDRO_CSV_for_Webpage)
        for line in csvFile:        
            linelst = line.split(',') 
            isLineComment=line.strip().startswith("#")
            if not isLineComment:
                river_name = linelst[0]
                station_name = linelst[1]
                paddleTas_guide = linelst[2]
                chart = linelst[3]
                minimum_PaddleableValue = linelst[4]
                currentValue = linelst[5]
                dataTime = linelst[6]
                riverStatus = linelst[7]
                kayakable  = linelst[8].rstrip('\n')
                
                text_file.write("  <tr>\n")
                text_file.write("<th>"+ river_name + "</th>\n")
                text_file.write("<th>"+ station_name  + "</th>\n")
                text_file.write("<th><a href=\"http:\\" +paddleTas_guide  +"\">Topo</a></th>\n")
                text_file.write("<th><a href=\"http:\\" +chart  +"\">Chart</a></th>\n")
                text_file.write("<th>"+ minimum_PaddleableValue + "</th>\n")
                text_file.write("<th>"+ currentValue + "</th>\n")
                text_file.write("<th>"+ dataTime + "</th>\n")
                text_file.write("<th>"+ riverStatus + "</th>\n")
                if kayakable == 'True':
                    text_file.write("<td bgcolor=\"#00ff00\">Yes</td>\n")
                if kayakable == 'False':
                    text_file.write("<td bgcolor=\"#ff0000\">No</td>\n")    
                
                text_file.write("</tr>\n")
                
          # end code of html file     


    text_file.write("</table>\n")
    
    text_file.write("<p>This webpage is a beta version. Its purpose is simple, to have all the Tasmanian rivers status visible at once. Things can be improved. Don't hesitate to contact me to give me your feedbacks</p>\n")
    text_file.write("<a href=\"mailto:besnard.laurent@gmail.com\">email</a> \n")
    text_file.write("\n\n\n<p><a href=\"https://www.facebook.com/CreekingTasmaniaRiverFlows\">Facebook page : CreekingTasmaniaRiverFlows</a></p>\n")
    text_file.write("<p><a href=\"https://github.com/lbesnard/River_Height_Tasmania\">Github repository</a></p>\n")
    text_file.write("</body>\n")
    text_file.write("</html>\n")            
    text_file.close()

        
            
            
            
if __name__ == "__main__":
    try:
        check_river_height_bom()
        check_river_height_hydroChart()
        check_river_height_dpipwe()
        createStatus_webpage()
    except Exception, e:
        print 
