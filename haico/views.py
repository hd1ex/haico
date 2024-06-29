from django.contrib.auth import login, logout, REDIRECT_FIELD_NAME
from django.http import HttpResponse, HttpRequest
from django.urls import reverse
from django.shortcuts import redirect, resolve_url

from authlib.integrations.django_client import OAuth
from django.utils.http import url_has_allowed_host_and_scheme

from haico import auth, settings

oauth = OAuth()
oauth.register(
    name='org',
    server_metadata_url=settings.OPENID_CONF_URL,
    client_kwargs={
        'scope': settings.OAUTH_CLIENT_SCOPES,
    }
)


def login_view(request: HttpRequest) -> HttpResponse:
    redirect_to = request.POST.get(REDIRECT_FIELD_NAME,
                                   request.GET.get(REDIRECT_FIELD_NAME, ''))
    if not url_has_allowed_host_and_scheme(redirect_to, request.get_host()):
        redirect_to = resolve_url('/')
    redirect_uri = request.build_absolute_uri(reverse('auth'))
    redirect_uri += f'?{REDIRECT_FIELD_NAME}={redirect_to}'
    return oauth.org.authorize_redirect(request, redirect_uri)


def auth_view(request: HttpRequest) -> HttpResponse:
    token = oauth.org.authorize_access_token(request)
    user = oauth.org.parse_id_token(token, token['userinfo']['nonce'])
    user = auth.update_user(user)
    login(request, user)

    redirect_to = request.POST.get(REDIRECT_FIELD_NAME,
                                   request.GET.get(REDIRECT_FIELD_NAME, ''))
    if not url_has_allowed_host_and_scheme(redirect_to, request.get_host()):
        redirect_to = resolve_url('/')
    return redirect(redirect_to)


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('/')
