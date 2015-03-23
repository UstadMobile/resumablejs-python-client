
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
    username = sys.argv[1:][4]
    password = sys.argv[1:][5]
    try:
        if (sys.argv[1:][6] == None):
	    forceNew = False
	    print("Force New is False")
        else:
	    forceNew = sys.argv[1:][6]

        if (sys.argv[1:][7] == None):
	    noAutoassign = False
	    print("no Auto assign is False")
        else:
	    noAutoassign = sys.argv[1:][7]
    except:
	forceNew = False
	noAutoassign = False
	print("ForceNew is False by default")
	print("noAutoassign is False by default")
    print("forceNew and noAutoassign is : ")
    print(forceNew)
    print(noAutoassign)
    
    try:
        file_in = open(sys.argv[1:][0], "rb")
	
    except:
	print("!ERROR in file given!")
	print("Unable to open file. Does the file exist?")
except:
    print("!ERROR in usage!")
    print("Run as: <script> <File (whole path)> <upload url> <chunk size> <chunk retries number> <username of server> <password of server> <force New> <noAssign>")
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

try:
    
    status_code = 0
    while (chunknumber <= totalchunks and retries < default.maxRetries and bytesSent < total_bytes):
        try: 
            
            if (status_code == 403):
                break
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
                        'username':username,
                        'password':password,
                        'forceNew':forceNew,
                        'noAutoassign':noAutoassign
                        }
                params = {'file':('file', decode)}
       
                try:    
    
                    response = requests.post(default.url, files=params, data=data)
                    print("Response code: " + str(response.status_code))
                    status_code = response.status_code
                    if (status_code == 403):
                        print("Error: Wrong username and password combination. Try again")
                        break
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
                        try:
                            print("The error was:" )
                            print(response.headers['error'])
                        except:
                            print("Unknwon server error")

                        retries = retries + 1
                except urllib2.HTTPError, e:
                    print (e.code)
                    if (e.code == 500):
                        print("!!INTERNAL SERVER ERROR 500!!")
                    else:
                        print("!!URL HTTP Lib ERROR : " + str(e))
            
                    retries = retries + 1
                    time.sleep(1)
    
        except:  
            print("Something went wrong in chunk processing.")
            retries = retries + 1;
            time.sleep(1)
except:
    print("Something terrible has happened in the process overall..")
    file_in.close()

file_in.close()

print("All done. File closed safely")
status_code = response.status_code
print(status_code)

if status_code == 200:
    courseid = response.headers['courseid']
    coursename = response.headers['coursename']

    print(courseid)
    print(coursename)
              
    
    try:
        print("Your course: " + coursename + " has uploaded. Course id: " + courseid )
    except:
        print("Your course has uploaded/updated.")        
    
elif (status_code == 500):
    error = response.headers['error']
    if (error == "Grunt test failed"):
        print("Server Error: Your course did not pass server tests. Your project uploaded but cannot be set as active")
    elif (error == "Exe export failed"):
        print("Server Error: Your course failed to finish exporting on the server. Your project uploaded but cannot be set as active.")
    elif (error == "Exe export failed to start"):
        print("Server Error: Your course failed to export on the server. Please get in touch.")
    elif (error == "Request is not POST"):
        print("eXe error: eXe failed to connect with the server by POST request")
    else:
        print("Error: Cannot connect to the server. Make sure the server is active and you have network access.")
elif (status_code == 403):
    print("Error: Wrong username and password combination. Try again")

