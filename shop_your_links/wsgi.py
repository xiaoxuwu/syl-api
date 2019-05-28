"""
WSGI config for ShopYourLinks project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from shop_your_links import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_your_links.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root=settings.MEDIA_ROOT, prefix=settings.MEDIA_PREFIX, autorefresh=True)