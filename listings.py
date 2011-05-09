##
# This is the web service for the listings.dev.payswarm.com website.
# License: LGPLv3
#
# @author Manu Sporny
import os, os.path, sys
from mod_python import apache

##
# The handler function is what is called whenever an apache call is made.
#
# @param req the HTTP request.
#
# @return apache.OK if there wasn't an error, the appropriate error code if
#         there was a failure.
def handler(req):
    # File that runs an apache test.
    status = apache.OK
  
    puri = req.parsed_uri
    service = puri[-3]
    argstr = puri[-2]
    args = {}

    # Retrieve all of the unit tests from the W3C website
    if(service == "/" or service == "index.html" or service == "index.xhtml"):
        req.content_type = 'text/html'
        ifile = open("index.html", "r")
        req.write(ifile.read())
        ifile.close()
    else:
        req.content_type = 'text/html'
        req.write("<strong>ERROR: Unknown Live Loop service: %s</strong>" % \
            (service,))

    return status

