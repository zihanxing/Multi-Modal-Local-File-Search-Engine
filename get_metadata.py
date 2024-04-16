import os
from datetime import datetime
from pathlib import Path
from datetime import datetime, timezone


def timeConvert(atime):
#   dt = atime
#   newtime = datetime.fromtimestamp(dt)
#   return newtime.date()
    # Convert timestamp to datetime object
    dt = datetime.fromtimestamp(atime)

    # Convert datetime object to RFC 3339 format
    date_time = dt.astimezone(timezone.utc)

    return date_time
   
def sizeFormat(size):
    newform = format(size/1024, ".2f")
    return newform + " KB"


def createFileRecords(somepath):
    #dictionary
    firstDict = {}
    
    stats = os.stat(somepath)
    attrs = {
        # 'File Name': name,
        'Size (KB)': sizeFormat(stats.st_size),
        'Creation Date': timeConvert(stats.st_ctime),
        'Modified Date': timeConvert(stats.st_mtime),
        'Last Access Date': timeConvert(stats.st_atime),   
    }
    
    
    # firstDict[name] = attrs 

    
    return attrs 
