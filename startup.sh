export RADICALE_CONFIG=/opt/radicale/radicale-config
: "${DJANGO_SUPERUSER_USERNAME:=admin}"
: "${DJANGO_SUPERUSER_EMAIL:=aabbcc@example.com}"
: "${DJANGO_SUPERUSER_PASSWORD:=admin}"
: "${HOST:='127.0.0.1'}"
: "${CSRF_ORIGIN:='http://127.0.0.1'}"
: "${CALDAV_PUBLIC_URL:='http://127.0.0.1:5232'}"

DJANGO_SECRET_KEY=$(openssl rand -hex 60)
DJANGO_API_SECRET_KEY=$(openssl rand -hex 60)
CALDAV_PASSWORD=$(openssl rand -hex 60)

mkdir -p /opt/data/collections

cd /opt/rtucaldav
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
cd rtucaldav

sed -i "s|STRING_TO_CHANGE_1|$DJANGO_SECRET_KEY|" local_settings.py
sed -i "s|STRING_TO_CHANGE_2|$CALDAV_PASSWORD|" local_settings.py
sed -i "s|STRING_TO_CHANGE_5|$DJANGO_API_SECRET_KEY|" local_settings.py

sed -i "s|STRING_TO_CHANGE_3|$HOST|" local_settings.py
sed -i "s|STRING_TO_CHANGE_4|$CSRF_ORIGIN|" local_settings.py
sed -i "s|STRING_TO_CHANGE_6|$CALDAV_PUBLIC_URL|" local_settings.py

cd ..
python3 manage.py migrate
python3 manage.py collectstatic --clear --noinput
python3 manage.py createsuperuser --noinput
deactivate

cd /opt/data
chown apache:apache -R .

cd /opt/radicale
htpasswd -cbB /opt/radicale/passwd rtu rtu
htpasswd -bB /opt/radicale/passwd rtucaldav $CALDAV_PASSWORD
python3 -m venv venv
source venv/bin/activate
python3 -m pip install radicale==3.1.8
deactivate

cd /etc/apache2/conf.d
sed -i "s|STRING_TO_CHANGE|$HOST|" basic.conf

cd /etc/cron
sed -i "s|STRING_TO_CHANGE_1|$CSRF_ORIGIN|" crontab
sed -i "s|STRING_TO_CHANGE_2|$DJANGO_API_SECRET_KEY|" crontab
crontab /etc/cron/crontab
crond

/usr/sbin/httpd -D FOREGROUND -f /etc/apache2/httpd.conf