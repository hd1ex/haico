import math
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
    id = 0
    number_slots: int = 1
    due_date: date = None
    ratio = 1


@dataclass
class Group:
    group_name: str
    slides: list
    slots: int


@dataclass
class Schedule:
    infoscreen: Infoscreen
    slides: list[Slide]


def schedule_content() -> list[Slide]:
    infoscreens = Infoscreen.objects.all()

    schedules = []

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
            number_slots = math.ceil(
                display_time / infoscreen.default_display_time)
            slides.append(Slide(display_time, content_piece.file_url,
                                content_piece.group,
                                content_piece.event, number_slots,
                                content_piece.valid_until))
        slides_event = [slide for slide in slides if slide.event]

        slides_regular = [slide for slide in slides if not slide.event]
        # Take care of regular slides

        # group slides by group
        groups = []
        for slide in slides_regular:
            # if group does not exist in groups[], add it
            if not any(group.group_name == slide.group for group in groups):
                groups.append(Group(slide.group, [], 0))
            # find first group in groups[] matching the name of the slide's group and append the slide to group's slides[]
            group = next(
                (group for group in groups if group.group_name == slide.group),
                None)
            group.slides.append(slide)

        max_slots = 0

        # calculate slots for each group and maxSlots
        for group in groups:
            slots = sum((slide.number_slots for slide in group.slides))
            group.slots = slots
            if slots > max_slots:
                max_slots = slots

        # shuffle slides whithin group and repeat slides to fill maxSlots
        for group in groups:
            random.shuffle(group.slides)
            if group.slots < max_slots:
                group.slides = repeat_array_to_slots(group.slides, max_slots)

        slides_regular = []
        # flatten groups to slides_regular and shuffle
        for group in groups:
            slides_regular.extend(group.slides)

        random.shuffle(slides_regular)

        # take care of event slides
        # if there are event slides, process them
        if len(slides_event) > 0:
            # sort slides by due date
            slides_event.sort(key=lambda slide: slide.due_date)
            temp_slides_event = []
            for slide in slides_event:
                days_until_event = (slide.due_date - date.today()).days
                if days_until_event <= infoscreen.ratio_4_max_days:
                    slide.ratio = 4
                elif days_until_event <= infoscreen.ratio_3_max_days:
                    slide.ratio = 3
                elif days_until_event <= infoscreen.ratio_2_max_days:
                    slide.ratio = 2
                else:
                    slide.ratio = 1
                for i in range(slide.ratio):
                    temp_slides_event.append(slide)

            slides_event = temp_slides_event

            #shuffle event slides
            random.shuffle(slides_event)


            # repeat event slides to fill length of regular slides if there are
            # less event slides than regular slides
            if sum(slide.number_slots for slide in slides_event) < len(slides_regular):

                slides_event = repeat_array_to_slots(slides_event,
                                                     len(slides_regular))

            # check if there are both event slides and regular slides
            if len(slides_event) > 0 and len(slides_regular) > 0:
                # merge regular and event slides
                slides = merge_slides_arrays(slides_regular, slides_event)
            # check if there are only event slides, then set event slides as slides
            elif len(slides_event) > 0 and len(slides_regular) == 0:
                slides = slides_event
        # otherwise set regular slides as slides (might be empty as well)
        else:
            slides = slides_regular

        # generate configs for static page generator
        relative_config_path = generate_infoscreen_config(infoscreen, slides)

        # call static page generator
        # subprocess.call([settings.STATIC_PAGE_GENERATOR_SCRIPT,
        # relative_config_path])

        schedules.append(Schedule(infoscreen, slides))

    return schedules
