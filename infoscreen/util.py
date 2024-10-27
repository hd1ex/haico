import datetime
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
from infoscreen.models import MediaType


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

def generate_static_htmls(infoscreen, slides):
    #delete all html files in the infoscreen folder
    dir_path = os.path.join(settings.STATIC_INFOSCREEN_ROOT,
                                 infoscreen.name)
    dir_list = os.listdir(dir_path)

    for item in dir_list:
        if item.endswith(".html"):
            os.remove(os.path.join(dir_path, item))

    # generate html files for each slide
    for index, slide in enumerate(slides):

        file_path = os.path.join(settings.STATIC_INFOSCREEN_ROOT,
                                 infoscreen.name, f'{index}.html')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        current_content = slide.source
        display_time = slide.display_time*1000
        next_url = f'{settings.BASE_URL}/{settings.STATIC_INFOSCREEN_FILES_FOLDER}/{infoscreen.name}/{(index + 1) % len(slides)}.html'
        next_file = slides[(index + 1) % len(slides)].source
        next_file_media_type = slides[(index + 1) % len(slides)].media_type

        if(next_file_media_type == MediaType.VIDEO):
            next_file_media_type = "video"
        elif (next_file_media_type == MediaType.IMAGE):
            next_file_media_type = "image"
        elif (next_file_media_type == MediaType.HTML):
            next_file_media_type = "document"



        context = {'current_content': current_content, 'display_time': display_time, 'next_url': next_url, 'next_file': next_file, 'next_file_media_type': next_file_media_type}

        #choose template depending on media type and write to file
        with open(file_path, 'w') as file:
            if slide.media_type == MediaType.HTML:
                file.write(render_to_string('infoscreen-static/website.html', context))
            elif slide.media_type == MediaType.IMAGE:
                file.write(render_to_string('infoscreen-static/image.html', context))
            elif slide.media_type == MediaType.VIDEO:
                file.write(render_to_string('infoscreen-static/video.html', context))

