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