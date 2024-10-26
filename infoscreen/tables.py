import django_tables2 as tables
from django.utils.html import format_html

from infoscreen.models import InfoscreenContent


class TitleFileLinkColumn(tables.Column):
    def render(self, record):
        return format_html('<a href ="{}">{}</a>',
                           record.file_url,
                           record.title)

    def value(self, record):
        return record.title


class ContentTable(tables.Table):
    title = TitleFileLinkColumn()
    valid_from = tables.DateColumn(visible=False)
    valid_until = tables.DateColumn(visible=False)
    file_url = tables.URLColumn(visible=False)

    class Meta:
        model = InfoscreenContent
        fields = ('title', 'group', 'screens', 'submission_time', 'file_url')
        attrs = {'class': 'table table-striped'}
        order_by = '-submission_time'


class ScheduleTable(tables.Table):
    display_time = tables.Column()
    group = tables.Column()
    event = tables.Column()
    ratio = tables.Column()
    due_date = tables.DateColumn()
    source = tables.Column()
    media_type = tables.Column()

    class Meta:
        fields = (
        'display_time', 'group', 'event', 'ratio', 'source',
        'due_date', 'media_type')
        attrs = {'class': 'table table-striped'}
