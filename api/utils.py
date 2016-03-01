import smtplib
from email.mime.text import MIMEText
import ConfigParser
import os
import datetime
import subprocess
import datetime

from dbconnect import DBConnect
import psycopg2.extras

def get_cfg(cfgfile=".cfgnfo"):
    """
    Retrieve the configuration information from the .cfgnfo file
    located in the current user's home directory

    :return: dict
    """
    if cfgfile == ".cfgnfo" or cfgfile == '.cfgnfo-test':
        cfg_path = os.path.join(os.path.expanduser('~'), '.cfgnfo')
    else:
        cfg_path = cfgfile

    cfg_info = {}
    config = ConfigParser.ConfigParser()
    config.read(cfg_path)

    for sect in config.sections():
        cfg_info[sect] = {}
        for opt in config.options(sect):
            cfg_info[sect][opt] = config.get(sect, opt)

    return cfg_info

def api_cfg(cfgfile=".cfgnfo"):
    try:
        mode = os.environ["espa_api_testing"]
        if mode == "True":
            cfgfile = ".cfgnfo-test"
    except:
        pass

    config = get_cfg(cfgfile)['config']
    config['cursor_factory'] = psycopg2.extras.DictCursor
    return config

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

def lowercase_all(indata):
    if hasattr(indata, 'iteritems'):
        ret = {}
        for key, val in indata.iteritems():
            ret[lowercase_all(key)] = lowercase_all(val)
        return ret

    elif isinstance(indata, basestring):
        return indata.lower()

    elif hasattr(indata, '__iter__'):
        ret = []
        for item in indata:
            ret.append(lowercase_all(item))
        return ret

    else:
        return indata

def date_from_doy(year, doy):
    '''Returns a python date object given a year and day of year'''

    d = datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(doy) - 1)

    if int(d.year) != int(year):
        raise Exception("doy [%s] must fall within the specified year [%s]" %
                        (doy, year))
    else:
        return d

