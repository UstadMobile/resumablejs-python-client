
import sys
import cookielib
import requests
import urllib2
from io import BytesIO
from mimetypes import MimeTypes
import urllib
import os
import time

try:
    fileToUpload = sys.argv[1:][0]
    filepath = sys.argv[1:][0]
    url = sys.argv[1:][1]
    chunkSize = sys.argv[1:][2]
    chunkRetries = sys.argv[1:][3]
    
    try:
        file_in = open(sys.argv[1:][0], "rb")
	
    except:
	print("!ERROR in file given!")
	print("Unable to open file. Does the file exist?")
except:
    print("!ERROR in usage!")
    print("Run as: <script> <File (whole path)> <upload url> <chunk size> <chunk retries number>")
    sys.exit(1)

class uploadConfig(object):
    resumableChunkSize = 1048576
    maxRetries = 10
    url = ""
    
    
    def __init__(self, resumableChunkSize, maxRetries, url):
	self.resumableChunkSize = resumableChunkSize
	self.maxRetries = maxRetries
	self.url = url

default = uploadConfig(int(chunkSize), int(chunkRetries), str(url))
print("Default Chunk Size:" + str(default.resumableChunkSize))

#Class representingg the job.
class UploadJob(object):
    resumableChunkNumber = 0
    resumableTotalChunks = 0
    resumableChunkSize = 0
    resumableTotalSize = 0
    resumableIdentifier = ""
    resumableFilename = ""
    resumableRelativePath = ""
    resumableType = ""

    def __init__(self, chunknumber, totalchunks, chunksize, totalsize, identifier, filename, relativepath, resumabletype):
        self.resumableChunkNumber = chunknumber
	self.resumableTotalChunks = totalchunks
	self.resumableChunkSize = chunksize
	self.resumableTotalSize = totalsize
	self.resumableIdentifier = identifier
	self.resumbaleFilename = filename
	self.resumableRelativePath = relativepath
	self.resumableType = resumabletype


    def next_chunk(self):
        self.resumableChunkNumber = self.resumableChunkNumber + 1;
    

#Get mime type
try:
    mime = MimeTypes()
    murl = urllib.pathname2url(filepath)
    mime_type = mime.guess_type(murl)[0]
    if mime_type == None:
        print("Couldn't determine. Defaulting.")
        mime_type = 'text/plain'
    print("Mime of the provided file is : " + str(mime_type))

except:
    print("!!Error in getting mime type. Defaulting to text.")
    mime_type = 'text/plain'

#Get basename
basename=os.path.basename(filepath)

print("Opening file : " + str(filepath))
file_in = open(filepath, "rb")

retries = 0
bytesSent = 0
bytes_read = 0
chunknumber = 0
total_bytes = len(file_in.read())
file_in.seek(0)
print("Total File size : " + str(total_bytes))

totalchunks = total_bytes / default.resumableChunkSize + 1

uploadJob = UploadJob(0, totalchunks, default.resumableChunkSize, total_bytes, str(total_bytes)+"-"+basename, basename, str(total_bytes)+"-"+basename, mime_type)

#try:
if True:
    
    status_code = 0
    while (chunknumber <= totalchunks and retries < default.maxRetries and bytesSent < total_bytes):
        #try: 
	if True:
            
            chunknumber = chunknumber + 1
            print("Attempting to process chunk " + str(chunknumber) + "/" + str(totalchunks) + "...")
            chunk = bytearray(default.resumableChunkSize)
            bytes_read = file_in.readinto(chunk)
            chunk = chunk[:bytes_read]
            if chunk != None:
                retries = 0
            print("Trying to send this chunk of length: " + str((bytes_read)))
            
            retries =0
            while(retries < default.maxRetries):
                if (retries > 0):
                    print(".. retrying " + str(retries + 1) + "/" + str(default.maxRetries) + "..")

                decode = str(chunk)
                params = {'file': decode}
                data = {
                        'resumableChunkNumber':chunknumber,
                        'resumableType':mime_type,
                        'resumableChunkSize':default.resumableChunkSize,
                        'resumableIdentifier':str(total_bytes)+"-"+basename,
                        'resumableTotalSize':total_bytes,
                        'resumableRelativePath':str(total_bytes)+"-"+basename,
                        'resumableCurrentChunkSize':bytes_read,
                        'resumableFilename':basename,
                        'resumableTotalChunks':totalchunks,
                        }
                params = {'file':('file', decode)}
       
                try:    
    
                    response = requests.post(default.url, files=params, data=data)
                    print("Response code: " + str(response.status_code))
                    status_code = response.status_code
                    if status_code == 200:
                        bytesSent = bytesSent + bytes_read
                        print("Bytes sent:" + str(bytesSent))
                        uploadJob.next_chunk()
                        percentage = float(chunknumber*100/totalchunks)
                        percentage_float = float (float(chunknumber) / float(totalchunks))
                        
                        #Progress %age call.
                        
                        break
                    else:
                        print("Something went wrong in sending the chunk.")

                        retries = retries + 1
                except urllib2.HTTPError, e:
                    print (e.code)
                    if (e.code == 500):
                        print("!!INTERNAL SERVER ERROR 500!!")
                    else:
                        print("!!URL HTTP Lib ERROR : " + str(e))
            
                    retries = retries + 1
                    time.sleep(1)
    
        #except:  
	else:
            print("Something went wrong in chunk processing.")
            retries = retries + 1;
            time.sleep(1)
#except:
else:
    print("Something terrible has happened in the process overall..")
    file_in.close()

file_in.close()

print("All done. File closed safely")
status_code = response.status_code
print(status_code)

if status_code == 200:
    print("All done. Please verify")
    
elif (status_code == 500):
    print("Server error")

else:
    print("Unknown error")

