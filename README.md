Welcome to resumablejs python client implementation.

resumablejsclient.py

This is a generic Library that contains the basic logic and implementation for Resumablejs client.
You should have a resumablejs server up and running and its end point set up. This server can be a django python web application, nodejs or anything else as per resumable.js 

The library is at src/resumablejsclient.py 
Include that library in your python application / file and import ResumableClient.
from resumablejsclient import ResumableClient

Then in your code, initialise the library as: 

resumable = ResumableClient('/file/to/upload.zip', 'http://server/upload/location') 

The usage is:

	    file_path: Path to local file to upload
            chunk_size: Chunk size to use with http upload (default 1MB)
            max_retries: Maximum number of retries (default: 20 times , over a second interval)
            request_extra_params: Dictionary of HTTP paramaters to add to each request (default: empty dictionary)
            http_auth: HTTP Basic auth parameters as a tuple of (username, password) (default: None)

The request_extra_params can be anything else that your resumablejs server wants, the http_auth will take in a tuple to do BASIC Authentication credentials. 
This means the file will be uploaded to an already set up resumbalejs server's endpoint with chunks of 1 MB (1048576 bytes) and it will retry 20 times (with a delay of 1 second every retry)
you can change the chunk size and max number of retries by initialising as:

resumable = ResumableClient('/file/to/upload.zip', 'http://server/upload/location', 524288, 10) 
Thats 500 KB chunks of 10 max retries.

To actually start the upload, just call:

resumable.start_upload();

This returns the response of the whole process or 1 for failure. 

ToDo:
3. Use variable chunk size based on network speed. 

