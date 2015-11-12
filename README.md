# imap-email-address-collector

A Python script to scrape email addresses from all messages on an IMAP server.

Useful if an address book got lost and you want to recover contact email addresses from all incoming and outgoing emails.

Works by scanning "From" and "To" fields in message headers and tries to extract name and email address from them.

Outputs the found names and addresses to the terminal or a CSV file.


## Usage

	usage: imap-email-address-collector.py [-h] --host HOST --user USER
	                                       [--csv CSV] [--nossl] [--donotannoyme]
	                                       [--password PASSWORD] [--port PORT]

	optional arguments:
	  -h, --help           show this help message and exit
	  --host HOST          imap host address
	  --user USER          login username
	  --csv CSV            (optional) output csv filepath
	  --nossl              (optional) do not use ssl
	  --donotannoyme       (optional) do not complain about non-ssl connections
	  --password PASSWORD  (optional) login password (will be prompted otherwise)
	  --port PORT          (optional) imap host port, defaults to 993


## License
What?!