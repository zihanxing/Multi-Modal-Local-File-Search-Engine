import os
from datetime import datetime, timezone
from pathlib import Path


def timeConvert(atime):
    """
    Convert timestamp to RFC 3339 format.

    Args:
        atime (float): The timestamp.

    Returns:
        datetime: The converted datetime object.
    """
    dt = datetime.fromtimestamp(atime)
    date_time = dt.astimezone(timezone.utc)
    return date_time
   
def sizeFormat(size):
    """
    Convert file size to KB format.

    Args:
        size (int): The file size in bytes.

    Returns:
        str: The file size in KB format.
    """
    newform = format(size/1024, ".2f")
    return newform + " KB"


def createFileRecords(somepath):
    """
    Create file records for a given path.

    Args:
        somepath (str): The path to the file.

    Returns:
        dict: A dictionary containing file attributes.
    """
    firstDict = {}
    
    stats = os.stat(somepath)
    attrs = {
        'Size (KB)': sizeFormat(stats.st_size),
        'Creation Date': timeConvert(stats.st_ctime),
        'Modified Date': timeConvert(stats.st_mtime),
        'Last Access Date': timeConvert(stats.st_atime),   
    }
    
    return attrs 
