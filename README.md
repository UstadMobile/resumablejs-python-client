Welcome to resumablejs python client implementation.

This project consists of two python files:


1. resumablejs-client.py

This is a generic tester that contains the basic logic and implementation for Resumablejs client.

You should have a resumablejs server up and running and its end point set up. This server can be a django python web application or anything else as per resumable.js 

This file is the Client. We could not find any python based implementation so we created one. 
If you want to see how we did it, this is the file you need to be looking and testing. 

To run and test this, simply run the python script at:

resumablejs-client.py "your file path" "your resumablejs server upload endpoint"  Each chunk size (in bytes)   max number of retries (times seconds) 

eg:
resumablejs-client.py /my/awesome/file/to/upload.txt http://www.resumableserver.com/upload/ 1048576 10

This means the file upload.txt will be uploaded to an already set up resumbalejs server's endpoint with chunks of 1 MB (1048576 bytes) and it will retry 10 times (with a delay of 1 second every retry)


2. resumablejs-client-umcloud.py 

This is for UMCLoud (Ustad Mobile Cloud Portal) implementation and testing purposes.
To test this against UMCloud run this as:

Currently we are using this to test eXe's block uploads (With the right endpoint, we have added username, password checks, checks to see if the epub/elp is valid, force New parameter and not Assign parameter as per eXe's milestones and features. This is probably not something applicable if you are just looking at knowing how the logic works. For that look at point 1. which is a generic resumablejs python client.

resumablejs-client-umcloud.py "file path" "resumablejs server endpoint"  chunk size in bytes    max number of retries per chunk  "username of umcloud" "password of umcloud" "forceNew" "noAutoassign"

ToDo:
1. Set this up with unit testing.
2. Use UploadJob class for every uploads.
3. Use variable chunk size based on network speed. 

