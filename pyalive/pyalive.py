#!/usr/bin/env python
__author__ = 'ntrepid8'
import requests
import json
from requests.exceptions import ConnectionError
from argparse import ArgumentParser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

error_subject = "CRITICAL WEBSITE ERROR(S) - notified by pyalive"
ok_subject = "WEBSITE(S) ARE ALIVE - notified by pyalive"


def is_alive(url, session=None):
    s = session if session else requests
    r = s.get(url=url, verify=False)
    if r.status_code != 200:
        raise ValueError("%s failed with code %s" % (url, str(r.status_code)))
    return True


def send_smtp_mail(**kwargs):
    outer = MIMEMultipart()
    outer['Subject'] = kwargs.get('subject', 'CRITICAL WEBSITE ERROR(S) - notified by pyalive')
    outer['To'] = kwargs.get('to')
    outer['From'] = kwargs.get('from', 'noreply@foo.com')
    msg = MIMEText(kwargs.get('text', 'pyalive check(s) failed'))
    outer.attach(msg)
    composed = outer.as_string()
    server = smtplib.SMTP_SSL(kwargs['host'])
    server.login(kwargs['user'], kwargs['password'])
    server.set_debuglevel(0)
    server.sendmail(outer['From'], outer['To'], composed)
    server.quit()


def send_sendmail_mail(**kwargs):
    msg = MIMEText(kwargs.get('text', 'pyalive check(s) failed'))
    msg['Subject'] = kwargs.get('subject', 'CRITICAL WEBSITE ERROR(S) - notified by pyalive')
    msg['To'] = kwargs.get('to')
    msg['From'] = kwargs.get('from', 'noreply@foo.com')
    p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
    p.communicate(msg.as_string())


def main():
    parser = ArgumentParser()
    parser.add_argument("--config", dest="config", help="path to the JSON config file", default=None)
    parser.add_argument("--url", dest="url", help="url to test", default=None)
    parser.add_argument("--notify-on", dest="notify", default="errors",
                        help="notify your on \"all\" checks or \"errors\" only")
    args = parser.parse_args()
    results = dict()
    errors_detected = False
    if args.url:
        try:
            alive = is_alive(args.url)
            results[args.url] = {"alive": alive, "message": None}
        except ValueError, e:
            results[args.url] = {"alive": False, "message": repr(e)}
            errors_detected = True
        except ConnectionError, e:
            results[args.url] = {"alive": False, "message": repr(e)}
            errors_detected = True

    config = None
    if args.config:
        f = open(args.config)
        config = json.load(f)
        f.close()

    urls = config.get('urls', []) if config else []
    for url in urls:
        try:
            alive = is_alive(url)
            results[url] = {"alive": alive, "message": None}
        except ValueError, e:
            results[url] = {"alive": False, "message": repr(e)}
            errors_detected = True
        except ConnectionError, e:
            results[url] = {"alive": False, "message": repr(e)}
            errors_detected = True

    if args.notify == "all" or (args.notify == "errors" and errors_detected):
        smtp = config.get('smtp') if config else None
        common_email = {
            "from": config.get("from") if config else None,
            "subject": error_subject if errors_detected else ok_subject,
            "text": json.dumps(results, indent=4, sort_keys=True),
        }
        if smtp:
            for e in config.get('emails', []):
                email = {"to": e}
                email.update(common_email)
                email.update(smtp)
                send_smtp_mail(**email)
        elif config:
            for e in config.get('emails', []):
                email = {"to": e}
                email.update(common_email)
                send_sendmail_mail(**email)
        else:
            print common_email['text']


if __name__ == '__main__':
    main()