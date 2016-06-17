updict = dict()

ee_keys_to_update = ['url.tst.earthexplorer',
                     'url.tst.forgot_login',
                     'url.tst.register_user']

edc_keys_to_update = ['url.tst.massloader',
                      'url.tst.orderdelivery',
                      'url.tst.orderservice',
                      'url.tst.orderupdate',
                      'url.tst.registration']

#replace_dict = {'eedevmast': 'earthexplorer', 'edclxs152'}


base_sql = "update ordering_configuration "\
      "set value = replace(value, '{0}', '{1}') "\
      "where key = '{2}';"


for item in ee_keys_to_update:
  print base_sql.format('earthexplorer', 'eedevmast.cr', item)


for item in edc_keys_to_update:
  print base_sql.format('edclxs152', 'eedevmast', item)


servd = {'url.tst.massloader': {'from':'MassLoader', 'to': 'MassLoaderdevmast'},
 'url.tst.orderdelivery': {'from':'OrderDeliveryService', 'to':'OrderDeliveryServicedevmast'},
 'url.tst.orderservice': {'from':'OrderWrapperService', 'to':'OrderWrapperServicedevmast'},
 'url.tst.orderupdate': {'from':'OrderStatusService', 'to':'OrderStatusServicedevmast'},
 'url.tst.registration': {'from':'RegistrationService', 'to':'RegistrationServicedevmast'}}

for item in servd:
    print base_sql.format(servd[item]['from'], servd[item]['to'], item)

servd2 = {'url.tst.massloader': {'from':'MassLoader', 'to': 'MassLoaderdevmast'},
 'url.tst.orderdelivery': {'from':'OrderDeliveryService', 'to':'OrderDeliveryServicedevmast'},
 'url.tst.orderservice': {'from':'OrderWrapperService', 'to':'OrderWrapperServicedevmast'},
 'url.tst.orderupdate': {'from':'OrderStatusService', 'to':'OrderStatusServicedevmast'},
 'url.tst.registration': {'from':'RegistrationService', 'to':'RegistrationServicedevmast'}}




