import datetime
import io
import json
import os
from io import IOBase
from pathlib import Path

from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.translation import gettext

from slugify import slugify

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

from haico import settings
from haico.settings import MAX_VIDEO_DURATION


def verify_multimedia(metadata: dict):
    width = metadata.get('width')
    height = metadata.get('height')

    target_width = settings.INFOSCREEN_TARGET_WIDTH
    target_height = settings.INFOSCREEN_TARGET_HEIGHT

    if width != target_width or height != target_height:
        raise ValidationError(gettext(
            'Your media file has the dimensions %(width)sx%(height)s. '
            'They need to be %(target_width)sx%(target_height)s.'),
            params={'width': width,
                    'height': height,
                    'target_width': target_width,
                    'target_height': target_height},
            code='mismatched_dimensions')


def verify_infoscreen_file(file: IOBase) -> str:
    file_parser = createParser(file)
    extension = getattr(file_parser, 'filename_suffix', None)
    if not file_parser or not extension:
        raise ValidationError(gettext('Unable to parse file. Is this a '
                                      'multimedia file?'))
    try:
        file_metadata = extractMetadata(file_parser)
    except Exception as err:
        raise ValidationError('Metadata extraction error: %s' % err)

    if file_metadata:
        verify_multimedia(file_metadata)
    else:
        raise ValidationError(gettext('Unsupported file type.'))

    return extension


def get_video_duration(file: IOBase) -> int:
    file_parser = createParser(file)
    if not file_parser:
        raise ValidationError(gettext('Unable to parse file. Is this a '
                                      'multimedia file?'))
    try:
        file_metadata = extractMetadata(file_parser)
    except Exception as err:
        raise ValidationError('Metadata extraction error: %s' % err)
    #extract video duration, if file is not video, set duration as None
    if file_metadata:
        try:
            duration = file_metadata.get('duration').seconds

        except Exception as err:
            duration = None
        if duration is int and duration > MAX_VIDEO_DURATION:
            raise ValidationError(gettext('Video duration exceeds the maximum allowed duration.'))

    return duration or None


def get_infoscreen_file_folder(group: str) -> str:
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    return f'{settings.INFOSCREEN_FILES_FOLDER}/{slugify(group)}/{date}/'


def save_infoscreen_file(file, title: str, group: str, extension: str) -> str:
    folder = get_infoscreen_file_folder(group)
    os.makedirs(folder, exist_ok=True)

    filename = Path(folder, slugify(title) + extension)

    i = 1
    while filename.exists():
        filename = Path(folder, f'{slugify(title)}-{i}{extension}')
        i += 1

    with open(filename, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return f'{settings.BASE_URL}/{filename}'


def save_infoscreen_config(infoscreen, slides) -> str:
    schedule_text = json.dumps([slide.to_dict() for slide in slides], indent=4)
    file_path = os.path.join(settings.STATIC_INFOSCREEN_ROOT,
                             infoscreen.name, 'schedule.json')

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as file:
        file.write(schedule_text)
    return file_path
