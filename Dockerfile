# For testing run with: docker run --expose=8000 -p 8000:8000 -i container_id
# For production don't set a port, let docker pick one.

FROM ubuntu:14.04
MAINTAINER Geoffrey Golliher <brokenway@gmail.com>

LABEL Description="This image is used to start the Katch url shortener service."

RUN mkdir -p /var/www/shorties

RUN apt-get update
#RUN apt-get install -y postgresql
RUN apt-get install -y python-setuptools
RUN easy_install virtualenv
RUN easy_install pip 
RUN apt-get install -y apache2
RUN apt-get install -y libapache2-mod-wsgi
RUN apt-get install -y sqlite3
RUN apt-get install -y python-psycopg2
RUN pip install https://github.com/mitsuhiko/flask/tarball/master
RUN easy_install datadog

ADD shorties /var/www/shorties
RUN cd /var/www/shorties/src; /usr/local/bin/flask --app=server initdb 

# Testing. If this fails, the build fails.
RUN python /var/www/shorties/src/server_tests.py 
RUN python /var/www/shorties/src/hash_lib_tests.py 

RUN useradd -m --home /home/httpd httpd
ADD shorties/apache_configs/apache2.conf /etc/apache2/apache2.conf
ADD shorties/apache_configs/ports.conf /etc/apache2/ports.conf

RUN chown httpd:httpd /var/log/apache2
RUN chown httpd:httpd /var/lock/apache2
RUN chown -R httpd:httpd /var/www/shorties

ENV APACHE_RUN_USER httpd 
ENV APACHE_RUN_GROUP httpd
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid

CMD /usr/sbin/apache2ctl -D FOREGROUND
