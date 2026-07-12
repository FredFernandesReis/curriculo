"""
Configurações do projeto Currículo PRO.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega .env se existir (produção / local)
env_file = BASE_DIR / '.env'
if env_file.exists():
    try:
        from decouple import Config, RepositoryEnv
        _config = Config(RepositoryEnv(str(env_file)))

        def env(key, default=None):
            return _config(key, default=default)
    except Exception:
        def env(key, default=None):
            return os.environ.get(key, default)
else:
    def env(key, default=None):
        return os.environ.get(key, default)

SECRET_KEY = env(
    'SECRET_KEY',
    'django-insecure-sxf0k3m&20d2ijnqo4(7zgn_%54ee4h9c%k!+i61f^h*y!rgdu',
)

DEBUG = str(env('DEBUG', 'True')).lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = [
    h.strip()
    for h in str(env(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1,.ngrok-free.app,.ngrok.io,.ngrok.app',
    )).split(',')
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in str(env('CSRF_TRUSTED_ORIGINS', '')).split(',')
    if origin.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'accounts',
    'clientes',
    'curriculos',
    'dashboard',
    'pdf_generator',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'core.middleware.NgrokCsrfMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Banco de dados: SQLite em dev, PostgreSQL em produção (DATABASE_URL)
DATABASE_URL = env('DATABASE_URL', '')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'core:home'

# WhatsApp
WHATSAPP_NUMBER = env('WHATSAPP_NUMBER', '5531988702824')
WHATSAPP_ADMIN_NUMBER = env('WHATSAPP_ADMIN_NUMBER', WHATSAPP_NUMBER)
WHATSAPP_DISPLAY = env('WHATSAPP_DISPLAY', '(31) 98870-2824')

# Valor do currículo (para dashboard)
try:
    CURRICULO_PRECO = float(env('CURRICULO_PRECO', '29.90'))
except (TypeError, ValueError):
    CURRICULO_PRECO = 29.90

# Sessão para auto-save do formulário
SESSION_COOKIE_AGE = 86400 * 7  # 7 dias

# Segurança em produção
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
