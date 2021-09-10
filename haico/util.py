import textwrap
from typing import Optional

from django.core import mail

from haico import settings


def flow_text(text: str) -> str:
    """
    This method applies format=flowed (RFC 3676) to a non-wrapped text.
    Note that there is no paragraph or quote detection.
    Existing new lines are preserved.
    See https://joeclark.org/ffaq.html for a quick description of f=f.
    :param text: is the non flowed text
    :return: flowed text according to RFC 3676
    """
    result = ''

    for line in text.splitlines():
        result += ' \r\n'.join(textwrap.wrap(line, 77,
                                             break_long_words=False,
                                             break_on_hyphens=False))
        result += '\r\n'

    return result


def send_email(subject: str, message: str, to: list[str],
               reply_to: Optional[list[str]]):
    message = flow_text(message)

    with mail.get_connection() as connection:
        msg = mail.EmailMessage(
            subject, message, None, to,
            reply_to=reply_to, connection=connection,
        )

        msg.content_subtype = 'plain; format=flowed'

        msg.send()


def send_email_to_staff(subject: str, message: str,
                        reply_to: Optional[list[str]]):
    staff_email = settings.STAFF_EMAIL_ADDRESSES
    reply_to = staff_email if reply_to is None else reply_to + staff_email
    send_email(subject, message, staff_email, reply_to)
