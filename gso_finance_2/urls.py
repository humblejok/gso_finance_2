"""gso_finance_2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from common import views
from rest_framework import routers
from common.views import CurrencyViewSet, CompanyViewSet, QuickCurrencyViewSet,\
    CountryViewSet, QuickCountryViewSet, VisibilityLevelViewSet,\
    QuickVisibilityLevelViewSet, AddressTypeViewSet, QuickAddressTypeViewSet,\
    PhoneTypeViewSet, QuickPhoneTypeViewSet, MailTypeViewSet,\
    QuickMailTypeViewSet, PersonViewSet
from portfolio.views import PortfolioViewSet, AccountViewSet
from common.models import MailType

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


router.register(r'persons', PersonViewSet)
router.register(r'portfolios', PortfolioViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'companies', CompanyViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^index.html', views.index, name='index'),
]
