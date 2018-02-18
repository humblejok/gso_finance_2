'''
Created on 12 nov. 2017

@author: sdejo
'''
email_v1_mapping = { 'EMAIL_PERSONAL': 'PERSONAL', 'EMAIL_WORK': 'WORK', 'EMAIL_CONTACT': 'CONTACT', 'EMAIL_TECHNICAL': 'TECHNICAL'}
phone_v1_mapping = { 'PHONE_MOB_PERSONAL': 'PERSONAL_MOBILE', 'PHONE_MOB_WORK': 'WORK_MOBILE', 'PHONE_MOB_CONTACT': 'CONTACT_MOBILE',
                     'PHONE_LAND_PERSONAL': 'PERSONAL_LAND', 'PHONE_LAND_WORK': 'WORK_LAND','PHONE_LAND_CONTACT': 'CONTACT_LAND',
                     'PHONE_FAX_WORK': 'WORK_FAX', 'PHONE_FAX_HONE': 'PERSONAL_FAX'}
address_v1_mapping = { 'ADR_WEB': 'DEFAULT', 'ADR_HOME': 'PERSONAL', 'ADR_WORK': 'WORK', 'ADR_MAIN_OFFICE': 'MAIN', 'ADR_SUBSI_OFFICE': 'SUBSIDIARY'}

def my_class_import(name):
    components = name.split('.')
    module = __import__('.'.join(components[:(len(components)-1)]), fromlist=components[-1])
    return getattr(module,components[-1])

# FROM https://github.com/ploopkazoo/python-base64url/blob/master/base64url.py
def base64urlencode(arg):
    stripped = arg.split("=")[0]
    filtered = stripped.replace("+", "-").replace("/", "_")
    return filtered

def base64urldecode(arg):
    filtered = arg.replace("-", "+").replace("_", "/")
    padded = filtered + "=" * ((len(filtered) * -1) % 4)
    return padded

def full_setup():
    models = my_class_import('common.models')
    Security = my_class_import('security.models.Security')
    Portfolio = my_class_import('portfolio.models.Portfolio')
    models.populate_environment()
    models.Company.import_from_csv(True)
    Security.import_from_csv(True)
    Portfolio.import_from_csv(True)