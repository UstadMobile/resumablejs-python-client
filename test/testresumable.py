import unittest
import os
from resumablejs_client_encapsulated import ResumableClient
import urllib2
import sys

import urllib2
from io import BytesIO
import hashlib
import time


serverport=os.environ['RESUMABLEJSSERVERPORT']
clientport = int(serverport) + 1
#filepath = "file.txt"
currentdir = os.path.dirname(os.path.abspath(__file__))
filepath = os.getenv('RESUMABLEJSFILEPATH', currentdir + "../chrome.deb")
controlUrl = "http://127.0.0.1:"+serverport
chunkSize = 1048576 #1MB
chunkRetries = 10
resumableUrl = "http://127.0.0.1:" + str(int(serverport) + 1) + "/upload"
#resumableUrl = "http://54.77.18.106:8005/upload/"

print(filepath)
clientmd5 = hashlib.md5(open(filepath).read()).hexdigest()
print(controlUrl)
print(chunkSize)
print(chunkRetries)
print(resumableUrl)


class TestResumableClient(unittest.TestCase):
    def setUp(self):
    	#resumable = ResumableClient("file.txt", "http://54.77.18.106:8005/upload/", 1048576, 10)
    	pass
        

    def testOnePlusOne(self):
        two=2
        opo=1+1
        self.assertEqual(two, opo, "Success!")
    
    
    def testResumableClientStart(self):
    	resumable = ResumableClient(filepath, resumableUrl, chunkSize, chunkRetries)
    	urllib2.urlopen(controlUrl + "/resumable/start").read()
        urllib2.urlopen(controlUrl + "/resumable/slowdownoff").read()
    	response = resumable.startUpload()
        status_code = response.status_code
    	self.assertEqual(status_code, 200, "Normal Start success")
    	retry = resumable.retry
        serverfilepath = response.headers['serverfilepath']
        time.sleep(5)
        servermd5 = hashlib.md5(open(serverfilepath).read()).hexdigest()
    	self.assertEqual(retry, 0, "Success witout any retries")
        self.assertEqual(clientmd5, servermd5, "Client and Server md5 matches!")



    def testResumableClientStop(self):
    	resumable = ResumableClient(filepath, resumableUrl, chunkSize, chunkRetries)
    	urllib2.urlopen(controlUrl+"/resumable/stop").read()
        urllib2.urlopen(controlUrl + "/resumable/slowdownoff").read()
    	response = resumable.startUpload();
        try:
            status_code = response.status_code
        except:
            status_code = response
    	self.assertEqual(status_code, 1, "Normal Stop Fail test Success: " + str(status_code))

    def testResumableClientSlowDownOn(self):
    	resumable = ResumableClient(filepath, resumableUrl, chunkSize, chunkRetries)
        urllib2.urlopen(controlUrl + "/resumable/start").read()
    	urllib2.urlopen(controlUrl + "/resumable/slowdownon").read()
    	response = resumable.startUpload();
        status_code = response.status_code
    	retry = resumable.retry
        serverfilepath = response.headers['serverfilepath']
        time.sleep(5)
        servermd5 = hashlib.md5(open(serverfilepath).read()).hexdigest()
    	self.assertEqual(status_code, 200, "Normal Slow Down On test Success: " + str(status_code))
        self.assertEqual(clientmd5, servermd5, "Client and Server md5 matches!")

    @unittest.expectedFailure
    def testResumableClientSlowDownOnFail(self):
    	resumable = ResumableClient(filepath, resumableUrl, chunkSize, chunkRetries)
        urllib2.urlopen(controlUrl + "/resumable/start").read()
        urllib2.urlopen(controlUrl + "/resumable/slowdownoff").read()
    	urllib2.urlopen(controlUrl + "/resumable/slowdownon").read()
    	response = resumable.startUpload();
        status_code = response.status_code
    	retry = resumable.retry
    	self.assertEqual(status_code, 200, "Normal Slow Down On test Success: " + str(status_code))
    	self.assertEqual(retry, 0, "Success with slow down success without any retries (supposed to fail")


    def testResumableClientSlowDownOff(self):
    	resumable = ResumableClient(filepath, resumableUrl, chunkSize, chunkRetries)
        urllib2.urlopen(controlUrl + "/resumable/start").read()
    	urllib2.urlopen(controlUrl + "/resumable/slowdownoff").read()
    	response = resumable.startUpload();
        status_code = response.status_code
    	retry = resumable.retry
        serverfilepath = response.headers['serverfilepath']
        time.sleep(5)
        servermd5 = hashlib.md5(open(serverfilepath).read()).hexdigest()
    	self.assertEqual(status_code, 200, "Normal Slow Down Off test Success: " + str(status_code))
    	self.assertEqual(retry, 0, "Success witout any retries")
        self.assertEqual(clientmd5, servermd5, "Client and Server md5 matches!")
    


if __name__ == '__main__':
    unittest.main()
