from io import BytesIO
from PIL import Image
import sys
import tinify

from django.conf import settings

from .fields import OptimizedImageField


def optimize_from_buffer(data):
    """Optimize an image that has not been saved to a file."""
    if not is_testing_mode():
        if settings.OPTIMIZED_IMAGE_METHOD == 'pillow':
            image = Image.open(data)
            bytes_io = BytesIO()
            if data.name.split('.')[-1].lower() != 'jpg':
                extension = data.name.split('.')[-1].upper()
            else:
                extension = 'JPEG'
            image.save(bytes_io, format=extension, optimize=True)
            data.seek(0)
            data.file.write(bytes_io.getvalue())
            data.file.truncate()
        elif settings.OPTIMIZED_IMAGE_METHOD == 'tinypng':
            tinify.key = settings.TINYPNG_KEY
            optimized_buffer = tinify.from_buffer(data.file.read()).to_buffer()
            data.seek(0)
            data.file.write(optimized_buffer)
            data.file.truncate()
    return data


def optimize_legacy_images_in_model_fields(list_of_models, verbosity=0):
    """
    Call this function to go through models and optimize images.

    This is best done after changing your model fields from ImageField to
    OptimizedImageField, and migrating the models. This function goes through
    the list_of_models in the params, finds all of their OptimizedImageFields,
    and optimizes the images in those fields. Note: there is a 500 image/month
    limit on a free TinyPNG API key, so use this function wisely.
    """
    for model in list_of_models:
        if verbosity == 1:
            sys.stdout.write('\nOptimizing for model: {}'.format(model))

        field_names_to_optimize = []
        for field in model._meta.get_fields():
            if type(field) == OptimizedImageField:
                field_names_to_optimize.append(field.attname)

        if verbosity == 1:
            sys.stdout.write('\nWill check the following fields: {}'.format(field_names_to_optimize))

        model_instances = model.objects.all()
        for model_instance in model_instances:
            for field_name in field_names_to_optimize:
                if verbosity == 1:
                    sys.stdout.write('\nChecking for instance id {} field {}'.format(model_instance.pk, field_name))

                # If the instance's field has an image, optimize it
                image_file = getattr(model_instance, field_name)
                if image_file.name not in [None, '']:
                    if verbosity == 1:
                        sys.stdout.write('\nImage found. Optimizing.')

                    if verbosity == 1:
                        sys.stdout.write('\nOptimized and saved image.')


def is_testing_mode():
    """Return True if currently running tests."""
    return True if 'test' in sys.argv else False
