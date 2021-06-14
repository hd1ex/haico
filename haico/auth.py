import re

from django.contrib.auth.models import User, Group

from haico import settings


def filter_groups(groups: str) -> list[str]:
    res = []

    with open('auth_group_mappings', 'r') as file:
        for line in file.readlines():
            if not line or line.startswith('#'):
                continue
            regex = re.compile(line.strip())

            for group in groups:
                m = regex.match(group)
                if m:
                    if not m.lastindex:
                        res.append(group)
                    else:
                        res.append(m.group(1))

    return res


def update_user(auth: dict) -> User:
    username = auth.get(settings.OAUTH_USERNAME_CLAIM)
    groups = filter_groups(auth.get(settings.OAUTH_GROUP_CLAIM))
    email = auth.get(settings.OAUTH_EMAIL_CLAIM, '')

    user, _ = User.objects.get_or_create(username=username)
    user.email = email

    user.groups.clear()
    for name in groups:
        group, _ = Group.objects.get_or_create(name=name)
        user.groups.add(group)

    is_admin = settings.ADMIN_GROUP in groups
    user.is_staff = is_admin
    user.is_admin = is_admin
    user.is_superuser = is_admin

    user.save()

    return user
