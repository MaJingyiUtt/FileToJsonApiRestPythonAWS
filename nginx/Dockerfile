FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY flaskapp.conf /etc/nginx/conf.d/
COPY .htpasswd /etc/nginx/.htpasswd
