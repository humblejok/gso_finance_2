from django.conf.urls import url, include
from rest_framework import routers
from common.views import CurrencyViewSet, CompanyViewSet, QuickCurrencyViewSet,\
    CountryViewSet, QuickCountryViewSet, VisibilityLevelViewSet,\
    QuickVisibilityLevelViewSet, AddressTypeViewSet, QuickAddressTypeViewSet,\
    PhoneTypeViewSet, QuickPhoneTypeViewSet, MailTypeViewSet,\
    QuickMailTypeViewSet, PersonViewSet, ProviderSearch, CompaniesSearch, whoami
from portfolio.views import PortfolioViewSet, AccountViewSet, AccountOperations,\
    AccountTypeViewSet, QuickAccountTypeViewSet,\
    QuickFinancialOperationTypeViewSet, FinancialOperationTypeViewSet,\
    OperationStatusViewSet, QuickOperationStatusViewSet, portfolios_history,\
    portfolios_setup, portfolio_compute, \
    portfolio_security_operations, portfolio_initialize,\
    portfolio_import_history, portfolio_transactions_external_pending,\
    portfolio_holdings_securities, portfolio_holdings_accounts
from providers.views import ExternalSecurityViewSet, ExternalSecuritySearch,\
    ExternalSecurityUnmapped, external_securities_history,\
    ExternalAccountViewSet, ExternalPortfolioHoldingsViewSet
from security.views import SecurityViewSet, securities_history,\
     SecuritiesSearch, SecurityTypeViewSet, QuickSecurityTypeViewSet,\
    securities_statistics
from authentication import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from portfolio.views_account import accounts_create_or_update

router = routers.DefaultRouter()
router.register(r'currencies', CurrencyViewSet)
router.register(r'quick_currencies', QuickCurrencyViewSet)

router.register(r'countries', CountryViewSet)
router.register(r'quick_countries', QuickCountryViewSet)

router.register(r'visibility_levels', VisibilityLevelViewSet)
router.register(r'quick_visibility_levels', QuickVisibilityLevelViewSet)

router.register(r'address_types', AddressTypeViewSet)
router.register(r'quick_address_types', QuickAddressTypeViewSet)

router.register(r'phone_types', PhoneTypeViewSet)
router.register(r'quick_phone_types', QuickPhoneTypeViewSet)

router.register(r'mail_types', MailTypeViewSet)
router.register(r'quick_mail_types', QuickMailTypeViewSet)

router.register(r'security_types', SecurityTypeViewSet)
router.register(r'quick_security_types', QuickSecurityTypeViewSet)

router.register(r'account_types', AccountTypeViewSet)
router.register(r'quick_account_types', QuickAccountTypeViewSet)

router.register(r'operation_statuses', OperationStatusViewSet)
router.register(r'quick_operation_statuses', QuickOperationStatusViewSet)

router.register(r'financial_operation_types', FinancialOperationTypeViewSet)
router.register(r'quick_financial_operation_types', QuickFinancialOperationTypeViewSet)


router.register(r'persons', PersonViewSet)
router.register(r'portfolios', PortfolioViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'companies', CompanyViewSet)

router.register(r'securities', SecurityViewSet)

router.register(r'external_securities', ExternalSecurityViewSet)
router.register(r'external_accounts', ExternalAccountViewSet)
router.register(r'external_portfolio_holdings', ExternalPortfolioHoldingsViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^whoami/$', whoami),
    url(r'^login/', auth_views.UserLogin.as_view(), name='login'),
    url(r'^api/token/', TokenObtainPairView.as_view()),
    url(r'^api/refresh/', TokenRefreshView.as_view()),

    url(r'^external_securities_search/(?P<provider_code>.+)/(?P<provider_identifier>.+)/$', ExternalSecuritySearch.as_view()),
    url(r'^external_securities_unmapped/$', ExternalSecurityUnmapped.as_view()),
    url(r'^external_securities_history/(?P<external_security_id>[0-9]+)/$', external_securities_history),

    url(r'^securities_history/(?P<security_id>[0-9]+)/$', securities_history),
    url(r'^securities_statistics/(?P<security_id>[0-9]+)/$', securities_statistics),    
    url(r'^securities_search/(?P<search_filter>.+)/$', SecuritiesSearch.as_view()),
    
    
    url(r'^companies_search/(?P<search_filter>.+)/$', CompaniesSearch.as_view()),

    url(r'^account_operations/(?P<account_id>[0-9]+)/$', AccountOperations.as_view()),
    url(r'^portfolio/(?P<portfolio_id>[0-9]+)/holdings/securities/$', portfolio_holdings_securities),
    url(r'^portfolio/(?P<portfolio_id>[0-9]+)/holdings/accounts/$', portfolio_holdings_accounts),
    

    url(r'^providers_search/(?P<provider_code>.+)/$', ProviderSearch.as_view()),
    url(r'^portfolio/compute/(?P<portfolio_id>[0-9]+)/$', portfolio_compute),
    url(r'^portfolio/security/operations/(?P<portfolio_id>[0-9]+)/(?P<account_id>[0-9]+)/(?P<security_id>[0-9]+)/$', portfolio_security_operations),
    url(r'^portfolio/valuation/initialize/(?P<portfolio_identifier>.+)/(?P<as_of>.+)/$', portfolio_initialize),
    url(r'^portfolio/valuation/history/(?P<portfolio_identifier>.+)/$', portfolio_import_history),
    url(r'^portfolio/transactions/external/pending/(?P<portfolio_id>.+)/$', portfolio_transactions_external_pending),
    
    url(r'^portfolio/(?P<portfolio_identifier>.+)/accounts/$', accounts_create_or_update),
    
    
    url(r'^portfolios_history/(?P<portfolio_id>[0-9]+)/(?P<data_type>.+)/$', portfolios_history),
    url(r'^portfolios_setup/$', portfolios_setup),
    
    url(r'^eamcom/', include('eamcom.urls')),
    url(r'^providers/', include('providers.urls')),

    
]
