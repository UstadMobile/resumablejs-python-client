
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

    def __init__(self, file_path, url, chunk_size=1048576, max_retries=20, request_extra_params = {}, http_auth = None):
        """Setup a new resumable upload request
        Args:
            file_path: Path to local file to upload
            chunk_size: Chunk size to use with http upload
            maxretries: Maximum number of retries
            request_extra_params: Dictionary of HTTP paramaters to add to each request (default: empty dictionary)
            http_auth: HTTP Basic auth parameters as a tuple of (username, password) (default: None)

        """
        file_in = open(file_path, "rb")
        
        self.file_path = file_path
        self.url = url
        self.chunk_size = int(chunk_size)
        self.max_retries = int(max_retries)

        self.mime_type = self.get_mime_type(file_path)

        basename=os.path.basename(file_path)
        self.file_name = basename

        self.chunk_number = 0

        total_bytes = int(self.get_total_size(file_path))
        self.total_chunks = int(total_bytes) / int(chunk_size) + 1
        self.total_size = int(total_bytes)

        self.identifier = str(total_bytes)+"-"+basename
        self.realtive_path = str(total_bytes)+"-"+basename
        self.retry = 0
        
        self.request_extra_params = request_extra_params
 
        self.http_auth = http_auth


    def next_chunk(self):
        self.chunk_number = self.chunk_number + 1;

    def get_mime_type(self, file_path):
        #Get mime type
        try:
            mime = MimeTypes()
            murl = urllib.pathname2url(file_path)
            mime_type = mime.guess_type(murl)[0]
            if mime_type == None:
                mime_type = 'text/plain'
        except:
            mime_type = 'text/plain'

        return mime_type
    
    def get_total_size(self, file_path):
        total_bytes = int(os.path.getsize(file_path))
        return total_bytes


    def start_upload(self):
        file_in = open(self.file_path, "rb")
        retries = 0
        bytes_sent = 0
        bytes_read = 0
        self.chunk_number = 0
        status_code = 0
        while (self.chunk_number <= self.total_chunks and retries < self.max_retries  
            and bytes_sent < self.total_size):
            try: 
                self.next_chunk()
                chunk = bytearray(self.chunk_size)
                bytes_read = file_in.readinto(chunk)
                chunk = chunk[:bytes_read]
                if chunk != None:
                    retries = 0
                retries =0
                while(retries < self.max_retries):
                    decode = str(chunk)
                    params = {'file': decode}
                    data = {
                            'resumableChunkNumber':self.chunk_number,
                            'resumableType':self.mime_type,
                            'resumableChunkSize':self.chunk_size,
                            'resumableIdentifier':str(self.total_size)+"_"+self.file_name,
                            'resumableTotalSize':self.total_size,
                            'resumableRelativePath':str(self.total_size)+"-"+self.file_name,
                            'resumableCurrentChunkSize':bytes_read,
                            'resumableFilename':self.file_name,
                            'resumableTotalChunks':self.total_chunks,
                            }
                    for extra_param_name in self.request_extra_params:
                        data[extra_param_name] = self.request_extra_params[extra_param_name]

                    params = {'file':('file', decode)}

                    try:  
                        response = requests.post(self.url, files=params, data=data, auth=self.http_auth)
                        status_code = response.status_code
                        
                        if status_code == 200:
                            bytes_sent = bytes_sent + bytes_read
                            percentage = float(self.chunk_number*100/self.total_chunks)
                            percentage_float = float (float(self.chunk_number) / float(self.total_chunks))
                            #Progress %age call.
                            break
                        else:
                            retries = retries + 1
                            self.retry = self.retry + 1
                    except Exception, e:
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

        if status_code:
            status_code = response.status_code
        else:
            status_code = 1

        if status_code != 1:
            return response
        else:
            return 1


