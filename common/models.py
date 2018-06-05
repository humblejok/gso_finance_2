from django.db import models
from gso_finance_2.settings import RESOURCES_DIR

import csv
import os
from gso_finance_2.utility import my_class_import, address_v1_mapping,\
    email_v1_mapping, phone_v1_mapping
from json import loads

def populate_environment(only_model=None):
    setup_reader = csv.reader(open(os.path.join(RESOURCES_DIR,'Common Setup.csv')), delimiter=';')
    header = None
    models_dict = {}
    for row in setup_reader:
        if header==None:
            header = row
            continue
        current_model = row[header.index('model')]
        if only_model==None or only_model==current_model:
            if current_model not in models_dict:
                print("New model found:" + current_model)
                models_dict[current_model] = my_class_import(current_model)
                models_dict[current_model].objects.all().delete()
            new_instance = models_dict[current_model]()
            new_instance.identifier = row[header.index('identifier')]
            new_instance.default_name = row[header.index('default_name')]
            new_instance.quick_access = row[header.index('quick_access')].lower()=='true'
            new_instance.save()
        

##############################################################
#                  ENVIRONMENT MODELS                        #
##############################################################

class Currency(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)
    
class Country(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)

class VisibilityLevel(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)

class AddressType(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)
    
class PhoneType(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)
    
class MailType(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)
    
class CompanyMemberRole(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)
    
class CompanySubsidiaryRole(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)


##############################################################
#                       COMMON MODELS                        #
##############################################################
class Address(models.Model):
    address_type = models.ForeignKey(AddressType, related_name='address_type_rel', null=True)
    line_1 = models.CharField(max_length=128, null=True)
    line_2 = models.CharField(max_length=128, null=True)
    zip_code = models.CharField(max_length=32, null=True)
    city = models.CharField(max_length=128, null=True)
    country = models.ForeignKey(Country, related_name='address_country_rel', null=True)
    
    @staticmethod
    def instanciate_from_dict(data):
        new_instance = Address()
        for key in data:
            if key=='model':
                continue
            if key=='address_type':
                setattr(new_instance, key, AddressType.objects.get(identifier=address_v1_mapping[data[key]]))
            elif key=='country':
                setattr(new_instance, key, Country.objects.get(identifier=data[key]))
            else:
                setattr(new_instance, key, data[key])
        new_instance.save()
        return new_instance
        
    
class Email(models.Model):
    address_type = models.ForeignKey(MailType, related_name='email_type_rel', null=True)
    email_address = models.EmailField()
    
    @staticmethod
    def instanciate_from_dict(data):
        new_instance = Email()
        for key in data:
            if key=='model':
                continue
            if key=='address_type':
                setattr(new_instance, key, MailType.objects.get(identifier=email_v1_mapping[data[key]]))
            else:
                setattr(new_instance, key, data[key])
        new_instance.save()
        return new_instance
    
class Phone(models.Model):
    line_type = models.ForeignKey(PhoneType, related_name='phone_type_rel', null=True)
    phone_number = models.TextField(max_length=32)
    
    @staticmethod
    def instanciate_from_dict(data):
        new_instance = Phone()
        for key in data:
            if key=='model':
                continue
            if key=='line_type':
                setattr(new_instance, key, PhoneType.objects.get(identifier=phone_v1_mapping[data[key]]))
            else:
                setattr(new_instance, key, data[key])
        new_instance.save()
        return new_instance

class Person(models.Model):
    default_name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    birth_date = models.DateField(null=True)
    addresses = models.ManyToManyField(Address, blank=True)
    emails = models.ManyToManyField(Email, blank=True)
    phones = models.ManyToManyField(Phone, blank=True)
    active = models.BooleanField(default=True)
    picture = models.CharField(max_length=256, blank=True, null=True)
    
    @staticmethod
    def import_from_csv(clean=False):
        if clean:
            Person.objects.all().delete()
        import_reader = csv.reader(open(os.path.join(RESOURCES_DIR,'persons.csv'), encoding='utf-8'), delimiter=';')
        header = None
        print("Persons - First pass")
        for row in import_reader:
            if len(row)==0:
                continue
            if header==None:
                header = row
                continue
            print("Creating:" + row[1])
            new_person = Person()
            index = -1
            for column in header:
                index = index + 1
                if column in ['model', 'addresses', 'emails', 'phones', 'active']:
                    continue
                setattr(new_person, column, row[index].encode('utf-8') if row[index]!='' else None)
            new_person.save()
            for column in ['addresses', 'emails', 'phones']:
                all_data = loads(row[header.index(column)], encoding='utf-8')
                for data in all_data:
                    working_class = my_class_import(data['model'])
                    getattr(new_person, column).add(working_class.instanciate_from_dict(data))
            new_person.save()
    
class CompanyMember(models.Model):
    person = models.ForeignKey(Person, null=False, related_name='company_member_person_rel')
    role = models.ForeignKey(CompanyMemberRole, related_name='company_member_role_rel', null=False)
    
    @staticmethod
    def instanciate_from_dict(data):
        new_instance = CompanyMember()
        for key in data:
            if key=='model':
                continue
            if key=='role':
                setattr(new_instance, key, CompanyMemberRole.objects.get(identifier=data[key]))
            elif key=='person':
                setattr(new_instance, key, Person.objects.get(default_name=data[key]))
            else:
                setattr(new_instance, key, data[key])
        new_instance.save()
        return new_instance
    
class Company(models.Model):
    default_name = models.CharField(max_length=256)
    creation_date = models.DateField(null=True)
    base_currency = models.ForeignKey(Currency, null=True, related_name='company_currency_name')
    addresses = models.ManyToManyField(Address, blank=True)
    emails = models.ManyToManyField(Email, blank=True)
    phones = models.ManyToManyField(Phone, blank=True)
    members = models.ManyToManyField(CompanyMember, blank=True)
    subsidiaries = models.ManyToManyField('CompanySubsidiary', related_name='company_subsidiary_rel', blank=True)
    active = models.BooleanField(default=True)
    logo = models.CharField(max_length=256, blank=True, null=True)
    is_provider = models.BooleanField(default=False)
    provider_code = models.CharField(max_length=16, blank=True, null=True)
    
    @staticmethod
    def import_from_csv(clean=False):
        if clean:
            Company.objects.all().delete()
        import_reader = csv.reader(open(os.path.join(RESOURCES_DIR,'companies.csv'), encoding='utf-8'), delimiter=';')
        header = None
        print("Companies - First pass")
        for row in import_reader:
            if len(row)==0:
                continue
            if header==None:
                header = row
                continue
            print("Creating:" + row[1])
            new_company = Company()
            index = -1
            for column in header:
                index = index + 1
                if column in ['model', 'addresses', 'emails', 'phones', 'members', 'subsidiaries', 'active']:
                    continue
                elif column=='base_currency' and row[index]!='':
                    setattr(new_company, column, Currency.objects.get(identifier=row[index]))
                else:
                    setattr(new_company, column, row[index] if row[index]!='' else None)
            new_company.save()
            for column in ['addresses', 'emails', 'phones', 'members', 'subsidiaries']:
                all_data = loads(row[header.index(column)], encoding='utf-8')
                for data in all_data:
                    print(data)
                    working_class = my_class_import(data['model'])
                    getattr(new_company, column).add(working_class.instanciate_from_dict(data))
            new_company.save()
    
class CompanySubsidiary(models.Model):
    company = models.ForeignKey('Company', related_name='company_subsidiary_company_rel', null=False)
    role = models.ForeignKey(CompanySubsidiaryRole, related_name='company_subsidiary_role_rel', null=False)
    
    @staticmethod
    def instanciate_from_dict(data):
        new_instance = Phone()
        for key in data:
            if key=='model':
                continue
            if key=='role':
                setattr(new_instance, key, CompanySubsidiaryRole.objects.get(identifier=data[key]))
            elif key=='person':
                setattr(new_instance, key, Company.objects.get(default_name=data[key]))
            else:
                setattr(new_instance, key, data[key])
        new_instance.save()
        return new_instance
    