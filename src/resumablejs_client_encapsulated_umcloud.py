
import sys
import cookielib
import requests
import urllib2
from io import BytesIO
from mimetypes import MimeTypes
import urllib
import os
import time

class ResumableClient(object):

    def __init__(self, filepath, url, chunksize, maxretries, forceNew, noAutoassign, username, password):
        file_in = open(filepath, "rb")
        
        self.filePath = filepath
        self.url = url
        self.chunkSize = int(chunksize)
        self.maxRetries = int(maxretries)

        self.mimeType = self.get_mime_type(filepath)

        basename=os.path.basename(filepath)
        self.fileName = basename

        self.chunkNumber = 0

        total_bytes = int(self.get_total_size(filepath))
        self.totalChunks = int(total_bytes) / int(chunksize) + 1
        self.totalSize = int(total_bytes)

        self.identifier = str(total_bytes)+"-"+basename
        self.realtivePath = str(total_bytes)+"-"+basename
        self.retry = 0
        
        self.forceNew = forceNew
        self.noAutoassign = noAutoassign

        self.username = username
        self.password = password


    def next_chunk(self):
        self.chunkNumber = self.chunkNumber + 1;

    def get_mime_type(self, filepath):
        print("Getting mime type..")
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

        return mime_type
    
    def get_total_size(self, filepath):
        try:
            total_bytes = int(os.path.getsize(filepath))
            """
            print("Opening file: " + str(filepath))
            file_in = open(filepath, "rb")
            total_bytes = len(file_in.read())
            file_in.seek(0)
            print("Total File size : " + str(total_bytes))
            file_in.close()
            """
            return total_bytes
        except:
            return 0


    def startUpload(self):
        file_in = open(self.filePath, "rb")

        retries = 0
        bytesSent = 0
        bytes_read = 0
        self.chunkNumber = 0

       
            
        status_code = 0
        while (self.chunkNumber <= self.totalChunks and retries < self.maxRetries 
            and bytesSent < self.totalSize):
            try: 
                #self.chunknumber = self.chunknumber + 1
                self.next_chunk()
                print("Attempting to process chunk " + str(self.chunkNumber) + "/" + 
                    str(self.totalChunks) + "...")
                chunk = bytearray(self.chunkSize)
                bytes_read = file_in.readinto(chunk)
                chunk = chunk[:bytes_read]
                if chunk != None:
                    retries = 0
                print("Trying to send this chunk of length: " + str((bytes_read)))
                
                retries =0
                while(retries < self.maxRetries):
                    print("Retry: " + str(retries))
                    if (retries > 0):
                        print(".. retrying " + str(retries + 1) + "/" + 
                            str(self.maxRetries) + "..")

                    decode = str(chunk)
                    params = {'file': decode}
                    data = {
                            'resumableChunkNumber':self.chunkNumber,
                            'resumableType':self.mimeType,
                            'resumableChunkSize':self.chunkSize,
                            'resumableIdentifier':str(self.totalSize)+"_"+self.fileName,
                            'resumableTotalSize':self.totalSize,
                            'resumableRelativePath':str(self.totalSize)+"-"+self.fileName,
                            'resumableCurrentChunkSize':bytes_read,
                            'resumableFilename':self.fileName,
                            'resumableTotalChunks':self.totalChunks,
                            'forceNew':self.forceNew,
                            'noAutoassign':self.noAutoassign,
                            }
                    params = {'file':('file', decode)}

                    try:  
                        response = requests.post(self.url, files=params, data=data, auth=(self.username, self.password))
                        status_code = response.status_code
                        
                        print("Response code: " + str(status_code))
                        if status_code == 200:
                            bytesSent = bytesSent + bytes_read
                            print("Bytes sent:" + str(bytesSent))
                            #uploadJob.next_chunk()
                            percentage = float(self.chunkNumber*100/self.totalChunks)
                            percentage_float = float (float(self.chunkNumber) / float(self.totalChunks))
                            
                            #Progress %age call.
                            
                            break
                        else:
                            print("Something went wrong in sending the chunk.")
                            print(data)

                            retries = retries + 1
                            self.retry = self.retry + 1
                    except Exception, e:
                        print("!EXCEPTION! : ")
                        print(e)
                        retries = retries + 1
                        self.retry = self.retry + 1

                    except urllib2.HTTPError, e:                    
                        retries = retries + 1
                        self.retry = self.retry + 1
                        time.sleep(1)
        
            except:  
                retries = retries + 1;
                time.sleep(1)

        file_in.close()

        print("All done. File closed safely")
        if status_code:
            status_code = response.status_code
        else:
            status_code = 1

        if status_code != 1:
            return response
        else:
            return 1


