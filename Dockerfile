FROM corpusops/python:3
WORKDIR /app
ARG APP_USER=ovh
ENV APP_USER=$APP_USER
ENV PATH=/app/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN bash -exc ': \
	&& if ! ( getent passwd $APP_USER &>/dev/null );then useradd -ms /bin/bash -d /home/$APP_USER $APP_USER --uid 1000;fi \
	&& chown -Rf $APP_USER:$APP_USER .'
ADD req*txt ./
USER $APP_USER
RUN bash -exc ': \
	&& pip install --user -U -r requirements.txt \
	'
ADD /app *md *txt ./
USER root
ENTRYPOINT ["/app/entry.sh"]
CMD []
