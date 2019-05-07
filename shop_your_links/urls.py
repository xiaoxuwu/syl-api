"""plot_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin
from rest_framework import routers
from rest_framework.authtoken import views as auth_views
from internal import views
from django.conf.urls import include as include_extra, url

from django.conf import settings
admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_HEADER
admin.site.index_title = settings.ADMIN_INDEX_TITLE

router = routers.DefaultRouter()
router.register(r'links', views.LinkViewSet, base_name='Links')


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/', include(router.urls)),
    path('auth/', auth_views.obtain_auth_token),
    url('jet/', include_extra('jet.urls', 'jet')),  # Django JET URLS
    url('jet/dashboard/', include_extra('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url('admin/', admin.site.urls),
]