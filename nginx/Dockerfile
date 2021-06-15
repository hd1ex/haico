FROM nginx:alpine

ENV SERVER_USER="http"
RUN adduser -D -g "$SERVER_USER" "$SERVER_USER"

ENV APP_CONF=/etc/nginx/sites-available/haico.conf
RUN mkdir -p $(dirname $APP_CONF)
COPY nginx.conf /etc/nginx/nginx.conf
COPY haico.conf $APP_CONF

RUN rm /etc/nginx/conf.d/default.conf && \
    mkdir -p /etc/nginx/sites-enabled/ && \
    ln -sf $APP_CONF /etc/nginx/sites-enabled/
