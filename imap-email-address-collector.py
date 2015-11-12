#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# imap-email-address-collector
# 
import sys
import re
import csv
import getpass
import imaplib
import argparse
from email.parser import HeaderParser

RE_EMAIL = re.compile(r'^[a-z0-9._%+-]+\@[a-z0-9.-]+\.[a-z]{2,}$')
RE_QUOTES = re.compile(r'[\'\"]')
RE_SPACES = re.compile(r'[\n\t\s]+')

NOSSL_PROMT = 'LETTHEWOLDREADALLMESSAGES'

results = {}
unmatched = set()


def matchAndAdd(email, name=''):
	email = email.lower()
	if RE_EMAIL.match(email):
		if email not in results or len(name) > len(results[email]): # only overwrite with longer name
			results[email] = name.strip()
	else:
		unmatched.add(email)


def grabAddress(address):
	address = str(address).strip()
	address = RE_QUOTES.sub('', address)
	address = RE_SPACES.sub(' ', address)

	if address.startswith('<'): # No name, just an email address
		address = address[1:]
		if address.endswith('>'):
			address = address[:-1]
		matchAndAdd(address)

	else: # Name and email address
		try:
			name, email = address.split('<')
		except Exception:
			matchAndAdd(address)
		else:
			matchAndAdd(email[:-1], name)


def listBoxes(imap):
	boxes = imap.list()
	if boxes[0] == 'OK' and len(boxes) > 1:
		for box in boxes[1]:
			box = re.split(r'\) \".\" ', box, maxsplit=1)
			if len(box) == 2:
				yield box[1]
	else:
		print 'No folders found.'
		sys.exit(0)


def main(args):
	if args.password:
		password = args.password
	else:
		password = getpass.getpass('Password: ')

	if args.nossl:
		print 'Connecting to %s:%s without SSL...' % (args.host, args.port)
		if not args.donotannoyme:
			confirmation = raw_input('Please type %s:' % NOSSL_PROMT)
			if not confirmation == NOSSL_PROMT:
				print 'Good choice ;) (Disable with --donotannoyme)'
				sys.exit(1)
		imap = imaplib.IMAP4(args.host, args.port)
	else:
		print 'Connecting to %s:%s over SSL...' % (args.host, args.port)
		imap = imaplib.IMAP4_SSL(args.host, args.port)

	try:
		imap.login(args.user, password)

	except imaplib.IMAP4.error:
		print "Login failed."
		sys.exit(1)
	else:

		print 'Logged in as %s' % args.user

	print 'Collecting email addresses from all messages...'

	for box in listBoxes(imap):
		print 'Scanning %s' % box

		imap.select(box, readonly=True)
		typ, data = imap.search(None, 'ALL')
		count = 0

		for num in data[0].split():
			typ, data = imap.fetch(num, '(BODY[HEADER.FIELDS (TO FROM)])')
			headers = headerParser.parsestr(data[0][1])

			for h in ('From', 'To'):
				if headers[h]:
					for address in headers[h].split(','):
						grabAddress(address)

			count += 1
			sys.stdout.flush()
			sys.stdout.write('\rScanned %s messages' % count)

		if count > 0:
			print ''

		imap.close()

	imap.logout()

	if len(results) > 0:
		print 'Found %s addresses' % len(results)

		if not args.csv:
			toStdout = True
		else:
			try:
				outFile = open(args.csv, 'wb')
			except Exception:
				toStdout = True
				print 'Cannot write to %s, dumping out here.' % args.csv
			else:
				toStdout = False

		if toStdout:
			outFile = sys.stdout
			print '======================================================='
		else:
			print 'Writing to %s' % args.csv

		writer = csv.writer(outFile)

		writer.writerows(list(results.items()))

		if toStdout:
			print '======================================================='
		else:
			outFile.close()

		if len(unmatched) > 0:
			print 'Could not interpret %s address(es): %s' % (len(unmatched), "'"+("', '".join(unmatched))+"'")
	else:
		print 'No addresses found'


if __name__ == '__main__':
	headerParser = HeaderParser()
	argParser = argparse.ArgumentParser()

	argParser.add_argument('--host', help='imap host address', required=True)
	argParser.add_argument('--user', help='login username', required=True)
	argParser.add_argument('--csv', help='(optional) output csv filepath')
	argParser.add_argument('--nossl', help='(optional) do not use ssl', action='store_true')
	argParser.add_argument('--donotannoyme', help='(optional) do not complain about non-ssl connections', action='store_true')
	argParser.add_argument('--password', help='(optional) login password (will be prompted otherwise)')
	argParser.add_argument('--port', help='(optional) imap host port, defaults to 993', type=int, default=993)

	main(argParser.parse_args())
