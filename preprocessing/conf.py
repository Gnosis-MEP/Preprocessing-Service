import os

from decouple import config

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SOURCE_DIR)

RUN_PUBLISHERS_BIN = os.path.join(SOURCE_DIR, 'run_publishers.py')

REDIS_ADDRESS = config('REDIS_ADDRESS', default='localhost')
REDIS_PORT = config('REDIS_PORT', default='6379')

USER_MANAGER_STREAM_KEY = config('USER_MANAGER_STREAM_KEY', default='um-data')
USER_MANAGER_CMD_KEY = config('USER_MANAGER_CMD_KEY', default='um-cmd')

MATCHING_ENGINE_STREAM_KEY = config('MATCHING_ENGINE_STREAM_KEY', default='me-data')

PREPROCESSING_STREAM_KEY = config('PREPROCESSING_STREAM_KEY', default='pp-data')
PREPROCESSING_CMD_KEY = config('PREPROCESSING_CMD_KEY', default='pp-cmd')

LOGGING_LEVEL = config('LOGGING_LEVEL', default='ERROR')

MINIO_ACCESS_KEY = config('MINIO_ACCESS_KEY', default='somekey')
MINIO_SECRET_KEY = config('MINIO_SECRET_KEY', default='somesecret')
MINIO_ENDPOINT = config('MINIO_ENDPOINT', default='localhost:9000')
MINIO_SECURE_CONNECTION = config('MINIO_SECURE_CONNECTION', default=False, cast=bool)
