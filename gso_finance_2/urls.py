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
from common.views import CurrencyViewSet, CompanyViewSet
from portfolio.views import PortfolioViewSet, AccountViewSet

router = routers.DefaultRouter()
router.register(r'currencies', CurrencyViewSet)
router.register(r'portfolios', PortfolioViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'companies', CompanyViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^index.html', views.index, name='index'),
]
