import os
import argparse

usage_text = 'python wpscanloop.py'
example_text = '''Example:
python wpscanloop.py'''
parser = argparse.ArgumentParser(usage=usage_text, epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)

#Arguments
parser.add_argument("-f", "--file", help="Specify input file.\n", nargs='+')
parser.add_argument("-o", "--output", help="Specify output filename. \n", nargs="+")

args = parser.parse_args()

if not args.file:
	HTTPFileName = "/root/Documents/data/http_hosts.txt"
else:
	HTTPFileName = args.file[0]
if args.output:
	if '.txt' in args.output[0]:
		outputFilename = str(args.output[0])
	else:
		outputFilename = str(args.output[0])+'.txt'
else:
	outputFilename = "/root/Documents/output/http/wpscanoutput.txt"

URLs=[]

with open(HTTPFileName, 'r') as f:
	lines = f.readlines()
	for line in lines:
		URLs.append(line)

for URL in URLs:
	URL = URL.split("\n")
	os.system("wpscan --url "+URL[0]+" -e 2>&1 | tee -a "+outputFilename)