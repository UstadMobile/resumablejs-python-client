#!/bin/bash
#Start the servers

if [ $# -eq 0 ]; then
    echo "No arguments provided"
    echo "Usage: .sh <serverfile> <port> <test file path> <Optional: file to test>"
    echo "Ex:    .sh node-qunit-server-2.js 1234 /home/varuna/UstadMobile/resumablejs-python-client/testresumable.py chrome.deb"
    exit 1
fi

if [ $# -lt 3 ] && [ $# -gt 4 ]; then
    echo "You need to give at least 3 arguments"
    echo "Usage: .sh <serverfile> <port> <test file path> <Optional: file to test>"
    echo "Ex:    .sh node-qunit-server-2.js 1234 /home/varuna/UstadMobile/resumablejs-python-client/testresumable.py chrome.deb"    
    exit 1
fi

serverfile=${1}
serverfile=`readlink -f ${1}`
serverport=${2}
testfile=${3}
testfile=`readlink -f ${3}`
echo "Starting.."
uploadfile=`readlink -f ${4}`
clientport=`expr $serverport + 1`

export RESUMABLEJSSERVERPORT=${2}
export PYTHONPATH=../src

if [ -z "${uploadfile}" ]
 then
    echo "UPLOAD FILE not specified. Defaulting."
 else
    echo "UPLOAD FILE specified!"
    export RESUMABLEJSFILEPATH=`readlink -f ${4}`
fi

echo ${serverport}
echo ${serverfile}
echo ${clientport}

#Run the server
node $1 $2 &

SERVERPID=$! #Gets process ID
echo "Process id: "
echo ${SERVERPID}
sleep 5

#export RESUMABLEJSSERVERPORT=${2}

#Run python tests
resumablefolder=`dirname ${3}`
resumableclient="${resumablefolder}/resumablejs_client_encapsulated.py"
coverage -x ${testfile}
coverage report ${resumableclient}
#When all done and good . End of testing, etc
kill $SERVERPID
