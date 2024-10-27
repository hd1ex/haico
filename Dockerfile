FROM python:3-alpine

# Setup environment
ENV APP_NAME="haico"
ENV APP_PATH="/srv/$APP_NAME"
WORKDIR $APP_PATH
ENV VIRTUAL_ENV="$APP_PATH/venv"
ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY

ENV SERVER_USER="http"
RUN adduser -D -g "$SERVER_USER" "$SERVER_USER"

# Install dependencies
RUN set -e; \
    apk update; \
    apk add gcc libc-dev linux-headers pcre-dev gettext libffi-dev \
        openssl-dev

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip; \
    pip install -r requirements.txt

# Copy files
COPY manage.py manage.py
COPY haico/ haico/
COPY infoscreen/ infoscreen/
COPY static/ static/
COPY templates/ templates/
COPY locale/ locale/
COPY auth_group_mappings auth_group_mappings

# Run applications
RUN python manage.py migrate
RUN python manage.py collectstatic --no-input
RUN python manage.py compilemessages

RUN chown -R "$SERVER_USER:$SERVER_USER" "$APP_PATH"

CMD gunicorn $APP_NAME.wsgi:application --bind 0.0.0.0:8000
