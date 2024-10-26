import json
import re

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from django_tables2 import RequestConfig
from django_tables2.export import TableExport

from .forms import NewInfoscreenContentForm
from .models import InfoscreenContent, Infoscreen
from .scheduling import schedule_content, Slide
from .tables import ContentTable, ScheduleTable


def is_mobile(request: HttpRequest) -> bool:
    """Return True if the request comes from a mobile device."""
    mobile_agent_re = re.compile(r'.*(iphone|mobile|androidtouch)',
                                 re.IGNORECASE)

    return mobile_agent_re.match(request.META['HTTP_USER_AGENT']) is not None


def index_view(request: HttpRequest) -> HttpResponse:
    show_all = request.GET.get('all')

    content = InfoscreenContent.query_all() if show_all \
        else InfoscreenContent.query_currently_displayed()

    table = ContentTable(content)
    RequestConfig(request).configure(table)

    export_format = request.GET.get('_export', None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table)
        return exporter.response("table.{}".format(export_format))

    context = {'table': table, 'show_all': show_all}
    return render(request, 'infoscreen/index_table_view.html', context)


def schedule_view(request: HttpRequest) -> HttpResponse:

    infoscreens = Infoscreen.query_all()
    tables = []

    for infoscreen in infoscreens:
        f = open(infoscreen.schedule_file)
        slides_data = json.load(f)
        schedule = [Slide.from_dict(slide_data) for slide_data in slides_data]
        table = ScheduleTable(schedule)
        RequestConfig(request).configure(table)
        tables.append({'title': infoscreen.name, 'data': table})

    # export_format = request.GET.get('_export', None)
    # if TableExport.is_valid_format(export_format):
    #     exporter = TableExport(export_format, table)
    #     return exporter.response("table.{}".format(export_format))
    context = {'tables': tables}

    return render(request, 'infoscreen/schedule_view.html', context)

@csrf_protect
@login_required
def schedule_generate(request: HttpRequest) -> HttpResponse:
    schedule_content()
    messages.add_message(
        request, messages.SUCCESS,
        gettext(
            'Schedules generated successfully.'
        ),
        'alert alert-success')
    return schedule_view(request)

@csrf_protect
@login_required
def new_content_form(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = NewInfoscreenContentForm(request.POST, request.FILES)
        form.fill_choices(request.user)
        if form.is_valid():
            return form.form_valid(request)
    else:
        form = NewInfoscreenContentForm()
        form.fill_choices(request.user)

    context = {'form': form, 'is_mobile': is_mobile(request)}
    return render(request, 'infoscreen/new_content_form.html', context)
