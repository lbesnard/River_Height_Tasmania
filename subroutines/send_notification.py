def send_email(msg):
    fromaddr = '***@gmail.com'
    toaddrs = '***@gmail.com'
    bodytext = 'From: %s\nTo: %s\nSubject: %s\n\n%s' %(fromaddr, toaddrs, 'paddle is on', msg)
   
    # Credentials (if needed)
    username = '***'
    password = '***' 
  
    # The actual mail sent
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, bodytext)
    server.quit()
 
def send_tweet(msg):
    # http://mike.verdone.ca/twitter/  needs to be installed. easy_install twitter ()
    import subprocess
    command = 'twitter set %s' % msg
    success = subprocess.call(command, shell=True)
    
    return success