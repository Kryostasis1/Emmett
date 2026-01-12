from lib import assets
import argparse
import re
import requests
from termcolor import colored

#Format
class Format:
	end = '\033[0m'
	underline = '\033[4m'

#Header
usage_text = 'python shc.py'
example_text = '''Example:
python shc.py'''
parser = argparse.ArgumentParser(usage=usage_text, epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)

#Arguments
parser.add_argument("-u", "--url", help="Specify URL to be scanned.\n", nargs='+', required=True)

args = parser.parse_args()

print(assets.logo)

def URLMatch(URL):
        if re.match("^((http:\/\/)|(https:\/\/))[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,20}(:[0-9]{1,5})?(\/.*)?$", URL):
            return True
        if re.match("((http:\/\/)|(https:\/\/))([0-9]{1,3}).([0-9]{1,3}).([0-9]{1,3}).([0-9]{1,3})", URL):
            return True
        return False

#URL Request
url = ''.join(args.url)
URLCheck = URLMatch(url)
if URLCheck == False:
	print("Submitted site is not a complete URL. Please ensure you are using http:// or https://.")
	exit()
else:
	try:
		response = requests.head(url)
	except requests.exceptions.Timeout:
	# Maybe set up for a retry, or continue in a retry loop
		print("URL attempt timeout, check the web application is reachable.")
		exit()
	except requests.exceptions.TooManyRedirects:
	# Tell the user their URL was bad and try a different one
		print("Max redirect reached, check URL is correct.")
		exit()
	except requests.exceptions.RequestException as e:
	# catastrophic error. bail.
		print("Error submitting URL.")
		exit()

#Response Code
print(Format.underline+"URL Details"+Format.end)
print("Testing URL: "+url)
if 200 <= response.status_code <= 226:
	print("Response Code: {}\n".format(colored(response.status_code, "green")))
if 300 <= response.status_code <= 308:
	print("Response Code: {}\n".format(colored(response.status_code, "yellow"))) 
if 400 <= response.status_code <= 451:
	print("Response Code: {}\n".format(colored(response.status_code, "red")))
	error_code = str(response.status_code)
	warning = "WARNING: The inputted URL replied with error code "+error_code+" the below results may not be correct.\n"
	print("{}".format(colored(warning, "red")))

#Response Header Checks
print(Format.underline+"Response Headers"+Format.end)
weak_headers = ["server", "X-Powered-By", "X-AspNet-Version", "X-AspNetMvc-Version"]
if any([x in response.headers for x in weak_headers]):
	if "server" in response.headers:
		print("Server header was found enabled and advertising: {}".format(colored(response.headers["server"], "red")))
	if "X-Powered-By" in response.headers:
		print("X-Powered-By header was found enabled and advertising: {}".format(colored(response.headers["X-Powered-By"], "red")))
	if "X-AspNet-Version" in response.headers:
		print("X-AspNet-Version header was found enabled and advertising: ".format(colored(response.headers["X-AspNet-Version"], "red")))	
	if "X-AspNetMvc-Version" in response.headers:
		print("X-AspNetMvc-Version header was found enabled and advertising: ".format(colored(response.headers["X-AspNetMvc-Version"], "red")))
else:
	print("No weak response headers discovered.")