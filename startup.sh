export RADICALE_CONFIG=/opt/radicale/radicale-config
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=adminer@example.com
export DJANGO_SUPERUSER_PASSWORD=admin

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
sed -i "s|STRING_TO_CHANGE_3|$HOST|" local_settings.py
sed -i "s|STRING_TO_CHANGE_4|$CSRF_ORIGIN|" local_settings.py
sed -i "s|STRING_TO_CHANGE_5|$DJANGO_API_SECRET_KEY|" local_settings.py
sed -i "s|STRING_TO_CHANGE_6|$CSRF_ORIGIN|" local_settings.py
cd ..
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py createsuperuser --noinput
deactivate

cd /opt/data
chown apache:apache -R .

cd /opt/radicale
htpasswd -cbB /opt/radicale/passwd rtu rtu
htpasswd -bB /opt/radicale/passwd rtucaldav $CALDAV_PASSWORD
python3 -m venv venv
source venv/bin/activate
python3 -m pip install radicale
deactivate

cd /etc/apache2/conf.d
sed -i "s|STRING_TO_CHANGE|$HOST|" basic.conf

cd /etc/crontabs
sed -i "s|STRING_TO_CHANGE_1|$CSRF_ORIGIN|" root
sed -i "s|STRING_TO_CHANGE_2|$DJANGO_API_SECRET_KEY|" root

crond
/usr/sbin/httpd -D FOREGROUND -f /etc/apache2/httpd.conf