import smtplib
from email.mime.text import MIMEText
import ConfigParser
import os
import subprocess
import datetime

def get_cfg(cfgfile=".cfgnfo"):
    """
    Retrieve the configuration information from the .cfgnfo file
    located in the current user's home directory

    :return: dict
    """
    if cfgfile == ".cfgnfo":
        cfg_path = os.path.join(os.environ['ESPA_CONFIG_PATH'], '.usgs', cfgfile)
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

def api_cfg(section='config', cfgfile=".cfgnfo"):
    config = get_cfg(cfgfile)[section]
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

def backup_cron():
    """
    Make a backup of the current user's crontab
    to /home/~/backups/
    """
    bk_path = os.path.join(os.environ['ESPA_CONFIG_PATH'], backups)
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

def chunkify(lst, n):
    """Divides your list into "n" parts
    :param lst: list of objects to be divided
    :param n: the number of parts to divide list into
    :return: list of lists for pieces of original list
    """
    return [lst[i::n] for i in xrange(n)]


