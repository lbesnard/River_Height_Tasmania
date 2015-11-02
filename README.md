River Heights Tasmania : a kayakers dream tool !
=====================

A tool to check the current height of Tasmanian rivers with an online gauge and to send notifications via twitter/facebook when a river is paddleable.

Data from DPIPWE, Hydro and BOM are checked every half an hour. If a river is above a certain flow/height, and wasn't in the previous run of the script, a notification is sent to a twitter account (which can be then seen automatically on a smartphone), and is then synced to facebook.
* [CreekingTasmaniaRiverFlows_Twitter](https://twitter.com/besnard_laurent)
* [CreekingTasmaniaRiverFlows_Facebook](https://www.facebook.com/CreekingTasmaniaRiverFlows?fref=nf)

A summary page is also updated every half hour:
* [RiverStatusTasmania](http://www.elcaminoloco.net/tas_river/RiverStatusTasmania.html)



# INFORMATION 
Links to the different config files
* https://www.dropbox.com/s/g81irf5nhad8y8r/riverHeight_bom.csv?dl=1
* https://www.dropbox.com/s/hjp7hxsf2eatir5/riverHeight_dpipwe.csv?dl=1
* https://www.dropbox.com/s/wkmc2db7muys8k8/riverHeight_hydroCharts.csv?dl=1


## BOM
Checking data from BOM is quite straight forward. A page such as www.bom.gov.au/cgi-bin/wrap_fwo.pl?IDT60151.html is checked and then values are simply retrieved 

## DPIPWE
The DPIPWE website is more complicated to handle. Although near-realtime csv files are downloadable, the link to download the data from each station expires after each download. The Selenium driver is used to simulate a web browser, and automatically perform tasks.


## HYDRO
Data only exists as different pdf files, with a mix of timeseries images and embedded text. Plots have a changeable scale. Looking for the min and max values to know what the flow (MG/L) per pixel is, is the priority. I'm then looking for the existance or not of blue pixels of the timeseries (for example) within a box. No accurate data is given since the image quality of the timeseries would only give approximate values.

## Installation

Crontab
```
PATH=$HOME/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
0,30 *  * * * . $HOME/.profile;  export DISPLAY=:0 && python /opt/River_Height_Tasmania/riverHeight.py ; ftp_upload.sh

```
