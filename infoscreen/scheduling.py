import random
import subprocess
from dataclasses import dataclass
from datetime import date

from haico import settings
from .models import Infoscreen, InfoscreenContent
from .util import repeat_array_to_slots, \
    merge_slides_arrays, generate_infoscreen_config


@dataclass
class Slide:
    display_time: int
    source: str
    group: str
    event: bool
    due_date: date = None
    ratio: int = 1


@dataclass
class Group:
    group_name: str
    slides: list
    slots: int




def schedule_content() -> list[Slide]:
    infoscreens = Infoscreen.objects.all()

    for infoscreen in infoscreens:

        if infoscreen.overwritten_by:
            content = (InfoscreenContent.query_currently_displayed()
                       .filter(screens=infoscreen.overwritten_by))
        else:
            content = (InfoscreenContent.query_currently_displayed()
                       .filter(screens=infoscreen))
        slides = []
        for content_piece in content:
            display_time = content_piece.video_duration or infoscreen.default_display_time
            slides.append(Slide(display_time, content_piece.file_url,
                                content_piece.group.name,
                                content_piece.event,
                                content_piece.valid_until))
        slides_event = [slide for slide in slides if slide.event]

        slides_regular = [slide for slide in slides if not slide.event]

        # take care of event slides
        # if there are event slides, process them
        if len(slides_event) > 0:
            # sort slides by due date
            temp_slides_event = []
            for slide in slides_event:
                days_until_event = (slide.due_date - date.today()).days
                if days_until_event <= infoscreen.ratio_3_max_days:
                    slide.ratio = 3
                elif days_until_event <= infoscreen.ratio_2_max_days:
                    slide.ratio = 2
                else:
                    slide.ratio = 1
                for i in range(slide.ratio):
                    temp_slides_event.append(slide)

            slides_event = temp_slides_event

        slides = slides_regular + slides_event

        #shuffle slides
        random.shuffle(slides)

        # generate configs for static page generator
        config_file_path = save_infoscreen_config(infoscreen, slides)
        print(f'Generated config file: {config_file_path}')
        infoscreen.config_url = f'{settings.BASE_URL}/{config_file_path}'
        infoscreen.config_file = config_file_path
        infoscreen.save()

        # call static page generator
        # subprocess.call([settings.STATIC_PAGE_GENERATOR_SCRIPT,
        # relative_config_path])

        schedules.append(Schedule(infoscreen, slides))

    return schedules
