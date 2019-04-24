# makePoll
Google Form -> xml -> SecurePoll to set up polls on the wiki


##	Set up on the developer console (one time):
	1. Create service account
	2. Enable Google Sheet API
	3. Get credentials for the API with service account
	4. Set CRED variable to the path to the credentials file


##	Set up before running form response parser (every poll):
	1. Go to response tab of the form
	2. Click the green icon (view response in sheets)
	3. Create a Google sheet with name "Escher_Poll_mm_dd_yy" or something like that
	4. Share sheet with service account email (felichri@makepoll-224313.iam.gserviceaccount.com) for now
