'''
Purpose: lta services client module
Author: David V. Hill
'''

import requests
import collections
import xml.etree.ElementTree as xml
from cStringIO import StringIO

from suds.client import Client as SoapClient
from suds.cache import ObjectCache

from api.domain import sensor
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.system.logger import ilogger as logger

config = ConfigurationProvider()

class LTAService(object):
    ''' Abstract service client for all of LTA services '''

    service_name = None

    def __init__(self):
        self.xml_header = "<?xml version ='1.0' encoding='UTF-8' ?>"
        self.url = config.url_for(self.service_name)

    def __repr__(self):
        return "LTAService:{0}".format(self.__dict__)


class LTASoapService(LTAService):
    ''' Abstract service class for SOAP based clients '''

    def __init__(self, *args, **kwargs):
        super(LTASoapService, self).__init__(*args, **kwargs)
        logger.info('Building SoapClient for:{0}'.format(self.url))
        self.client = SoapClient(self.url, cache=self.build_object_cache())

    def build_object_cache(self):
        cache = ObjectCache()
        cache.setduration(seconds=config.get('soap.client_timeout'))
        cache.setlocation(config.get('soap.cache_location'))
        return cache


class RegistrationServiceClient(LTASoapService):

    service_name = 'registration'

    def __init__(self, *args, **kwargs):
        super(RegistrationServiceClient, self).__init__(*args, **kwargs)

    def login_user(self, username, password):
        '''Authenticates a username/password against the EE Registration
        Service

        Keyword args:
        username EE username
        password EE password

        Returns:
        EE contactId if login is successful
        Exception if unsuccessful with reason
        '''

        return repr(self.client.service.loginUser(username, password))

    def get_user_info(self, username, pw):
        '''Retrieves the email address on file for the supplied credentials

        Keyword args:
        username EE username
        pw       EE password

        Returns:
        Email address on file for the user.
        Exception if the username/password is invalid
        None if there is no email on file.
        '''

        # build a named tuple for the return value
        userinfo = collections.namedtuple('UserInfo',
                                          ['email', 'first_name', 'last_name'])

        info = self.client.service.getUserInfo(username, pw).contactAddress

        userinfo.email = info.email
        userinfo.first_name = info.firstName
        userinfo.last_name = info.lastName

        return userinfo

    def get_username(self, contactid):
        '''Retrieves the users EE username given their contactid

        Keyword args:
        contactid -- The EE contactid

        Return:
        The EE username
        '''

        return self.client.service.getUserName(contactid)

class OrderWrapperServiceClient(LTAService):
    '''LTA's OrderWrapper Service is a business process service that handles
    populating demographics and interacting with the inventory properly when
    callers order data.  It is implemented as a REST style service that passes
    schema-bound XML as the payload.

    This is the preferred method for ordering data from the LTA (instead of
    calling TRAM services directly), as there are multiple service calls that
    must be performed when placing orders, and only the LTA team really know
    what those calls are.  Their services are largely undocumented.
    '''
    service_name = 'orderservice'

    def __init__(self, *args, **kwargs):
        super(OrderWrapperServiceClient, self).__init__(*args, **kwargs)

    def verify_scenes(self, scene_list):
        ''' Checks to make sure the scene list is valid, where valid means
        the scene ids supplied exist in the Landsat inventory and are orderable

        Keyword args:
        scene_list A list of scenes to be verified

        Returns:
        A dictionary with keys matching the scene list and values are 'true'
        if valid, and 'false' if not.

        Return value example:
        dictionary = dict()
        dictionary['LT51490212007234IKR00'] = True
        dictionary['asdf'] = False
        ...
        ...
        ...

        '''

        #build the service + operation url
        request_url = '{0}/verifyScenes'.format(self.url)

        #build the request body
        sb = StringIO()
        sb.write(self.xml_header)

        head = ("<sceneList "
                "xmlns='http://earthexplorer.usgs.gov/schema/sceneList' "
                "xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' "
                "xsi:schemaLocation="
                "'http://earthexplorer.usgs.gov/schema/sceneList "
                "http://earthexplorer.usgs.gov/EE/sceneList.xsd'>")

        sb.write(head)

        for s in scene_list:
            product = sensor.instance(s)
            sb.write("<sceneId sensor='{0}'>{1}</sceneId>"
                     .format(product.lta_name, s.upper()))

        sb.write("</sceneList>")

        request_body = sb.getvalue()

        #set the required headers
        headers = dict()
        headers['Content-Type'] = 'application/xml'
        headers['Content-Length'] = len(request_body)

        #send the request and check return status
        #request = urllib2.Request(request_url, request_body, headers)
        __response = requests.post(request_url,
                                   data=request_body,
                                   headers=headers)

        response = None

        if __response.ok:
            response = __response.content
        else:
            msg = StringIO()
            msg.write("Error in lta.OrderWrapperServiceClient.verify_scenes\n")
            msg.write("Non 200 response code from service\n")
            msg.write("Response code was:{0}".format( __response.status_code))
            msg.write("Reason:{0}".format(__response.reason))
            # Return the code and reason as an exception
            raise Exception(msg.getvalue())

        __response.close()

        #parse, transform and return response
        retval = dict()
        response = response.replace('&', '&amp;')
        response = response.replace('\n', '')

        root = xml.fromstring(response)
        scenes = root.getchildren()

        for s in list(scenes):
            if s.attrib['valid'] == 'true':
                status = True
            else:
                status = False

            retval[s.text] = status

        return retval

    def order_scenes(self, scene_list, contact_id, priority=5):
        ''' Orders scenes through OrderWrapperService

        Keyword args:
        scene_list A list of scene ids to order
        contactId  The EE user id that is ordering the data
        priority   The priority placed on the backend ordering system.
                   Landsat has asked us to set the priority to 5 for all ESPA
                   orders.

        Returns:
        A dictionary containing the lta_order_id and up to three lists of scene
        ids, organized by their status.  If there are no scenes in the
        ordered status, the ordered list and the lta_order_id will not be
        present.  If there are no scenes in either the invalid or available
        status, then those respective lists will not be present.

        Example 1 (Scenes in each status):
        {
            'lta_order_id': 'abc123456',
            'ordered': ['scene1', 'scene2', 'scene3'],
            'invalid': ['scene4', 'scene5', 'scene6'],
            'available': ['scene7', 'scene8', 'scene9']
         }

        Example 2 (No scenes ordered):
        {
            'invalid': ['scene1', 'scene2', 'scene3'],
            'available': ['scene4', 'scene5', 'scene6']
        }

        Example 3 (No scenes available):
        {
            'lta_order_id': 'abc123456',
            'ordered': ['scene1', 'scene2', 'scene3'],
            'invalid': ['scene4', 'scene5', 'scene6']
        }
        '''

        # build service url
        request_url = '{0}/submitOrder'.format(self.url)

        def build_request(contact_id, priority, product_list):
            # build the request body
            sb = StringIO()
            sb.write(self.xml_header)

            head = ("<orderParameters "
                    "xmlns="
                    "'http://earthexplorer.usgs.gov/schema/orderParameters' "
                    "xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' "
                    "xsi:schemaLocation="
                    "'http://earthexplorer.usgs.gov/schema/orderParameters "
                    "http://earthexplorer.usgs.gov/EE/orderParameters.xsd'>")

            sb.write(head)
            sb.write('<contactId>{0}</contactId>'.format(contact_id))
            sb.write('<requestor>ESPA</requestor>')

            # 1111111 is a dummy value.
            sb.write('<externalReferenceNumber>{0}</externalReferenceNumber>'
                     .format(1111111))

            sb.write('<priority>{0}</priority>'.format(priority))

            product_info = self.get_download_urls(product_list, contact_id)

            for p in product_info.keys():

                try:
                    sensor.instance(p)
                except sensor.ProductNotImplemented, pne:
                    raise pne
                else:
                    sb.write('<scene>')
                    sb.write('<sceneId>{0}</sceneId>'.format(p))
                    sb.write('<prodCode>{0}</prodCode>'
                             .format(product_info[p]['lta_code']))
                    sb.write('<sensor>{0}</sensor>'
                             .format(product_info[p]['sensor']))
                    sb.write('</scene>')

            sb.write('</orderParameters>')

            request_body = sb.getvalue()

            return request_body

        payload = build_request(contact_id, priority, scene_list)
        # set the required headers
        headers = dict()
        headers['Content-Type'] = 'application/xml'
        headers['Content-Length'] = len(payload)

        # send the request and check response

        __response = requests.post(request_url, data=payload, headers=headers)

        if __response.ok:
            response = __response.content
        else:
            logger.debug('Non 200 response from lta.order_scenes')
            logger.debug('Response:{0}'.format(__response.content))
            logger.debug('Request:{0}'.format(payload))
            msg = StringIO()
            msg.write('Error in lta.OrderWrapperServiceClient.order_scenes\n')
            msg.write('Non 200 response code from service\n')
            msg.write('Response code was:{0}'.format(__response.status_code))
            msg.write('Reason:{0}'.format(__response.reason))
            
            raise Exception(msg.getvalue())

        __response.close()

        # parse the response
        '''
        Example response for scenes

        <?xml version="1.0" encoding="UTF-8"?>
        <orderStatus xmlns="http://earthexplorer.usgs.gov/schema/orderStatus"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://host/schema/orderStatus
            http://host/OrderWrapperServicedevsys/orderStatus.xsd">

            <scene>
                <sceneId>LT51490212007234IKR00</sceneId>
                <prodCode>T273</prodCode>
                <sensor>LANDSAT_TM</sensor>
                <status>ordered</status>
                <orderNumber>0621405213419</orderNumber>
            </scene>

            <scene>
                <sceneId>LE70290302013153EDC00</sceneId>
                <prodCode>T271</prodCode>
                <sensor>LANDSAT_ETM_SLC_OFF</sensor>
                <status>available</status>
                <downloadURL>http://one_time_use.tar.gz</downloadURL>
            </scene>

            <scene>
                <sceneId>LE70290302003142EDC00</sceneId>
                <prodCode>T272</prodCode>
                <sensor>LANDSAT_ETM_PLUS</sensor>
                <status>invalid</status>
            </scene>

        </orderStatus>
        '''

        logger.warn('Ordering scenes SOAP response:{0}'.format(response))

        # since the xml is namespaced there is a namespace prefix for every
        # element we are looking for.  Build those values to make the code
        # a little more sane
        response_namespace = 'http://earthexplorer.usgs.gov/schema/orderStatus'
        ns_prefix = ''.join(['{', response_namespace, '}'])
        status_elem = ''.join([ns_prefix, 'status'])
        sceneid_elem = ''.join([ns_prefix, 'sceneId'])
        order_number_elem = ''.join([ns_prefix, 'orderNumber'])
        # leave this here for now.  We aren't using it yet but will when EE
        # straightens out their urls + internal dowloading capability
        #dload_url_elem = ''.join([ns_prefix, 'downloadURL'])

        # escape the ampersands and get rid of newlines if they exist
        # was having problems with the sax escape() function
        response = response.replace('&', '&amp;').replace('\n', '')

        #this will get us the list of <scene></scene> elements
        scene_elements = xml.fromstring(response).getchildren()

        # the dictionary we will return as the response
        # contains the lta_order_id at the top (if anything is ordered)
        # and possibly three lists of scenes, one for each status
        # retval['available'] = list()
        # retval['invalid'] = list()
        # retval['ordered'] = list()
        retval = dict()

        for scene in scene_elements:

            name = scene.find(sceneid_elem).text
            status = scene.find(status_elem).text

            if status == 'available':
                if not 'available' in retval:
                    retval['available'] = [name]
                else:
                    retval['available'].append(name)
            elif status == 'invalid':
                if not 'invalid' in retval:
                    retval['invalid'] = [name]
                else:
                    retval['invalid'].append(name)
            elif status == 'ordered':
                if not 'ordered' in retval:
                    retval['ordered'] = [name]
                else:
                    retval['ordered'].append(name)

                if not 'lta_order_id' in retval:
                    retval['lta_order_id'] = scene.find(order_number_elem).text

        return retval

    def get_download_urls(self, product_list, contact_id):
        ''' Returns a list of named tuples containing the product id,
        product status, product code, sensor name, and (conditionally) a
        one time use download url to obtain the product.  The download url
        is only populated if the status of the product is returned
        as 'available'

        Keyword args:
        product_list A list of products to generate a download url for
        contact_id The id of the user requesting the product urls

        Returns:
        A dict of dicts:
        d[product_name] = {'lta_prod_code': 'T272',
                           'sensor': 'LANDSAT_8',
                           'status': 'available',
                           'download_url': 'http://one_time_use.tar.gz'}
        '''

        def build_request(contact_id, products):
            # build the request body
            sb = StringIO()
            sb.write(self.xml_header)
            head = ("<downloadSceneList "
                    "xmlns="
                    "'http://earthexplorer.usgs.gov/schema/downloadSceneList' "
                    "xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' "
                    "xsi:schemaLocation="
                    "'http://earthexplorer.usgs.gov/schema/downloadSceneList "
                    "http://earthexplorer.usgs.gov/EE/downloadSceneList.xsd'>")

            sb.write(head)

            sb.write("<contactId>{0}</contactId>".format(contact_id))

            for p in products:
                try:
                    product = sensor.instance(p)
                except sensor.ProductNotImplemented:
                    logger.warn("{0} not implemented, skipping".format(p))
                else:
                    sb.write("<scene>")
                    sb.write("<sceneId>{0}</sceneId>"
                             .format(product.product_id))

                    sb.write("<sensor>{0}</sensor>".format(product.lta_name))
                    sb.write("</scene>")

            sb.write("</downloadSceneList>")

            request_body = sb.getvalue()

            return request_body

        def parse_response(response_xml):
            '''<?xml version="1.0" encoding="UTF-8"?>'
               <downloadList xmlns="http://host/schema/downloadList"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://host/schema/downloadList
                   http://host/OrderWrapperServicedevsys/downloadList.xsd">
               <scene>
               <sceneId>LC80380292014211LGN00</sceneId>
               <prodCode>D217</prodCode>
               <sensor>LANDSAT_8</sensor>
               <status>available</status>
               <downloadURL>http://one_time_use.tar.gz</downloadURL>
               </scene>
               </downloadList>
             '''

            __ns = 'http://earthexplorer.usgs.gov/schema/downloadList'
            __ns_prefix = ''.join(['{', __ns, '}'])
            sceneid_elem = ''.join([__ns_prefix, 'sceneId'])
            prod_code_elem = ''.join([__ns_prefix, 'prodCode'])
            sensor_elem = ''.join([__ns_prefix, 'sensor'])
            status_elem = ''.join([__ns_prefix, 'status'])
            dload_url_elem = ''.join([__ns_prefix, 'downloadURL'])

            # escape the ampersands and get rid of newlines if they exist
            # was having problems with the sax escape() function
            #response = response_xml.replace('&', '&amp;').replace('\n', '')

            #this will get us the list of <scene></scene> elements

            scene_elements = list(xml.fromstring(response_xml).getchildren())

            retval = {}

            ehost = config.url_for('external_cache')
            ihosts = config.url_for('internal_cache').split(',')

            for index, scene in enumerate(list(scene_elements)):
                name = scene.find(sceneid_elem).text
                prod_code = scene.find(prod_code_elem).text
                sensor = scene.find(sensor_elem).text
                status = scene.find(status_elem).text

                retval[name] = {'lta_code': prod_code,
                                'sensor': sensor,
                                'status': status}

                #may not be included with every response if not online
                __dload_url = scene.find(dload_url_elem)

                dload_url = None

                if __dload_url is not None:
                    dload_url = __dload_url.text

                    if dload_url.find(ehost) != -1:
                        dload_url = dload_url.replace(ehost,
                                                      ihosts[index % 2].strip())
                    retval[name]['download_url'] = dload_url

            return retval

        # build service url
        request_url = "{0}/{1}".format(self.url, 'getDownloadURL')
        payload = build_request(contact_id, product_list)
        response = requests.post(request_url, data=payload)

        if response.ok:
            return parse_response(response.text)
        else:
            msg = ('Error retrieving download urls.  Reason:{0} Response:{1}\n'
                   'Contact id:{2}'.format(response.reason,
                                           response.text,
                                           contact_id))

            logger.error(msg)
            raise RuntimeError(msg)

    def input_exists(self, product, contact_id):
        '''Determines if a given product is ready for download'''

        result = self.get_download_url([product], contact_id)

        if 'download_url' in result[product] \
                and result[product]['status'] == 'available':

            return True
        else:
            return False


class OrderUpdateServiceClient(LTASoapService):

    service_name = 'orderupdate'

    def __init__(self, *args, **kwargs):
        super(OrderUpdateServiceClient, self).__init__(*args, **kwargs)

    #TODO - Migrate this call to the OrderWrapperService
    def get_order_status(self, order_number):
        ''' Returns the status of the supplied order number

        Keyword args:
        order_number The EE order number to check status on

        Returns:
        A list of dictionaries containing unit_num, unit_status & sceneid
        '''

        retval = dict()

        resp = self.client.factory.create("getOrderStatusResponse")
        resp = self.client.service.getOrderStatus(order_number)

        if resp is None:
            return dict()

        retval['order_num'] = str(resp.order.orderNbr)
        retval['order_status'] = str(resp.order.orderStatus)
        retval['units'] = list()

        for u in resp.units.unit:
            unit = dict()
            unit['unit_num'] = int(u.unitNbr)
            unit['unit_status'] = str(u.unitStatus)
            unit['sceneid'] = str(u.orderingId)
            retval['units'].append(unit)

        return retval

    def update_order(self, order_number, unit_number, status):
        ''' Update the status of orders that ESPA is working on

        Keyword args:
        order_number The EE order number to update
        unit_number  The unit within the order to update
        status The EE defined status to set the unit to
               'F' for failed
               'C' for complete
               'R' for rejected

        Returns:
        On success, a tuple (True, None, None)
        On failure, a tuple (False, failure message, failure status)
        '''

        returnval = collections.namedtuple('UpdateOrderResponse',
                                           ['success', 'message', 'status'])

        resp = self.client.factory.create('StatusOrderReturn')

        try:
            unit_number = int(unit_number)
            status = str(status)
            resp = self.client.service.setOrderStatus(
                orderNumber=str(order_number),
                systemId='EXTERNAL',
                newStatus=status,
                unitRangeBegin=unit_number,
                unitRangeEnd=unit_number)
        except Exception, e:
            raise e

        if resp.status == 'Pass':
            return returnval(success=True, message=None, status=None)
        else:
            return returnval(success=False,
                             message=resp.message,
                             status=resp.status)


class OrderDeliveryServiceClient(LTASoapService):
    '''EE SOAP Service client to find orders for ESPA which originated in EE'''

    service_name = 'orderdelivery'

    def __init__(self, *args, **kwargs):
        super(OrderDeliveryServiceClient, self).__init__(*args, **kwargs)

    def get_available_orders(self):
        ''' Returns all the orders that were submitted for ESPA through EE

        Returns:
        A dictionary of lists that contain dictionaries

        response[ordernumber, email, contactid] = [
            {'sceneid':orderingId, 'unit_num':unitNbr},
            {...}
        ]
        '''
        rtn = dict()
        resp = self.client.factory.create("getAvailableOrdersResponse")

        try:
            resp = self.client.service.getAvailableOrders("ESPA")
        except Exception, e:
            raise e

        #if there were none just return
        if len(resp.units) == 0:
            return rtn

        #return these to the caller.
        for u in resp.units.unit:

            #ignore anything that is not for us
            if str(u.productCode).lower() not in ('sr01', 'sr02', 'sr03'):

                logger.warn('{0} is not an ESPA product. Order[{1}] Unit[{2}]'
                            'Product code[{3}]... ignoring'
                             .format(u.orderingId, u.orderNbr,
                                     u.unitNbr, u.productCode))
                continue

            # get the processing parameters
            pp = u.processingParam

            try:
                email = pp[pp.index("<email>") + 7:pp.index("</email>")]
            except:
                logger.warn('Could not find an email address for '
                            'unit {0} in order {1] : rejecting'
                            .format(u.unitNbr,u.orderNbr))

                # we didn't get an email... fail the order
                resp = OrderUpdateServiceClient().update_order(u.orderNbr,
                                                               u.unitNbr,
                                                               "R")
                # we didn't get a response from the service
                if not resp.success:
                    raise Exception('Could not update order[{0}] unit[{1}] '
                                    'to status:F. Error message:{2} '
                                    'Error status code:{3}'
                                    .format(u.orderNbr,
                                            u.unitNbr,
                                            resp.message,
                                            resp.status))
                else:
                    continue

            try:
                # get the contact id
                cid = pp[pp.index("<contactid>") + 11:pp.index("</contactid>")]
            except:
                logger.warn('Could not find a contactid for unit {0} in '
                            'order {1}... rejecting'
                            .format(u.unitNbr, u.orderNbr))

                # didn't get an email... fail the order
                resp = OrderUpdateServiceClient().update_order(u.orderNbr,
                                                               u.unitNbr,
                                                               "R")
                # didn't get a response from the service
                if not resp.success:
                    raise Exception('Could not update unit {0} in order {1} '
                                    'to status:F. Error message:{2} '
                                    'Error status code:{3}'
                                    .format(u.orderNbr,
                                            u.unitNbr,
                                            resp.message,
                                            resp.status))
                else:
                    continue

            # This is a dictionary that contains a list of dictionaries
            key = (str(u.orderNbr), str(email), str(cid))

            if not key in rtn:
                rtn[key] = list()

            rtn[key].append({'sceneid': str(u.orderingId),
                             'unit_num': int(u.unitNbr)}
                            )

        return rtn


''' This is the public interface that calling code should use to interact
    with this module'''


def login_user(username, password):
    return RegistrationServiceClient().login_user(username, password)


def get_user_info(username, password):
    return RegistrationServiceClient().get_user_info(username, password)


def get_user_name(contactid):
    return RegistrationServiceClient().get_username(contactid)


def verify_scenes(product_list):
    return OrderWrapperServiceClient().verify_scenes(product_list)


def input_exists(product, contact_id):
    return OrderWrapperServiceClient().input_exists(product, contact_id)


def order_scenes(product_list, contact_id, priority=5):
    return OrderWrapperServiceClient().order_scenes(product_list,
                                                    contact_id,
                                                    priority)


def get_download_urls(product_list, contact_id):
    return OrderWrapperServiceClient().get_download_urls(product_list,
                                                         contact_id)


def get_available_orders():
    return OrderDeliveryServiceClient().get_available_orders()


def get_order_status(lta_order_number):
    return OrderUpdateServiceClient().get_order_status(lta_order_number)


def update_order_status(lta_order_number, unit_number, new_status):
    return OrderUpdateServiceClient().update_order(lta_order_number,
                                                   unit_number,
                                                   new_status)
