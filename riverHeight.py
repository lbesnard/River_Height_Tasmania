#!/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Laurent Besnard
# email address: laurent.besnard@utas.edu.au
# Website: https://github.com/lbesnard/River_Height_Tasmania
# May 2013; Last revision: 15-May-2014
#
# The script is distributed under the terms of the GNU General Public License 


import string, re, os, time, smtplib, sys, urllib2, csv, os.path, logging
 
 
def station_info(station_name,location):
    
    import requests
    # Getting webpage to check according to the river to check
    if location == 'NORTH':
        url = 'http://www.bom.gov.au/cgi-bin/wrap_fwo.pl?IDT60151.html'
    elif location == 'SOUTH':
        url = 'http://www.bom.gov.au/cgi-bin/wrap_fwo.pl?IDT60152.html'
    elif location == 'NORTHWEST':
        url = 'http://www.bom.gov.au/cgi-bin/wrap_fwo.pl?IDT60150.html'
        
    html = requests.get(url).text
       
    start_tag = '<td>' +station_name
    end_tag = 'Table</a></td>\n</tr>\n<tr>\n'
    startIndex = html.find(start_tag) + len(start_tag)
    endIndex = html.find(end_tag, startIndex) + len(end_tag) - 1
    raw_data = html[startIndex:endIndex]
    

    #regular expression of the BOM webpage
    mobj = re.search('<.*>(.*)</.*>\n  <.*>(.*)</.*>\n  <.*>(.*)</.*>\n  ', raw_data)
    timeStr = mobj.groups()[0].strip('"')
    height = float(mobj.groups()[1].strip('"').replace("^",""))
    status = mobj.groups()[2].replace(" ","")
    
    return timeStr,height,status

def message(station_name,timeStr,height,status):
    # create the string message which will be sent by email or twitter
    msg = [ str(height) + 'm@' + station_name + ':'+ str(timeStr) +'__RiverStatus:' + str(status)]
    return msg
    
    
def send_email(msg):
    fromaddr = '**********@gmail.com'
    toaddrs = '***********@gmail.com'
    bodytext = 'From: %s\nTo: %s\nSubject: %s\n\n%s' %(fromaddr, toaddrs, msg, msg)
   
    # Credentials (if needed)
    username = '********@gmail.com'
    password = '**********' 
  
    # The actual mail sent
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, bodytext)
    server.quit()
 
def send_tweet(msg):
    # http://mike.verdone.ca/twitter/  needs to be installed. easy_install twitter ()
    import subprocess
    command = 'twitter -e besnard.laurent@gmail.com set %s' % msg
    success = subprocess.call(command, shell=True)
    
    return success


  
if __name__ == "__main__":
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
        logger.info('Open river height file on dropbox')
        csvFile = urllib2.urlopen('https://www.dropbox.com/s/wdbh6m804p4lkwx/riverHeight.csv?dl=1')
    

        
        # read river status from previous run
        riverStatusFile = pythonScriptPath + '/riverStatus.csv'
        if os.path.isfile(riverStatusFile):
            with open(riverStatusFile, 'rb') as f:
                data = list(csv.reader(f))
        else :
            data  = []
            
        #write current river status for next run
        writerRiverStatus = open(pythonScriptPath + '/riverStatus.csv', 'w+')

        for line in csvFile:
            #initialise values for each river
            chg = False
            riverRunnable_now = False
            
            linelst = line.split(',')
            station_name = linelst[0]
            location = linelst[1]
            
            #find previous river status
            matching = [s for s in data if station_name in s]
            if not matching:
                previousRiverStatus = 'steady'
                riverRunnable_before = False
            elif matching:
                previousRiverStatus = matching[0][1]
                if matching[0][2] == 'True':
                    riverRunnable_before = True
                elif matching[0][2] == 'False': 
                    riverRunnable_before = False

            [timeStr,height,currentRiverStatus] = station_info(station_name,location)
            
            #write current river status for next run            
           
            if height>=float(linelst[2]):
                riverRunnable_now = True
                
            if riverRunnable_now == True and riverRunnable_before == False:
                chg = True
                writerRiverStatus.write(station_name +','+ currentRiverStatus  +',True\n')
            elif riverRunnable_now == True and riverRunnable_before == True:
                writerRiverStatus.write(station_name +','+ currentRiverStatus  +',True\n')
            else :
                chg = False
                writerRiverStatus.write(station_name +','+ currentRiverStatus  + ',False\n')
                
                
                
            if chg:
                #send_email(msg)
                msg = message(station_name,timeStr,height,currentRiverStatus)
                logger.info('TWEET:'+str(msg[0]))
                
                successTweet = send_tweet(msg)
                if success == 1:
                    logger.info('WARNING : duplicate tweet')
                elif success == 0:
                    logger.info('Tweet sent')                
            
            elif not chg:
                logger.info( 'NO CHANGE:' + station_name )
                 
        writerRiverStatus.close()

    except Exception, e:
        logger.error ("ERROR: " + str(e))