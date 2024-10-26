import random
from dataclasses import dataclass
from datetime import date

from haico import settings
from .models import Infoscreen, InfoscreenContent, MediaType
from .util import save_infoscreen_config, generate_static_htmls


@dataclass
class Slide:
    display_time: int
    source: str
    media_type: MediaType
    group: str
    event: bool
    due_date: date = None
    ratio: int = 1


    def to_dict(self):
        return {
            'display_time': self.display_time,
            'source': self.source,
            'group': self.group,
            'event': self.event,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'ratio': self.ratio,
            'media_type': MediaType(self.media_type)
        }

    def from_dict(self=None):
        return Slide(
            display_time=self['display_time'],
            source=self['source'],
            group=self['group'],
            event=self['event'],
            due_date=date.fromisoformat(self['due_date']) if self[
                'due_date'] else None,
            ratio= self['ratio'] if self['ratio'] else 1,
            media_type= MediaType(self['media_type']) if self['media_type'] else MediaType.HTML
        )



def schedule_content():
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
            slides.append(Slide(display_time,
                                content_piece.file_url,
                                content_piece.media_type,
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
        schedule_file_path = save_infoscreen_config(infoscreen, slides)
        print(f'Generated config file: {schedule_file_path}')
        infoscreen.schedule_url = f'{settings.BASE_URL}/{schedule_file_path}'
        infoscreen.schedule_file = schedule_file_path
        infoscreen.save()

        generate_static_htmls(infoscreen, slides)

        # call static page generator
        # subprocess.call([settings.STATIC_PAGE_GENERATOR_SCRIPT,
        # relative_config_path])
