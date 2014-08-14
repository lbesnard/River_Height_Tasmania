
def station_info_bom(station_name,location):
    import string, re, os, time, smtplib, sys, urllib2, csv, os.path, requests, datetime
    
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
    
    if html.find(start_tag) != -1:
        #regular expression of the BOM webpage
        mobj = re.search('<.*>(.*)</.*>\n  <.*>(.*)</.*>\n  <.*>(.*)</.*>\n  ', raw_data)
        timeStr = mobj.groups()[0].strip('"')
        height = float(mobj.groups()[1].strip('"').replace("^",""))
        status = mobj.groups()[2].replace(" ","")
    else:
        logger.warning ("WARNING: " + str('station ' + station_name  + ' cannot be found on the BOM webpage'))
        timeStr = 'N.A.'
        height = float(0)
        status = 'N.A.'
        
    return timeStr,height,status 

#def message_BOM(station_name,timeStr,height,status):
#    import string, os, time, sys, datetime
#
#    # create the string message which will be sent by email or twitter
#    msg = [ str(height) + 'm@' + station_name + ':'+ str(timeStr) +'__RiverStatus:' + str(status)]
#    return msg
    
def message_BOM(station_name,timeStr,height,status,riverName,stationNickname,paddleTasmaniaLink,BOM_chartlink_short):
    import string, os, time, sys, datetime
    
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
    # create the string message which will be sent by email or twitter
    msg =  riverName+' is ' + str(status)  + ' at ' +stationNickname +':'  +  str(height) + 'm at '+ str(timeStr) + '.See Chart: ' +BOM_chartlink_short + ' Guide: ' + paddleTasmaniaLink  
    if len(msg) > 140:
        logger.info('WARNING : Tweet size greater than 140')
        
    return msg