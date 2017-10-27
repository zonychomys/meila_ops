#!/usr/bin/env bash
set -e

sed -i "s/{{ MYSQL_DBNAME }}/${MYSQL_DBNAME}/g" meila_ops/settings.py
sed -i "s/{{ MYSQL_USER }}/${MYSQL_USER}/g" meila_ops/settings.py
sed -i "s/{{ MYSQL_PASS }}/${MYSQL_PASS}/g" meila_ops/settings.py
sed -i "s/{{ MYSQL_HOST }}/${MYSQL_HOST}/g" meila_ops/settings.py
sed -i "s/{{ MYSQL_PORT }}/${MYSQL_PORT}/g" meila_ops/settings.py
sed -i "s/{{ EMAIL_HOST }}/${EMAIL_HOST}/g" meila_ops/settings.py
sed -i "s/{{ EMAIL_PORT }}/${EMAIL_PORT}/g" meila_ops/settings.py
sed -i "s/{{ EMAIL_USER }}/${EMAIL_USER}/g" meila_ops/settings.py
sed -i "s/{{ EMAIL_PASS }}/${EMAIL_PASS}/g" meila_ops/settings.py
sed -i "s/{{ EMAIL_USE_TLS }}/${EMAIL_USE_TLS}/g" meila_ops/settings.py
sed -i "s/{{ EMAIL_TIMEOUT }}/${EMAIL_TIMEOUT}/g" meila_ops/settings.py
/usr/sbin/sshd
python manage.py makemigrations
python manage.py migrate

if [ "${1#-}" != "$1" ]; then
    set -- python manage.py runserver 0.0.0.0:2226 "$@"
fi

exec "$@"
