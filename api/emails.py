'''
Purpose: holds all the emails + email logic for espa-web
Author: David V. Hill
'''

import datetime
import re

from cStringIO import StringIO

from email.mime.text import MIMEText
from smtplib import SMTP

from api.domain.order import Order
from api.api_logging import api_logger as logger
from api.domain.config import ApiConfig
config = ApiConfig()

class Emails(object):

    def __init__(self):
        self.status_base_url = config.url_for('status_url')

    def __send(self, recipient, subject, body):
        return self.send_email(recipient=recipient, subject=subject, body=body)

    def __order_status_url(self, email):
        return ''.join([self.status_base_url, '/', email])

    def send_email(self, recipient, subject, body):
        '''Sends an email to a receipient on the behalf of espa'''

        def _validate(email):
            if not self.validate_email(email):
                raise TypeError("Invalid email address provided:%s" % email)

        to_header = recipient

        if type(recipient) in (list, tuple):
            for r in recipient:
                _validate(r)

            to_header = ','.join(recipient)
        elif type(recipient) in (str, unicode):
            _validate(recipient)
        else:
            raise ValueError("Unsupported datatype for recipient:%s"
                             % type(recipient))

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['To'] = to_header
        msg['From'] = config.settings['email.espa_address']
        s = SMTP(host=config.settings['email.espa_server'])
        s.sendmail(msg['From'], recipient, msg.as_string())
        s.quit()

        return True

    def validate_email(self, email_addr):
        '''Compares incoming email address against regular expression
        to make sure its at least formatted like an email

        Keyword args:
        email -- String to validate as an email address

        Return:
        True if the string is a properly formatted email address
        False if not
        '''
        #pattern = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$'
        #some clown used a single quote in his email address... sigh.
        email_addr = email_addr.replace("'", "\'")
        pattern = r'^[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$'
        return re.match(pattern, email_addr.strip())

    def send_gzip_error_email(self, product_id):
        '''Sends an email to our people telling them to reprocess
           a bad gzip on the online cache'''

        address_block = config.settings['email.corrupt_gzip_notification_list']
        addresses = address_block.split(',')

        subject = "Corrupt gzip detected: %s" % product_id

        m = list()
        m.append("This is an automated email, please do not reply.\n\n ")
        m.append("A corrupt gzip has been detected on the online cache. ")
        m.append("Please reprocess this at your earliest convienience.\n\n")
        m.append("Thanks!\n\n")
        m.append("The LSRD Team")

        email_msg = ''.join(m)

        return self.__send(recipient=addresses,
                           subject=subject,
                           body=email_msg)

    def send_all_initial(self):
        '''Finds all the orders that have not had their initial emails sent and
        sends them'''

        orders = Order.where('status', 'ordered')
        for o in orders:
            if not o.initial_email_sent:
                self.send_initial(o)
                o.update('initial_email_sent', datetime.datetime.now())

    def send_initial(self, order):

        if isinstance(order, str):
            order = Order.where('orderid', order)[0]
        elif isinstance(order, int):
            order = Order(order)

        if not isinstance(order, Order):
            msg = 'order must be str, int or instance of Order'
            raise TypeError(msg)

        email = order.user_email()
        url = self.__order_status_url(email)

        m = list()
        m.append("Thank you for your order.\n\n")
        m.append("%s has been received and is currently " % order.orderid)
        m.append("being processed.  ")
        m.append("Another email will be sent when this order is complete.\n\n")
        m.append("You may view the status of your order and download ")
        m.append("completed products directly from %s\n\n" % url)
        m.append("Requested products\n")
        m.append("-------------------------------------------\n")

        scenes = Scene.where('order_id', order.id)

        #products = order.scene_set.all()

        for product in scenes:
            name = product.name

            if name == 'plot':
                name = "Plotting & Statistics"
            m.append("%s\n" % name)

        email_msg = ''.join(m)
        subject = 'Processing order %s received' % order.orderid

        return self.__send(recipient=email, subject=subject, body=email_msg)

    def send_completion(self, order):

        if isinstance(order, str):
            order = Order.where('orderid', order)
        elif isinstance(order, int):
            order = Order(id)

        if not isinstance(order, Order):
            msg = 'order must be str, int or instance of Order'
            raise TypeError(msg)

        email = order.user.email
        url = self.__order_status_url(email)

        m = list()
        m.append("%s is now complete and can be downloaded " % order.orderid)
        m.append("from %s.\n\n" % url)
        m.append("This order will remain available for 10 days.  ")
        m.append("Any data not downloaded will need to be reordered ")
        m.append("after this time.\n\n")
        m.append("Please contact Customer Services at 1-800-252-4547 or ")
        m.append("email custserv@usgs.gov with any questions.\n\n")
        m.append("Requested products\n")
        m.append("-------------------------------------------\n")

        #products = order.scene_set.filter(status='complete')
        scenes = Scene.where("status", "complete")

        for product in scenes:
            line = product.name
            if line == 'plot':
                line = "Plotting & Statistics"

            m.append("%s\n" % line)

        body = ''.join(m)
        subject = 'Processing for %s complete.' % order.orderid

        return self.__send(recipient=email, subject=subject, body=body)


    def send_purge_report(self, start_capacity, end_capacity, orders):
        buffer = StringIO()
        for order in orders:
            buffer.write('{0}\n'.format(order))
        order_str = buffer.getvalue()
        buffer.close()

        body = '''===================================
        Disk usage before purge
        Capacity:{start_capacity} Used:{start_used} Available:{start_available} Percent Used:{start_percent_free}

        ===================================
        Disk usage after purge
        Capacity:{end_capacity} Used:{end_used} Available:{end_available} Percent Used:{end_percent_free}

        ===================================
        Past 24 Hours
        Orders Placed:not available
        Orders Completed:not available
        Scenes Placed:not available
        Scenes Completed:not available

        Past 7 Days
        Orders Placed:not available
        Orders Completed:not available
        Scenes Placed:not available
        Scenes Completed:not available

        ===================================
        Open orders:not available
        Open scenes:not available

        ===================================
        Purged orders
          {purged_orders}
        ========== End of report ==========
        '''.format(start_capacity=start_capacity['capacity'],
                   start_used=start_capacity['used'],
                   start_available=start_capacity['available'],
                   start_percent_free=start_capacity['percent_free'],
                   end_capacity=end_capacity['capacity'],
                   end_used=end_capacity['used'],
                   end_available=end_capacity['available'],
                   end_percent_free=end_capacity['percent_free'],
                   purged_orders=order_str)

        now = datetime.datetime.now()
        subject = 'Purged orders for {month}-{day}-{year}'.format(day=now.day,
                                                                  month=now.month,
                                                                  year=now.year)
        recipients = config.settings['email.purge_report_list']
        return self.__send(recipient=recipients, subject=subject, body=body)

def send_purge_report(start_capacity, end_capacity, orders):
    return Emails().send_purge_report(start_capacity, end_capacity, orders)

