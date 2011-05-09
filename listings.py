##
# This is the web service for the listings.dev.payswarm.com website.
# License: LGPLv3
#
# @author Manu Sporny
import os, os.path, sqlite3, sys, urllib
from mod_python import apache

##
# Checks to see if the given URL is valid.
#
# @param req the HTTP request object.
# @param url the URL to check.
#
# @return True if the URL is acceptable for this application, false otherwise
def validurl(req, url):
    rval = False
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
        rval = True

    return rval

##
# Creates a listings database given a filename.
#
# @param req the HTTP request object.
# @param dbfile the name of the database file to create.
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
    except sqlite3.OperationalError:
        req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        req.content_type = 'text/plain'
        req.write("Error: Failed to create listings.db database file. "
            "Make sure the web server has write permission to the root "
            "website directory.")

##
# Opens a connection to the database
#
# @param req the HTTP request object.
#
# @return a cursor to the listings database.
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
# @param conn an active connection to the database.
#
# @return a JSON-LD document if it exists or None if it doesn't exist.
def dbwrite(req, conn):
    rval = False
    url = req.parsed_uri[-3]

    # retrieve the POST data
    data = req.read(65536)
    if(len(data) < 65536):
        # insert or update the listing in the database at the given URL
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO listings VALUES (?,?)",
            (url, data))

        # commit the data and close the connection to the database
        conn.commit()
        c.close()

        rval = True
    else:
        req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        req.content_type = 'text/plain'
        req.write("Error: POST data size must be less than 65536 bytes.\n")

    return rval

##
# Retrieves a value from the database.
#
# @param req the Web request that came into the web server.
# @param conn an active connection to the database.
#
# @return a JSON-LD document if it exists or None if it doesn't exist.
def dbget(req, conn):
    rval = None
    url = req.parsed_uri[-3]

    # retrieve the data for the URL, if it exists
    c = conn.cursor()
    c.execute("SELECT listing FROM listings WHERE url=?",
        (url,))
    for l in c:
        rval = l[0]
    c.close()

    return rval

##
# Deletes a given URL contained in the request from the database.
#
# @param req the Web request that came into the web server.
# @param conn an active connection to the database.
def dbdelete(req, conn):
    rval = None
    url = req.parsed_uri[-3]

    # delete the data for the URL, if it exists
    c = conn.cursor()
    c.execute("DELETE FROM listings WHERE url=?",
        (url,))
    conn.commit()
    c.close()

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

    # check to make sure the URL is valid, return immediately if it isn't
    if(not validurl(req, service)):
        return req.status

    # get a handle to the database
    conn = dbopen(req)
    
    # perform the basic REST CRUD operations
    if(method == "POST" or method == "PUT"):
        # attempt to write data on POST or PUT
        if(dbwrite(req, conn)):
            status = apache.OK
        else:
            req.status = apache.HTTP_INTERNAL_SERVER_ERROR
            req.content_type = 'text/plain'
            req.write("Error: Failed to POST to provided URL: %s\n" % service)
    elif(method == "GET"):
        # retrieve data on GET
        listing = dbget(req, conn)
        if(listing == None):
            req.status = apache.HTTP_NOT_FOUND
            req.content_type = 'text/plain'
            req.write("Error: The listing was not found: %s\n" % service)
        else:
            req.content_type = 'application/json'
            req.write(listing)
    elif(method == "DELETE"):
        dbdelete(req, conn)

    # close the connection to the database
    conn.close()

    return status

