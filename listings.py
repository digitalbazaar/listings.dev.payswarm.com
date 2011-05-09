##
# This is the web service for the listings.dev.payswarm.com website.
# License: LGPLv3
#
# @author Manu Sporny
import os, os.path, sqlite3, sys
from mod_python import apache

##
# Creates a listings database given a filename
def dbcreate(dbfile):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    # Create the listings table
    c.execute('''CREATE TABLE listings
    (url TEXT PRIMARY KEY, listing TEXT)''')
    
    # Commit the creation and close the database
    conn.commit()
    c.close()
    conn.close()

##
# Opens a connection to the database
#
# @return a cursor to the listings database
def dbopen():
    cwd = os.path.dirname(__file__)
    dbfile = os.path.join(cwd, "listings.db")
    
    # Create the database if it doesn't exist
    if(not os.path.exists(dbfile)):
        dbcreate(dbfile)
    
    # Open a connection to the database
    conn = sqlite3.connect(dbfile)

    return conn

##
# Retrieves a value from the database
#
# @param url the URL of the JSON-LD listing to retrieve.
#
# @return a JSON-LD document if it exists or None if it doesn't exist.
def dbget(url):
    return None

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
    method = req.method
    puri = req.parsed_uri
    service = puri[-3]
    argstr = puri[-2]
    args = {}

    # Get a handle to the database
    conn = dbopen()
    
    # Perform the basic REST CRUD operations
    if(method == "POST"):
        # FIXME: Implement POST
        # Create the post
        req.status = apache.HTTP_FORBIDDEN
        req.write("Error: Creating the listing is forbidden: %s\n" % service)
    elif(method == "GET"):
        # FIXME: Implement GET
        listing = dbget(service)
        if(listing == None):
            req.status = apache.HTTP_NOT_FOUND
            req.content_type = 'text/plain'
            req.write("Error: The listing was not found: %s\n" % service)
        else:
            req.content_type = 'application/json'
            req.write(listing)
    elif(method == "DELETE"):
        # FIXME: Implement delete
        req.status = apache.HTTP_FORBIDDEN
        req.write("Error: Deleting the listing is forbidden: %s\n" % service)

    return status

