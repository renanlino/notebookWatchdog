import sys
import urllib2
from datetime import datetime

timeNow = datetime.now()
datetime = "%d/%d/%d-%d:%d:%d" %(timeNow.day, timeNow.month, timeNow.year, timeNow.hour, timeNow.minute, timeNow.second)

url = "http://www.rlino.com.br/notebookWatchdog/writeData.cgi?temp=%s&datetime=%s" %(sys.argv[1], datetime)
resposta = urllib2.urlopen(url)
        
