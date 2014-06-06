#!/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Laurent Besnard
# email address: laurent.besnard@utas.edu.au
# Website: https://github.com/lbesnard/River_Height_Tasmania
# May 2013; Last revision: 15-May-2014
#
# The script is distributed under the terms of the GNU General Public License 

# this script takes a list of string numbers as in input. Those numbers are the
# stations id's from http://wrt.tas.gov.au/wist/ui
# The function stations_DPIPWE_csv needs to open firefox to download the data.
# The website needs the user to do a series of actions before letting him 
# download any data.
# if a user put the value of url_query (see below) directly in its web browser,
# he will experience a 500 error. 
# This is quite a shame data can't be retrieved in an easier way but there is no
# much way around it. 
# What is really important is actually the sequence number pageSequenceNo
# future development would be about improving the waiting process, when something
# in a page is found http://selenium-python.readthedocs.org/en/latest/waits.html
# and error handling which is not being done atm


def data_folder():
    global  csvDir 
    csvDir = '/tmp/riverData'


def dpipwe_data_stations_download(station_name,station_id):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from time import sleep
    import shutil
    import string, os, time,datetime,path
    
    data_folder()
    if os.path.exists(csvDir):
        shutil.rmtree(csvDir)

    # To prevent download dialog
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', csvDir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    

    
    # open firefox
    driver = webdriver.Firefox(firefox_profile=profile)
    driver.implicitly_wait(16) # seconds
    
    # home page
    driver.get("http://wrt.tas.gov.au/wist/ui") # seconds
    #driver.implicitly_wait(3) # seconds
    
    # open water flow page - sequence number is important and incremented
    pageSequenceNo = 2
    driver.get('http://wrt.tas.gov.au/wist/ui?command=content&pageSequenceNo='+ str(pageSequenceNo) +'&click=[0].Name#fopt')
    #driver.implicitly_wait(3) # seconds
    
    # open Search for water flow data 
    pageSequenceNo = 3
    driver.get('http://wrt.tas.gov.au/wist/ui?command=content&pageSequenceNo='+ str(pageSequenceNo) +'&click=[1].Name#fopt')
    
    # click on button continue and wait
    element = driver.find_element_by_id("ID0").click()
    #driver.implicitly_wait(12) # seconds
    
    
    ## this is arbitrary since we need to enter at least one station_name in the page in order to download anything else from any other stations
    #station_name = 'NORTH WEST BAY RIVULET AT MARGATE WATER SUPPLY INTAKE'
    
    # find in page where the station_name can be entered
    element = driver.find_element_by_id("ID2")
    #driver.implicitly_wait(3) # seconds
    
    element.send_keys(station_name)
    #driver.implicitly_wait(3) # seconds
    
    # click on continue
    driver.find_element_by_id("ID3").click()
    #driver.implicitly_wait(4) # seconds
    
    sleep(3) # to force python to wait for 2 secondes before downloading any data
    # click on raw data as csv
    data = driver.find_element_by_id("ID4").click()
    #driver.find_element_by_id("ID4").click().implicitly_wait(4) # seconds
    
    
    now = datetime.datetime.now()
    start_date = now.strftime("%d-%m-%Y")
    end_date = start_date
    pageSequenceNo = 7
    #for station_number in station_list_id:
         # from here the sequence number is  7 , and any data can be downloaded from any station
        
    url_query = 'http://wrt.tas.gov.au/wist/ui/StationNo.' + str(station_id) + '-StreamFlow-' + start_date +'-to-' + end_date + '.csv?command=download&pageSequenceNo='+ str(pageSequenceNo) +'&fieldName=[1].DownloadsTable[0].FileData'
    #print url_query        
    data = driver.get(url_query)
    #sleep(4)
    #pageSequenceNo += 1
        
    driver.close()



def read_csvData(station_id):
    import glob
    data_folder()
    csvfile = glob.glob(csvDir+'/StationNo.' + str(station_id) +'-*.csv')    

    # read first and last 2 lines
    with open(csvfile[0], 'rb') as fh:
        headline = next(fh).decode()
        dataEnd = tail(fh,window=2)
    
    # we look for the station name
    import re,string
    mobj = re.search('-StationNo'+str(station_id), (headline))
    station_name = str(headline[0:headline.index('-StationNo')])
    
    # we separate the 2 last lines in individual variables   
    firstData_str = dataEnd[0:dataEnd.index('\n')]
    secondData_str = dataEnd[dataEnd.index('\n')+1:]
    
    # flow of the river 
    cumecs1 = float(firstData_str.split(",")[2])
    from datetime import datetime

    lastdate = datetime.strptime(secondData_str.split(",")[1], '%d/%m/%Y - %H:%M')
    cumecs2 = float(secondData_str.split(",")[2])
    currentflow = cumecs2
    # check river status
    if cumecs2 - cumecs1 == 0:
        currentRiverStatus = 'steady'
    elif cumecs2 - cumecs1 > 0:
        currentRiverStatus = 'rising'
    elif cumecs2 - cumecs1 < 0:
        currentRiverStatus = 'falling'


    return station_name,lastdate,cumecs2,currentRiverStatus


def message_dpipwe(station_name,lastdate,currentflow,currentRiverStatus):
    # create the string message which will be sent by email or twitter
    msg = [ str(currentflow) + 'cumecs@' + station_name + ':'+ lastdate.strftime("%Y-%m-%d %H:%M:%S")  +'__RiverStatus:' + str(currentRiverStatus)]
    return msg
    
    
def tail( f, window=20 ):
    # read from a f open file , the last window lignes
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = window
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if (bytes - BUFSIZ > 0):
            # Seek back one whole BUFSIZ
            f.seek(block*BUFSIZ, 2)
            # read BUFFER
            data.append(f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            data.append(f.read(bytes))
        linesFound = data[-1].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    return '\n'.join(''.join(data).splitlines()[-window:])    
    #import glob
    #files = glob.glob(csvDir+'/*csv.part')    
    #files.sort(key=lambda x: os.path.getmtime(x))
    #newest_file = files[-1]
    
    #csvFileName = "riverData.csv"
    #os.rename(newest_file,csvFileName)