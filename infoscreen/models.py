from datetime import datetime

from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import Q
from django.utils.translation import pgettext_lazy, gettext_lazy as _

from haico import settings


class Infoscreen(models.Model):
    class Meta:
        ordering = ('name',)

    name = models.TextField(help_text='The name of the infoscreen.')

    def __str__(self) -> str:
        return self.name


class InfoscreenContent(models.Model):
    class Meta:
        verbose_name = pgettext_lazy('infoscreen content singular',
                                     'infoscreen content')
        verbose_name_plural = pgettext_lazy('infoscreen content plural',
                                            'infoscreen content')

    file_url = models.URLField(verbose_name=_('file url'),
                               help_text=_('An url to the hosted file.'))
    title = models.TextField(help_text=_('A title for the content.'),
                             verbose_name=_('title'))
    group = models.ForeignKey(Group,
                              on_delete=models.RESTRICT,
                              verbose_name=_('group'),
                              help_text=_(
                                  'The name of the associated group.'))
    valid_from = models.DateField(blank=True, null=True,
                                  help_text=_(
                                      'The date when this content should '
                                      'start to be shown. Empty means that it '
                                      'should be shown from now on.'),
                                  verbose_name=_('valid from'))
    valid_until = models.DateField(blank=True, null=True,
                                   help_text=_(
                                       'The date when this content expires. '
                                       'Empty means it does not expire.'),
                                   verbose_name=_('valid until'))
    screens = models.ManyToManyField(Infoscreen,
                                     help_text=_(
                                         'The screens this content '
                                         'should be displayed on.'),
                                     verbose_name=_('screens'))
    submitter = models.ForeignKey(User,
                                  on_delete=models.RESTRICT,
                                  help_text=_(
                                      'The submitter of the content.'),
                                  verbose_name=_('submitter'))
    submission_time = models.DateTimeField(
        help_text=_('The time of submission.'),
        verbose_name=_('submission time'))

    def __str__(self) -> str:
        return self.title

    def get_detail_url(self) -> str:
        return settings.BASE_URL \
               + f'/admin/infoscreen/infoscreencontent/{self.id}/change/'

    @staticmethod
    def query_currently_displayed():
        now = datetime.now()
        return InfoscreenContent.objects.filter(
            Q(valid_from__gte=now) | Q(valid_from=None)).filter(
            Q(valid_until__lte=now) | Q(valid_until=None))

    @staticmethod
    def query_all():
        return InfoscreenContent.objects.all()
