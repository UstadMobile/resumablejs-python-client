
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

    #TODO: Move init up; all thesae need to be in init
    chunkNumber = 0
    filePath = ""
    url = ""
    chunkSize = 0
    maxRetries = 0
    mimeType = ""
    fileName = ""
    totalChunks = 0
    totalSize = 0
    identifier = ""
    #TODO: fix spelling
    realtivePath= ""
    retry=0



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
        #TODO: Use os.path.getsize
        try:
            print("Opening file: " + str(filepath))
            file_in = open(filepath, "rb")
            total_bytes = len(file_in.read())
            file_in.seek(0)
            print("Total File size : " + str(total_bytes))
            file_in.close()
            return total_bytes
        except:
            return 0
            try:
                file_in.close()
            except:
                print("Unable to close file.");

    def __init__(self, filepath, url, chunksize, maxretries):
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


    def startUpload(self):
        file_in = open(self.filePath, "rb")

        retries = 0
        bytesSent = 0
        bytes_read = 0
        self.chunkNumber = 0

        try:
            
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
                                }
                        params = {'file':('file', decode)}

                        """
                        #Using MultipartPostHandler
                        cookies = cookielib.CookieJar()
                        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies), 
                                      MultipartPostHandler.MultipartPostHandler)
                        mpparams = { 'resumableChunkNumber':self.chunkNumber,
                                    'resumableType':self.mimeType,
                                    'resumableChunkSize':self.chunkSize,
                                    'resumableIdentifier':str(self.totalSize)+"-"+self.fileName,
                                    'resumableTotalSize':self.totalSize,
                                    'resumableRelativePath':str(self.totalSize)+"-"+self.fileName,
                                    'resumableCurrentChunkSize':bytes_read,
                                    'resumableFilename':self.fileName,
                                    'resumableTotalChunks':self.totalChunks, 
                                    'file': decode,
                                    }
                        """
               
                        try:  
                            """
                            #Using urllib2 and MultipartPostHandler
                            response = opener.open(self.url, str(mpparams))
                            status_code = response.code
                            """
                            print("Making request..")
                            print(data)
                            response = requests.post(self.url, files=params, data=data, timeout=10)
                            status_code = response.status_code
                            print(response)
                            
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
                            print (e.code)
                            if (e.code == 500):
                                print("!!INTERNAL SERVER ERROR 500!!")
                            else:
                                print("!!URL HTTP Lib ERROR : " + str(e))
                    
                            retries = retries + 1
                            self.retry = self.retry + 1
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
        if status_code:
            status_code = response.status_code
        else:
            status_code = 1
        print(status_code)

        if status_code == 200:
            print("All done. Please verify")
            
        elif (status_code == 500):
            print("Server error")

        else:
            print("Failed to determine process sucess. Chunks may have not been sent.")

        if status_code != 1:
            return response
        else:
            return 1


