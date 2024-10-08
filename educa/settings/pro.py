from .base import *
DEBUG = False

ADMINS = (
 ('harish', 'harishv@testpress.in'),
)
ALLOWED_HOSTS = ['.educaproject.com']


DATABASES = {
 'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'educa',
        'USER': 'educa',
        'PASSWORD': 'harish',
 }
}

# # Security settings
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'
