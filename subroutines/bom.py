
def station_info_bom(station_name,location):
    import string, re, os, time, smtplib, sys, urllib2, csv, os.path, requests, datetime
 
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

#def message_BOM(station_name,timeStr,height,status):
#    import string, os, time, sys, datetime
#
#    # create the string message which will be sent by email or twitter
#    msg = [ str(height) + 'm@' + station_name + ':'+ str(timeStr) +'__RiverStatus:' + str(status)]
#    return msg
    
def message_BOM(station_name,timeStr,height,status,riverName,stationNickname,paddleTasmaniaLink):
    import string, os, time, sys, datetime

    # create the string message which will be sent by email or twitter
    msg =  riverName+' is ' + str(status)  + ' at ' +stationNickname +':'  +  str(height) + 'm at '+ str(timeStr) + '.See ' + paddleTasmaniaLink  
    if len(msg) > 140:
        logger.info('WARNING : Tweet size greater than 140')
        
    return msg