"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from django.core.management.utils import get_random_secret_key
from main.encryption import get_encryption_key
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

# Build base and root directory paths for Django project (main)
BASE_DIR = Path(__file__).resolve().parent.parent

# Get server IP from environment
SERVER_IP = os.environ.get("IP_SERVER")
if not SERVER_IP:
    logger.warning("IP_SERVER environment variable not set, using fallback 'localhost'")
    SERVER_IP = "localhost"

# Basic project configuration
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    logger.warning("DJANGO_SECRET_KEY environment variable not set, generating random key (not suitable for production)")
    SECRET_KEY = get_random_secret_key()

DEBUG_STR = os.environ.get("DEBUG")
if DEBUG_STR:
    DEBUG = DEBUG_STR == "True"
else:
    logger.warning("DEBUG environment variable not set, using fallback 'False' (production mode)")
    DEBUG = False

if DEBUG:
    ALLOWED_HOSTS = ["*"]
    CORS_ALLOW_ALL_ORIGINS = True
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
    CORS_ALLOW_ALL_ORIGINS = False

# Define installed applications in the project
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "authentication",
    "authentication.fortytwo_auth",
    "channels",
    "chat",
    "tournament",
    "corsheaders",
    "game",
    "dashboard",
]

# Middleware configuration (intermediaries through which requests pass between client and application)
# Middleware executes in top-down order and is defined by default in Django
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Security middleware
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware
    "django.middleware.common.CommonMiddleware",  # Common middleware (for cookie handling)
    "django.middleware.csrf.CsrfViewMiddleware",  # CSRF protection middleware
    "django.contrib.sessions.middleware.SessionMiddleware",  # Session handling middleware
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # User authentication middleware
    "django.contrib.messages.middleware.MessageMiddleware",  # Message handling middleware
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Clickjacking protection middleware
    'authentication.middleware.UserSessionMiddleware',  # User activity tracking middleware
]

# CORS and Security configuration
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOWED_ORIGINS = [
    f"https://{SERVER_IP}:8445",
    f"https://{SERVER_IP}:8443",
    f"http://{SERVER_IP}:3000",
]
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS + [
    f"http://{SERVER_IP}:8082",
    f"ws://{SERVER_IP}:8000",
    f"wss://{SERVER_IP}:8445",
]

# Template and static files configuration
ROOT_URLCONF = "main.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "authentication/web/templates")
        ],  # Custom template directory (development)
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ASGI = Asynchronous Server Gateway Interface
# It is a specification for communication between web servers and web applications or web application frameworks
ASGI_APPLICATION = "main.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE"),
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("SQL_HOST"),
        "PORT": os.environ.get("SQL_PORT"),
        "OPTIONS": {
            # SSL/TLS configuration for PostgreSQL database
            "sslmode": "require",  # require because we are using SSL/TLS auto signed certificates
            "application_name": "django_app",
            "connect_timeout": 30,
        }
    }
}

# Validate critical database settings
for key in ["ENGINE", "NAME", "USER", "PASSWORD", "HOST", "PORT"]:
    if not DATABASES["default"][key]:
        if key in ["ENGINE", "NAME", "USER", "HOST", "PORT"]:
            logger.critical(f"Missing critical database setting: {key}")
            raise ValueError(f"Database configuration error: {key} environment variable not set")
        else:
            logger.warning(f"Database setting {key} not provided")

# Password validation for users (secure passwords)
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },  # Validate that the password is not similar to user attributes
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },  # Validate that the password has a minimum length
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },  # Validate that the password is not a common password
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },  # Validate that the password contains at least one digit
]

# Internationalization and time zone settings
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# GDPR and Inactivity Settings
TEST_MODE = 'False'  # Set to 'True' for testing, 'False' for production
TIME_MULTIPLIER = 86400  # 86400 for production (days)

# Safety margins for time checks (in seconds)
SAFETY_MARGIN = 2 if TEST_MODE else 300  # 2 seconds in test mode, 5 minutes in production

if TEST_MODE == 'True':	# Test mode (seconds)
    EMAIL_VERIFICATION_TIMEOUT = 10        
    INACTIVITY_WARNING = 40            
    INACTIVITY_THRESHOLD = 60          
    TASK_CHECK_INTERVAL = 5 # every 5 seconds it will check for inactive users            
    SESSION_ACTIVITY_CHECK = 2           
else:	# Production mode
    EMAIL_VERIFICATION_TIMEOUT = 600 # 10 minutes
    INACTIVITY_WARNING = 53 * TIME_MULTIPLIER # 53 days
    INACTIVITY_THRESHOLD = 60 * TIME_MULTIPLIER # 60 days
    TASK_CHECK_INTERVAL = 600  # 10 minutes (Celery)
    SESSION_ACTIVITY_CHECK = 300 # 5 minutes (middleware)

# Session settings for user activity tracking (middleware)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = INACTIVITY_THRESHOLD * 2  # Double the inactivity threshold

# Celery Configuration
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery configuration for handling connection retries
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
CELERY_WORKER_ENABLE_REMOTE_CONTROL = False
CELERY_WORKER_SEND_TASK_EVENTS = False

# Celery security configuration
CELERY_SECURITY_CONFIG = {
    'C_FORCE_ROOT': True,
}

# Worker configuration
CELERY_WORKER_CONFIG = {
    'worker_hijack_root_logger': False,
    'worker_max_tasks_per_child': 50,
    'worker_prefetch_multiplier': 1,
    'task_track_started': True,
    'worker_log_format': '[%(asctime)s: %(levelname)s] %(message)s',
    'worker_task_log_format': '[%(asctime)s: %(levelname)s] %(task_name)s - %(message)s',
    'worker_redirect_stdouts_level': 'ERROR',
}

# Beat configuration for periodic tasks
CELERY_BEAT_CONFIG = {
    'scheduler': 'django_celery_beat.schedulers:DatabaseScheduler',
    'max_interval': 300,  # 5 minutes
    'loglevel': 'WARNING',
}

# Celery periodic tasks configuration
CELERY_BEAT_SCHEDULE = {
    'cleanup-inactive-users': {
        'task': 'authentication.tasks.cleanup_inactive_users',
        'schedule': TASK_CHECK_INTERVAL,
    },
}

# Encryption key settings for GDPR compliance
ENCRYPTION_KEY = get_encryption_key()

# Static and media files (profile images)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
FILE_UPLOAD_PERMISSIONS = 0o644

# Static files configuration
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static_custom"),
]

# Eliminar o simplificar a solo Django admin
STATICFILES_APPS_ORDER = [
    'django.contrib.admin',
]

# Custom authentication configuration with CustomUser model defined in authentication.models
# We use CustomUser model instead of Django's default user model because we've added additional fields
# and modified authentication behavior to allow login with 42 or email
AUTH_USER_MODEL = "authentication.CustomUser"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "user"
LOGOUT_REDIRECT_URL = "login"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Environment variables for 42 authentication
FORTYTWO_CLIENT_ID = os.environ.get("FORTYTWO_CLIENT_ID")
if not FORTYTWO_CLIENT_ID:
    logger.warning("FORTYTWO_CLIENT_ID environment variable not set, OAuth authentication will not work")

FORTYTWO_CLIENT_SECRET = os.environ.get("FORTYTWO_CLIENT_SECRET")
if not FORTYTWO_CLIENT_SECRET:
    logger.warning("FORTYTWO_CLIENT_SECRET environment variable not set, OAuth authentication will not work")

FORTYTWO_REDIRECT_URI = os.environ.get("FORTYTWO_REDIRECT_URI")
if not FORTYTWO_REDIRECT_URI:
    logger.warning("FORTYTWO_REDIRECT_URI environment variable not set, OAuth authentication will not work")

FORTYTWO_API_UID = os.environ.get("FORTYTWO_API_UID")
if not FORTYTWO_API_UID:
    logger.warning("FORTYTWO_API_UID environment variable not set, OAuth API will not work")

FORTYTWO_API_SECRET = os.environ.get("FORTYTWO_API_SECRET") 
if not FORTYTWO_API_SECRET:
    logger.warning("FORTYTWO_API_SECRET environment variable not set, OAuth API will not work")

FORTYTWO_API_URL = os.environ.get("FORTYTWO_API_URL")
if not FORTYTWO_API_URL:
    logger.warning("FORTYTWO_API_URL environment variable not set, OAuth API will not work")

# Environment variables for sending emails (SMTP)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # Use this backend to print emails in the console
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'		# Use this backend to send real emails
EMAIL_HOST = os.environ.get("EMAIL_HOST")
if not EMAIL_HOST:
    logger.warning("EMAIL_HOST environment variable not set, email sending will not work")

EMAIL_PORT_STR = os.environ.get("EMAIL_PORT")
if EMAIL_PORT_STR:
    EMAIL_PORT = int(EMAIL_PORT_STR)
else:
    logger.warning("EMAIL_PORT environment variable not set, using fallback port 587")
    EMAIL_PORT = 587

EMAIL_USE_TLS_STR = os.environ.get("EMAIL_USE_TLS")
if EMAIL_USE_TLS_STR:
    EMAIL_USE_TLS = EMAIL_USE_TLS_STR == "True"
else:
    logger.warning("EMAIL_USE_TLS environment variable not set, using fallback 'True'")
    EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
if not EMAIL_HOST_USER:
    logger.warning("EMAIL_HOST_USER environment variable not set, email sending will not work")

EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
if not EMAIL_HOST_PASSWORD:
    logger.warning("EMAIL_HOST_PASSWORD environment variable not set, email sending will not work")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
if not DEFAULT_FROM_EMAIL:
    logger.warning("DEFAULT_FROM_EMAIL environment variable not set, email sending may not work correctly")

# Frontend settings
FRONTEND_URL = f"https://{SERVER_IP}:8445"
SITE_URL = FRONTEND_URL
EMAIL_VERIFICATION_URL = f"{FRONTEND_URL}/verify-email"

# Security settings
SECURE_BROWSER_XSS_FILTER = True
PASSWORD_RESET_TIMEOUT = 300
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# JWT token generation settings
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    logger.critical("JWT_SECRET_KEY environment variable not set - this is critical for security!")
    raise ValueError("JWT_SECRET_KEY must be set in production")

JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
if not JWT_ALGORITHM:
    logger.warning("JWT_ALGORITHM environment variable not set, using fallback 'HS256'")
    JWT_ALGORITHM = "HS256"

JWT_EXPIRATION_TIME_STR = os.environ.get("JWT_EXPIRATION_TIME")
if JWT_EXPIRATION_TIME_STR:
    JWT_EXPIRATION_TIME = int(JWT_EXPIRATION_TIME_STR)
else:
    logger.warning("JWT_EXPIRATION_TIME environment variable not set, using fallback '3600'")
    JWT_EXPIRATION_TIME = 3600

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "main.vault": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
