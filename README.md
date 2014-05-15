River_Height_Tasmania
=====================

A tool to send notification on twitter when a river is paddleable


G'Day
I was a bit bored yesterday, and frustrated I didn't check the BOM website and missed out on a North Esk trip last Sunday. So I coded a python script to send a notification on my phone each time a river is at the minimum/perfect paddling level.
Pretty simple, and definitely geeky but it's useful to me so I'm sure it would be useful to someone, especially with winter time coming.
--------------------------
|HOW IT WORKS| ---->
--------------------------
1) My python script connects to the BOM website
2) it downloads and reads at the same time a text configuration file of which rivers to check, and the level where they are paddleable.
here is the file :
https://www.dropbox.com/s/wdbh6m804p4lkwx/riverHeight.csv?dl=1 
The reason why the file is on dropbox is because I can update it from any computer, not necessarily from where the main script is running from.
the convention of this file is:
{BOM Station name},{NORTH,SOUTH,NORTHWEST BOM webpage, because there are 3 different webpages),{runnable height}
For example, to run the North Esk, the minimum level is around 1.6m online, so I need to add a line like this :
North Esk Rv at Corra Linn,NORTH,1.60
3) ONLY if the conditions defined below are found, will the Python script send a tweet on a twitter account I have just created for this purpose (https://twitter.com/besnard_laurent)
Conditions :
current height >= paddleable height
current river Status is rising
river status on the previous script run is either falling or steady
The last condition helps to avoid sending notifications every hour for days and days if the river is on. This could become quite annoying. This little tool is just valuable to warn that something is happening
The tweet would be something like [height@StationName: TIME__RiverStatus:status] :
[3.8m@Lake Leake: 6.00pm Mon__RiverStatus:steady]
[1.83m@South Esk Rv at Fingal: 6.12pm Mon__RiverStatus:steady]
4) Where this tool becomes really handy is if you have a smartphone. Because you can simply install twitter on it, 'follow me' (https://twitter.com/besnard_laurent) and you'll get a notification on your phone when it's time to get wet (if you have the 3g and mobile data or wifi on) ! I promise not to put any naked pics of me. And because it's just a notification, it takes almost no bandwidth, and it appears on your screen even if it's locked (well I'm sure this can be configured easily by you anyway)
5) my script is supposed to run every hour, every day. I'm happy to improve it, it's dead easy. I could also send emails...
So far i only put a few rivers:
North Esk Rv at Corra Linn,NORTH,1.60
St Patricks Rv at Nunamara Offtake,NORTH,1.1
Huon Rv at Tahune Bdge,SOUTH,0.6
Forth Rv blw Wilmot (H),NORTHWEST,4
Meander Rv at Meander,NORTH,1.0
Meander Rv at Deloraine Rwy Br (H),NORTH,0.9
But I'm happy to add more, and modify the required heights to paddle them.
Future improvements :
-Well it would be pretty cool to do the same thing with Hydro. Haven't checked this out much, but I think they mainly give pdf files, which is quite tricky to use (I'm not going to do any OCR on pdf !!)
- any ideas ?
So far there are only few useless entries on the twitter page. They're just here as an example, since no river is runnable yet. But as soon as it will rain, be sure to receive a notification at 3am !
cheerio
Loz
