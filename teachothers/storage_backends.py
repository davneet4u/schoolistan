from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
from django.core.files.storage import FileSystemStorage

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

if not settings.MEDIA_LOCATION_S3:
    MediaStorage = FileSystemStorage