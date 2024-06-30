from datetime import datetime
from smtplib import SMTPException

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.db import OperationalError
from django.utils import translation
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy, gettext

from haico import settings
from haico.util import send_email_to_staff

from . import util
from .models import Infoscreen, InfoscreenContent
from .scheduling import schedule_content
from .util import verify_infoscreen_file, get_video_duration


class DateInput(forms.DateInput):
    input_type = 'date'


def get_infoscreen_count() -> int:
    try:
        return Infoscreen.objects.all().count()
    except OperationalError:
        # Gets raised, when database does not exist (e.g. before migration)
        return 5


class NewInfoscreenContentForm(forms.Form):
    file = forms.FileField(label=gettext_lazy('File'))
    title = forms.CharField(max_length=60, label=gettext_lazy('File title'))
    group = forms.ModelChoiceField(Group.objects,
                                   empty_label='Test',
                                   label=gettext_lazy('Associated group'))
    valid_from = forms.DateField(widget=DateInput,
                                 required=False,
                                 label=gettext_lazy('Valid from'))
    valid_until = forms.DateField(widget=DateInput,
                                  required=False,
                                  label=gettext_lazy('Valid until'))
    event = forms.BooleanField(widget=forms.CheckboxInput,
                               required=False,
                               initial=False,
                               label=gettext_lazy('Event'))
    screens = forms.ModelMultipleChoiceField(
        Infoscreen.objects,
        initial=Infoscreen.objects.all,
        label=gettext_lazy('Targeted infoscreens'),
        widget=forms.SelectMultiple(
            attrs={'class': 'select-checkbox',
                   'size': get_infoscreen_count()}))
    helper = FormHelper()

    def fill_choices(self, user: User):
        groups = [('', gettext_lazy('Choose a group'))] \
                 + [(g.id, str(g)) for g in user.groups.all()]
        if(user.is_staff):
            screens = [(g.id, str(g)) for g in Infoscreen.objects.all()]
        else:
            screens = [(g.id, str(g)) for g in Infoscreen.objects.all().filter(admin_upload_only=False)]
        self.fields['group'].choices = groups
        self.fields['screens'].choices = screens

    def clean_file(self):
        """
        This method does file validation.
        """
        self.file_extension = verify_infoscreen_file(self.cleaned_data['file'])
        self.video_duration = get_video_duration(
            self.cleaned_data['file']) or 0

    def form_valid(self, request: HttpRequest) -> HttpResponse:
        """
        This method is called when valid form data has been POSTed.
        """

        title = self.cleaned_data['title']
        group = self.cleaned_data['group']
        valid_from = self.cleaned_data['valid_from']
        valid_until = self.cleaned_data['valid_until']
        screens = self.cleaned_data['screens']
        extension = self.file_extension
        user = request.user
        video_duration = self.video_duration
        event = self.cleaned_data['event']

        url = util.save_infoscreen_file(self.files['file'], title,
                                        str(group), extension)

        content = InfoscreenContent(file_url=url,
                                    title=title,
                                    group=group,
                                    valid_from=valid_from,
                                    valid_until=valid_until,
                                    submitter=user,
                                    submission_time=datetime.now(),
                                    video_duration=video_duration,
                                    event=event
                                    )
        content.save()
        content.screens.set(screens)
        content.save()

        # call content scheduler
        schedule_content()

        messages.add_message(
            request, messages.SUCCESS,
            gettext(
                'File "%(title)s" uploaded successfully.'
            ) % {'title': title},
            'alert alert-success')

        cur_language = translation.get_language()
        try:
            translation.activate('en')
            email_subject = f'New infoscreen content from {group}'
            email_text = render_to_string('infoscreen/new_content_email.txt',
                                          context={
                                              'user': user,
                                              'group': group,
                                              'content': content,
                                          })
        finally:
            translation.activate(cur_language)

        try:
            send_email_to_staff(email_subject, email_text, [user.email])
        except SMTPException:
            messages.add_message(
                request, messages.ERROR,
                gettext(
                    'Email-transport failed. Please email %(rec)s manually '
                    'and mention your content id (%(id)s). Sorry for the '
                    'inconvenience!'
                ) % {'rec': ', '.join(settings.STAFF_EMAIL_ADDRESSES),
                     'id': content.id},
                'alert alert-danger')

        return redirect('infoscreen_index')
