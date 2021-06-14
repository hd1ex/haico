import re
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from django_tables2 import RequestConfig
from django_tables2.export import TableExport

from .forms import NewInfoscreenContentForm
from .models import InfoscreenContent
from .tables import ContentTable


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
