import smtplib
from email.mime.text import MIMEText
import ConfigParser
import os
import datetime
import subprocess

from dbconnect import DBConnect


def get_cfg():
    """
    Retrieve the configuration information from the .cfgnfo file
    located in the current user's home directory

    :return: dict
    """
    cfg_path = os.path.join(os.path.expanduser('~'), '.cfgnfo')

    cfg_info = {}
    config = ConfigParser.ConfigParser()
    config.read(cfg_path)

    for sect in config.sections():
        cfg_info[sect] = {}
        for opt in config.options(sect):
            cfg_info[sect][opt] = config.get(sect, opt)

    return cfg_info


def send_email(sender, recipient, subject, body):
    """
    Send out an email to give notice of success or failure

    :param sender: who the email is from
    :type sender: string
    :param recipient: list of recipients of the email
    :type recipient: list
    :param subject: subject line of the email
    :type subject: string
    :param body: success or failure message to be passed
    :type body: string
    """
    # This does not need to be anything fancy as it is used internally,
    # as long as we can see if the script succeeded or where it failed
    # at, then we are good to go
    msg = MIMEText(body)
    msg['Subject'] = subject

    # Expecting tuples from the db query
    msg['From'] = ', '.join(sender)
    msg['To'] = ', '.join(recipient)

    smtp = smtplib.SMTP("localhost")
    smtp.sendmail(sender, recipient, msg.as_string())
    smtp.quit()


def get_email_addr(dbinfo, who):
    """
    Retrieve email address(es) from the database
    for a specified role
    """
    key = 'email.{0}'.format(who)
    sql = "select value from ordering_configuration where key = %s"

    with DBConnect(**dbinfo) as db:
        db.select(sql, key)
        out = db[0][0].split(',')

    return out


def backup_cron():
    """
    Make a backup of the current user's crontab
    to /home/~/backups/
    """
    bk_path = os.path.join(os.path.expanduser('~'), 'backups')
    if not os.path.exists(bk_path):
        os.makedirs(bk_path)

    ts = datetime.datetime.now()
    cron_file = ts.strftime('crontab-%m%d%y-%H%M%S')

    with open(os.path.join(bk_path, cron_file), 'w') as f:
        subprocess.call(['crontab', '-l'], stdout=f)

def is_empty(an_iter):
    """
    report True if object is empty
    """
    empty = False
    if len(an_iter) == 0:
        empty = True

    return empty

def not_empty(an_iter):
    """
    report True if object is not empty
    """
    empty = False 
    if len(an_iter) > 0:
        empty = True 

    return empty






