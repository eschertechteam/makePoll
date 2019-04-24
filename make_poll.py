"""
Templated xml generator for SecurePoll.
Original author: Fee Christoph
"""

import json
import os
import logging
import datetime
import click
import jinja2
import uuid
import gspread
import smtplib
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

logger = logging.getLogger("make_poll.py")
# If verbose is set, also print debug logs to the log file, else stop at info
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('make_poll.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

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
	logger.debug("column values: {}".format(wks.col_values(1)))
	str_list = list(filter(None, wks.col_values(1)))  # fastest

	# Note that this is 1-indexed
	return str(len(str_list)+1)


# authenticate access to the Google Form responses
def getForm(form):
	logger.debug("cred file:" + CRED)
	credentials = ServiceAccountCredentials.from_json_keyfile_name(CRED, scope)
	logger.info("GETTING FORM {}".format(form))
	gc = gspread.authorize(credentials)
	logger.info("AUTHORIZED")
	# Sample form response sheet name
	wks = gc.open(form).sheet1
	# wks is much like panda, can then do data manipulation and stuff
	return wks

def formatDate(strdate):
	date, time = strdate.split(' ')
	month, day, year = date.split('/')

	if len(month) == 1:
		month = '0' + month
	if len(day) == 1:
		day = '0' + day

	logger.debug(time)
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
@click.option('--date', '-d', nargs=3, help='YEAR MON DAY, e.g. 2019 04 23')
# @click.argument('input_dir', required=True)
def main(verbose, date):

	if len(date) == 3:
		year = date[0]
		month = '{:02d}'.format(date[1])
		day = '{:02d}'.format(date[2])
	else:
		year = datetime.datetime.now().year
		month = '{:02d}'.format(datetime.datetime.now().month)
		day = '{:02d}'.format(datetime.datetime.now().day)

	# response sheet name
	form = "Escher_Poll_{month}_{day}_{year}".format(year=year, month=month, day=day)
	try:
		#sendEmail()
		logger.info("START: Start collecting poll results")
		# worksheet object to get data from form
		wks = getForm(form)
		logger.info("SUCCESS: retrieved form from Google")

		# get last submitted entry of spreadsheet (last submitted form)
		first_empty = next_available_row(wks)
		last_row = int(first_empty) - 1
		last_row = wks.row_values(last_row)

		# TODO - FORMAT FOR EMPTY ROWS
		logger.debug("last row: {}".format(last_row))

		pollTimestamp, meetDate, startDate, endDate, props, nonstudents, tempstays, email = last_row[0], last_row[1], last_row[2], last_row[3], last_row[4], last_row[5], last_row[6], last_row[7]

		logger.info("poll timestamp = {}".format(pollTimestamp))

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
		logger.debug("LAST TIME: " + last_timestamp)
		logger.debug("NOW TIME: " + pollTimestamp)
		logger.debug("LAST ID: " + last_id)
		if last_timestamp == pollTimestamp:
			with open(REPLACE, 'w') as f:
				f.write("done")
			return

		logger.debug("LAST POLL: " + lastpoll)
		logger.debug("MEET DATE: " + meetDate)
		if lastpoll != config["out_name"]:
			logger.info("NEW POLL")
			rand_id = uuid.uuid1().int
			rand_id = str(rand_id)
			logger.info("RANDID " + rand_id)
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

		logger.debug("ID " + str(context["id"]))
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

		logger.info("FILLED ARRAY")

		# Get template and render template
		input_dir = os.path.dirname(os.path.abspath(__file__))
		template_dir = input_dir + '/templates'
		logger.debug("template dir: " + template_dir)

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

		logger.info('Rendered ' + config['template'] + ' -> ' + out_file)

	except jinja2.UndefinedError:
		logger.error('Error_Jinja: Template tried to operate on Undefined')
		exit(1)

	except jinja2.TemplateNotFound:
		logger.error('Error_Jinja: Template not found')
		exit(1)

	except jinja2.TemplateAssertionError:
		logger.error('Error_Jinja: Assertion error')
		exit(1)

	except jinja2.TemplateSyntaxError:
		logger.error('Error_Jinja: Template syntax error')
		exit(1)

	except jinja2.TemplateError:
		logger.error('Error_Jinja: Template Error')
		exit(1)

	except json.JSONDecodeError:
		logger.error('Error_JSON: Decoding error')
		exit(1)

	except FileNotFoundError as e:
		logger.error('FileNotFound: {}'.format(e))
		exit(1)

	except InvalidDateError as error:
		logger.error('Error_InvalidDate: poll closes before it begins. Please modify endDate and startDate')
		exit(1)

if __name__ == "__main__":
	# pylint: disable=no-value-for-parameter
	main()

