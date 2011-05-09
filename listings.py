##
# This is the web service for the listings.dev.payswarm.com website.
# License: LGPLv3
#
# @author Manu Sporny
import os, os.path, sqlite3, sys, urllib
from mod_python import apache

##
# Creates a listings database given a filename
def dbcreate(req, dbfile):
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
        c = conn.cursor()

        # Create the listings table
        c.execute('''CREATE TABLE listings
        (url TEXT PRIMARY KEY, listing TEXT)''')
        
        # Commit the creation and close the database
        conn.commit()
        c.close()
        conn.close()
    except sqlite3.OperationalError:
        req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        req.content_type = 'text/plain'
        req.write("Error: Failed to create listings.db database file. "
            "Make sure the web server has write permission to the root "
            "website directory.")

##
# Opens a connection to the database
#
# @return a cursor to the listings database
def dbopen(req):
    cwd = os.path.dirname(__file__)
    dbfile = os.path.join(cwd, "listings.db")
    
    # Create the database if it doesn't exist
    if(not os.path.exists(dbfile)):
        dbcreate(req, dbfile)
    
    # Open a connection to the database
    conn = sqlite3.connect(dbfile)

    return conn

##
# Writes a posted document to the database.
#
# @param req the Web request that came into the web server.
#
# @return a JSON-LD document if it exists or None if it doesn't exist.
def dbwrite(req, conn):
    rval = False
    url = req.parsed_uri[-3]
    safeurl = urllib.quote(url)

    if(url != safeurl):
        # if a percent-encoded character was detected, kick out an error
        req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        req.content_type = 'text/plain'
        req.write("Error: URL characters that require "
            "percent encoding per RFC3986 are not allowed.\n"
            "   Provided URL: %s\n" % url +
            "   Encoded URL : %s\n" % safeurl)
    else:
        # retrieve the POST data
        data = req.read(65536)
        if(len(data) < 65536):
            # insert or update the listing in the database at the given URL
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO listings VALUES (?,?)",
                (safeurl, data))

            # commit the data and close the connection to the database
            conn.commit()
            c.close()
            conn.close()

            rval = True
        else:
            req.status = apache.HTTP_INTERNAL_SERVER_ERROR
            req.content_type = 'text/plain'
            req.write("Error: POST data size must be less than 65536 bytes.\n")

    return rval

##
# Retrieves a value from the database
#
# @param url the URL of the JSON-LD listing to retrieve.
#
# @return a JSON-LD document if it exists or None if it doesn't exist.
def dbget(req):
    return None

##
# The handler function is what is called whenever an apache call is made.
#
# @param req the HTTP request.
#
# @return apache.OK if there wasn't an error, the appropriate error code if
#         there was a failure.
def handler(req):
    # file that runs an apache test.
    status = apache.OK
    method = req.method
    puri = req.parsed_uri
    service = puri[-3]
    argstr = puri[-2]
    args = {}

    # get a handle to the database
    conn = dbopen(req)
    
    # perform the basic REST CRUD operations
    if(method == "POST"):
        if(dbwrite(req, conn)):
            status = apache.OK
        else:
            req.status = apache.HTTP_INTERNAL_SERVER_ERROR
            req.content_type = 'text/plain'
            req.write("Error: Failed to POST to provided URL: %s\n" % service)
    elif(method == "GET"):
        # FIXME: Implement GET
        listing = dbget(req, conn)
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

