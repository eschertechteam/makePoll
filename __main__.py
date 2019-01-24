import json
import os
import shutil
import click
import jinja2
import uuid
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

scope = ['https://spreadsheets.google.com/feeds',
		 'https://www.googleapis.com/auth/drive']

# CRED should be file path to the json file of the service account
# made by going to Google API > Create Credentials > Service Account > JSON
CRED = 'makepoll-f158d926816b.json'

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

# populate config file
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


# find first empty row N. N - 1 is last row and most recent form entry
# courtesy of Pedro Lobito on StackOverflow
def next_available_row(wks):
	print(wks.col_values(1))
	str_list = list(filter(None, wks.col_values(1)))  # fastest
	
	# Note that this is 1-indexed
	return str(len(str_list)+1)


# authenticate access to the Google Form responses
def getForm():
	credentials = ServiceAccountCredentials.from_json_keyfile_name(CRED, scope)
	gc = gspread.authorize(credentials)
	
	# Sample form response sheet name
	wks = gc.open(FORM_NAME).sheet1
	# wks is much like panda, can then do data manipulation and stuff
	return wks


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Print more output.')
# @click.argument('input_dir', required=True)
def main(verbose):
	"""Templated xml generator for SecurePoll."""
	try:
		
		# worksheet object to get data from form
		wks = getForm()
		
		# get last submitted entry of spreadsheet (last submitted form)
		first_empty = next_available_row(wks)
		last_row = int(first_empty) - 1
		last_row = wks.row_values(last_row)
		
		meetDate, startDate, endDate, props, nonstudents, tempstays = last_row[1], last_row[2], last_row[3], last_row[4], last_row[5], last_row[6]
		
		config = {}
		config["type"] = "3-way"
		config["out_name"] = meetDate + ".xml"
		config["template"] = "3way-test.xml"
		
		context = {}
		
		
		context["title"] = "Voting Ballot for House Meeting - " + datetime.strptime(meetDate, '%m-%d-%Y').strftime('%d/%m/%Y')
		context["startDate"] = startDate
		context["endDate"] = endDate
		context["id"] = uuid.uuid1().int & (1<<64)-1
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
		
		print(config)
		
		# Get template and render template
		input_dir = os.path.dirname(os.path.abspath(__file__))
		template_dir = input_dir + '/templates'
		
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
		
		print(out_file)
		
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

if __name__ == "__main__":
	# pylint: disable=no-value-for-parameter
	main()
