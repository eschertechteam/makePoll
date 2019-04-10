#!/usr/bin/env bash

CDPATH="/home/bitnami/apps/mediawiki/htdocs/extensions/SecurePoll/house_poll"
PYPATH="/home/bitnami/apps/mediawiki/htdocs/extensions/SecurePoll/house_poll/make_poll.py"
IMPATH="/home/bitnami/apps/mediawiki/htdocs/extensions/SecurePoll/cli/import.php"
OUPATH="/home/bitnami/apps/mediawiki/htdocs/extensions/SecurePoll/house_poll/out"
REPLACE=$CDPATH/REPLACE

/usr/bin/python3 $PYPATH

echo "PYTHON STARTED MAYBE"

line=$(head -n 1 '/home/bitnami/apps/mediawiki/htdocs/extensions/SecurePoll/house_poll/LASTPOLLID')
echo $line

echo $OUPATH/$line

if grep -R 'new' $REPLACE; then
	echo "New file"
	/opt/bitnami/php/bin/php $IMPATH $OUPATH/$line
	echo 'done' > $REPLACE
elif grep -R 'old' $REPLACE; then
	echo "Old updated file"

	/opt/bitnami/php/bin/php $IMPATH --replace $OUPATH/$line
	echo 'done' > $REPLACE
else
	echo "Nothing new to update"
fi
