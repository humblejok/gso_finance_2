from django.conf.urls import url, include
from django.contrib import admin

from authentication import views as userAuth
from common import views
from rest_framework import routers
from common.views import CurrencyViewSet, CompanyViewSet, QuickCurrencyViewSet,\
    CountryViewSet, QuickCountryViewSet, VisibilityLevelViewSet,\
    QuickVisibilityLevelViewSet, AddressTypeViewSet, QuickAddressTypeViewSet,\
    PhoneTypeViewSet, QuickPhoneTypeViewSet, MailTypeViewSet,\
    QuickMailTypeViewSet, PersonViewSet, ProviderSearch
from portfolio.views import PortfolioViewSet, AccountViewSet, AccountOperations,\
    AccountTypeViewSet, QuickAccountTypeViewSet,\
    QuickFinancialOperationTypeViewSet, FinancialOperationTypeViewSet,\
    OperationStatusViewSet, QuickOperationStatusViewSet, portfolios_history
from providers.views import ExternalSecurityViewSet, ExternalSecuritySearch,\
    ExternalSecurityUnmapped, external_securities_history
from security.views import SecurityViewSet, securities_history,\
     SecuritiesSearch, SecurityTypeViewSet, QuickSecurityTypeViewSet

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

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^index.html', views.index, name='index'),
    url(r'^login/', userAuth.UserLogin.as_view(), name='login'),
    url(r'^login/test', userAuth.UserLoginTest.as_view(), name='logtest'),

    url(r'^external_securities_search/(?P<provider_code>.+)/(?P<provider_identifier>.+)/$', ExternalSecuritySearch.as_view()),
    url(r'^external_securities_unmapped/$', ExternalSecurityUnmapped.as_view()),
    url(r'^external_securities_history/(?P<external_security_id>[0-9]+)/$', external_securities_history),

    url(r'^securities_history/(?P<security_id>[0-9]+)/$', securities_history),
    url(r'^securities_search/(?P<search_filter>.+)/$', SecuritiesSearch.as_view()),

    url(r'^account_operations/(?P<account_id>[0-9]+)/$', AccountOperations.as_view()),
    #url(r'^portfolio_holdings/(?P<portfolio_id>[0-9]+)/$', PortfolioHoldings.as_view()),

    url(r'^providers_search/(?P<provider_code>.+)/$', ProviderSearch.as_view()),
    
    url(r'^portfolios_history/(?P<portfolio_id>[0-9]+)/(?P<data_type>.+)/$', portfolios_history),    
]
