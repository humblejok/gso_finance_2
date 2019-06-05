'''
Created on 04 June 2019

@author: sdejo
'''
from django.core.management.base import BaseCommand
from django.db.models import Q

from portfolio.computations import portfolios as pf_computer
from portfolio.models import Portfolio, Operation, MoneyAccountChain
from providers.models import ExternalTransaction, ExternalAccount


class Command(BaseCommand):
    help = 'Remove all sub items of a portfolio (DEBUG/TEST only)'
    
    def add_arguments(self, parser):
        parser.add_argument('portfolio_id', type=str)

    def handle(self, *args, **options):
        try:
            portfolio = Portfolio.objects.get(id=options['portfolio_id'])
        except Portfolio.DoesNotExist:
            print('Portfolio not found')
            return None
        print('WORKING ON:' + portfolio.name)
        for account in portfolio.accounts.all():
            print('\tACCOUNT:' + account.name)
            count = 0
            for operation in Operation.objects.filter(Q(source__id=account.id) | Q(target__id=account.id)):
                MoneyAccountChain.objects.filter(operation__id=operation.id).delete()
                ExternalTransaction.objects.filter(internal_operation__id=operation.id).delete()
                operation.delete()
                count = count + 1
            print('\t\tRemoved operations:' + str(count))
            e_accounts = ExternalAccount.objects.filter(associated__id=account.id)
            ExternalTransaction.objects.filter(Q(external_source__in=e_accounts) | Q(external_target__in=e_accounts)).delete()
            e_accounts.delete()
            e_accounts = ExternalAccount.objects.filter(potential_matches__id=account.id)
            ExternalTransaction.objects.filter(Q(external_source__in=e_accounts) | Q(external_target__in=e_accounts)).delete()
            e_accounts.delete()
            account.delete()
            print('\t\tAccount deleted')
        externals = ExternalTransaction.objects.filter(portfolio__id=portfolio.id)
        for external in externals:
            operation_id = external.internal_operation.id
            external.delete()
            Operation.objects.get(id=operation_id).delete()
        orphans = Operation.objects.filter(source__isnull=True, target__isnull=True)
        for orphan in orphans:
            if not ExternalTransaction.objects.filter(internal_operation__id=orphan.id).exists():
                orphan.delete()
        pf_computer.compute_accounts(portfolio)
        pf_computer.compute_valuation(portfolio)
        pf_computer.update_accounts(portfolio)
        pf_computer.update_portfolio_model(portfolio)