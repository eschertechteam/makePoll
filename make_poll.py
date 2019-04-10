import json
import os
import shutil
import click
import jinja2
import uuid
import gspread
import smtplib
import ssl
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from email.mime.text import MIMEText

scope = ['https://spreadsheets.google.com/feeds',
		 'https://www.googleapis.com/auth/drive']

# CRED should be file path to the json file of the service account
# made by going to Google API > Create Credentials > Service Account > JSON
CRED = os.path.join(os.path.dirname(__file__), 'makepoll-9b8df964291c.json')
REPLACE = os.path.join(os.path.dirname(__file__), 'REPLACE')
LASTPOLLID = os.path.join(os.path.dirname(__file__), 'LASTPOLLID')


# response sheet name
FORM_NAME = "Escher_Poll_{}_{}_{}".format('01', '23', '19')

"""
	Set up on the developer console (one time):
	1. Create service account
	2. Enable Google Sheet API
	3. Get credentials for the API with service account
	4. Set CRED variable to the path to the credentials file
	"""

"""
	Set up before running form response parser (every poll):
	1. Go to response tab of the form
	2. Click the green icon (view response in sheets)
	3. Create a Google sheet with name "Escher_Poll_mm_dd_yy" or something like that
	4. Share sheet with service account email (felichri@makepoll-224313.iam.gserviceaccount.com) for now
	TODO: hard code in the sharing?
	"""

# populate format
"""
	{
	"type":
	"out_name":
	"template":
	"context": {
		"title":
		"startDate":
		"endDate":
		"id":
		"admins":
		"title":
		"intro":
		"questions": {"title": , "options": []
	}
	}
	"""
"""
	Build xml file for wiki poll for House Votes.
	"""

class InvalidDateError(Exception):
	pass

# find first empty row N. N - 1 is last row and most recent form entry
# courtesy of Pedro Lobito on StackOverflow
def next_available_row(wks):
	print(wks.col_values(1))
	str_list = list(filter(None, wks.col_values(1)))  # fastest

	# Note that this is 1-indexed
	return str(len(str_list)+1)


# authenticate access to the Google Form responses
def getForm():
	print(CRED)
	credentials = ServiceAccountCredentials.from_json_keyfile_name(CRED, scope)
	print("GETTING FORM")
	gc = gspread.authorize(credentials)
	print("AUTHORIZED")
	# Sample form response sheet name
	wks = gc.open(FORM_NAME).sheet1
	# wks is much like panda, can then do data manipulation and stuff
	return wks

def formatDate(strdate):
	date, time = strdate.split(' ')
	month, day, year = date.split('/')

	if len(month) == 1:
		month = '0' + month
	if len(day) == 1:
		day = '0' + day

	print(time)
	if len(time) == 7:
		time = '0' + time
	return year + '-' + month + '-' + day + 'T' + time + 'Z'

def checkTime(startDate, endDate):
	sdate, stime = startDate.split(' ')
	smonth, sday, syear = sdate.split('/')
	shour, smin, ssec = stime.split(':')

	edate, etime = endDate.split(' ')
	emonth, eday, eyear = edate.split('/')
	ehour, emin, esec = etime.split(':')

	sdatetime = datetime(int(syear), int(smonth), int(sday), int(shour), int(smin), int(ssec))
	edatetime = datetime(int(eyear), int(emonth), int(eday), int(ehour), int(emin), int(esec))

	if edatetime <= sdatetime:
		raise InvalidDateError()

def sendEmail():
#	smtp_server = "localhost"
#	port = 1025
#
#	context = ssl.create_default_context()
#
#	try:
#		server = smtplib.SMTP(smtp_server, port)
#		server.starttls(context=context)
#
#		server.sendmail("donotreply@escherwiki.com", "receiveremail@gmail.com", "test message")
#
#	except Exception as e:
#		print(e)
#
#	finally:
#		server.quit()


	# Open a plain text file for reading.  For this example, assume that
	# the text file contains only ASCII characters.
	#fp = open(textfile, 'rb')
	fp = "this is a message"
	# Create a text/plain message
	msg = MIMEText(fp)
	#fp.close()

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = 'The contents of %s' % "test text"
	msg['From'] = "me"
	msg['To'] = "you"

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	s = smtplib.SMTP('localhost')
	s.sendmail("me", "you?", msg.as_string())
	s.quit()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Print more output.')
# @click.argument('input_dir', required=True)
def main(verbose):
	"""Templated xml generator for SecurePoll."""
	try:
		#sendEmail()
		print("STARTING")
		# worksheet object to get data from form
		wks = getForm()
		print("GOT FORM")

		# get last submitted entry of spreadsheet (last submitted form)
		first_empty = next_available_row(wks)
		last_row = int(first_empty) - 1
		last_row = wks.row_values(last_row)

		# TODO - FORMAT FOR EMPTY ROWS
		print(last_row)

		pollTimestamp, meetDate, startDate, endDate, props, nonstudents, tempstays, email = last_row[0], last_row[1], last_row[2], last_row[3], last_row[4], last_row[5], last_row[6], last_row[7]

		print(pollTimestamp)

		# check that start and end dates are in correct order in time
		checkTime(startDate, endDate)

		config = {}
		config["type"] = "3-way"
		config["out_name"] = datetime.strptime(meetDate, '%m/%d/%Y').strftime('%d-%m-%Y') + ".xml"
		config["template"] = "3way-test.xml"

		context = {}

		context["title"] = "Voting Ballot for House Meeting - " + meetDate
		context["startDate"] = formatDate(startDate)
		context["endDate"] = formatDate(endDate)


		# if simply updating, keep same id number

		with open(LASTPOLLID) as f:
			lastpoll = f.readline().strip()
			last_id = f.readline().strip()
			last_timestamp = f.readline().strip()
		print("LAST TIME: " + last_timestamp)
		print("NOW TIME: " + pollTimestamp)
		print("LAST ID: " + last_id)
		if last_timestamp == pollTimestamp:
			with open(REPLACE, 'w') as f:
				f.write("done")
			return

		print(lastpoll)
		print(meetDate)
		if lastpoll != config["out_name"]:
			print("NEW POLL")
			rand_id = uuid.uuid1().int
			rand_id = str(rand_id)
			print("RANDID " + rand_id)
			rand_id = rand_id[0:8]

			# update replace file
			context["id"] = int(rand_id)

			with open(REPLACE, 'w') as f:
				f.write("new")
		else:
			context["id"] = int(last_id)

			# update replace file to use --update in import.py
			with open(REPLACE, 'w') as f:
				f.write("old")

		# Store meetDate and ID
		with open(LASTPOLLID, 'w') as f:
			f.write(config["out_name"] + '\n')
			f.write(str(context["id"]) + '\n')
			f.write(pollTimestamp)


		print("ID " + str(context["id"]))
		context["admins"] = "FeeFiFoeFum"
		context["intro"] = "Click the buttons to vote Yes, Abstain, or No. Information on all proposals can be found in the email."
		context["questions"] = []

		proposals = {}
		proposals["title"] = "House Proposals"
		proposals["options"] = [x.strip() for x in props.split(',')]
		context["questions"].append(proposals)

		approvals = {}
		approvals["title"] = "Non-Student Approval"
		approvals["options"] = [x.strip() for x in nonstudents.split(',')]
		context["questions"].append(approvals)

		temps = {}
		temps["title"] = "Temp Stays"
		temps["options"] = [x.strip() for x in tempstays.split(',')]
		context["questions"].append(temps)

		config["context"] = context

		print("FILLED ARRAY")

		# Get template and render template
		input_dir = os.path.dirname(os.path.abspath(__file__))
		template_dir = input_dir + '/templates'
		print(template_dir)

		output_location = os.path.join(input_dir, 'out')

		if not os.path.isdir(output_location):
			os.mkdir(output_location)

		template_env = jinja2.Environment(
										  loader=jinja2.FileSystemLoader(template_dir),
										  autoescape=jinja2.select_autoescape(['html', 'xml']),

		)

		out_file = os.path.join(output_location, config['out_name'])

		template = template_env.get_template(config['template'])

		template_out = template.render(config['context'])

		with open(out_file, 'w') as file:
			file.write(template_out)

		if verbose:
			print('Rendered ' + page['template'] + ' -> ' + output_file)

	except jinja2.UndefinedError:
		print('Error_Jinja: Template tried to operate on Undefined')
		exit(1)

	except jinja2.TemplateNotFound:
		print('Error_Jinja: Template not found')
		exit(1)

	except jinja2.TemplateAssertionError:
		print('Error_Jinja: Assertion error')
		exit(1)

	except jinja2.TemplateSyntaxError:
		print('Error_Jinja: Template syntax error')
		exit(1)

	except jinja2.TemplateError:
		print('Error_Jinja: Template Error')
		exit(1)

	except json.JSONDecodeError:
		print('Error_JSON: Decoding error')
		exit(1)

	except FileNotFoundError:
		print('Error_FileNotFound: could not find file')
		exit(1)

	except InvalidDateError as error:
		print('Error_InvalidDate: poll closes before it begins. Please modify endDate and startDate')
		exit(1)

if __name__ == "__main__":
	# pylint: disable=no-value-for-parameter
	main()

