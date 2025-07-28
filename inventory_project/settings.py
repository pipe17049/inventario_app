"""
Django settings for inventory_project project.
"""

import os
from pathlib import Path
import mongoengine
from dotenv import load_dotenv

# Load environment variables - prioritize .env.local for development
env_local_path = Path(__file__).resolve().parent.parent / '.env.local'
env_path = Path(__file__).resolve().parent.parent / '.env'

if env_local_path.exists():
    load_dotenv(env_local_path)
    print(f"Loaded environment from: {env_local_path}")
else:
    load_dotenv(env_path)
    print(f"Loaded environment from: {env_path}")

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Environment detection
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # dev, staging, prod
IS_GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'

# Allowed hosts - support GitHub Actions and different environments
if IS_GITHUB_ACTIONS:
    # In GitHub Actions, allow broader host access for testing
    if DEBUG:
        ALLOWED_HOSTS = ['*']
    else:
        hosts_env = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
        ALLOWED_HOSTS = hosts_env.split(',')
else:
    hosts_env = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
    ALLOWED_HOSTS = hosts_env.split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'inventory',  # Our main app
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventory_project.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'inventory_project.wsgi.application'

# MongoDB configuration
# Support different configurations for development, staging, and production
if IS_GITHUB_ACTIONS or ENVIRONMENT in ['staging', 'production']:
    # Use GitHub Actions secrets or production environment variables
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGODB_HOST', 'localhost'),
        'port': int(os.getenv('MONGODB_PORT', 27017)),
        'db': os.getenv('MONGODB_DB', 'inventory_db'),
        'username': os.getenv('MONGODB_USERNAME'),
        'password': os.getenv('MONGODB_PASSWORD'),
        'authentication_source': os.getenv('MONGODB_AUTH_SOURCE', 'admin'),
        # Additional production settings
        'maxPoolSize': int(os.getenv('MONGODB_MAX_POOL_SIZE', 50)),
        'minPoolSize': int(os.getenv('MONGODB_MIN_POOL_SIZE', 5)),
        'serverSelectionTimeoutMS': int(os.getenv('MONGODB_TIMEOUT', 5000)),
    }
else:
    # Local development settings
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGODB_HOST', 'localhost'),
        'port': int(os.getenv('MONGODB_PORT', 27017)),
        'db': os.getenv('MONGODB_DB', 'inventory_db'),
        'username': os.getenv('MONGODB_USERNAME'),
        'password': os.getenv('MONGODB_PASSWORD'),
        'authentication_source': 'admin',
    }

# Connect to MongoDB with error handling
try:
    mongoengine.connect(**MONGODB_SETTINGS)
    if IS_GITHUB_ACTIONS:
        print("✅ MongoDB connection established (GitHub Actions)")
    else:
        print(f"✅ MongoDB connection established ({ENVIRONMENT})")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    if not IS_GITHUB_ACTIONS:
        raise

# Database (We'll keep this for Django's internal tables)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache configuration (using dummy cache since we removed Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = DEBUG

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Cache timeout (in seconds)
CACHE_TTL = 60 * 15  # 15 minutes
