### Установка
###### Установка Coins
    # apt-get install python-dev python-virtualenv mercurial libxml2-dev libxslt1-dev gettext

    $ git clone git@github.com:kihamo/coins.git /var/www/coins
    $ cd /var/www/coins
    $ ./build.sh -i

###### Настройка Supervisor
    # apt-get install supervisor
    # ln -si /var/www/coins/supervisor.program.conf /etc/supervisor/conf.d/coinscollection.conf
    # supervisorctl reload

###### Настройка Nginx
    # apt-get install nginx
    # ln -si /var/www/coins/nginx.host.conf /etc/nginx/sites-enabled/coinscollection.conf
    # nginx -s reload &> /dev/null || nginx

### Обновление
    $ cd /var/www/coins
    $ ./build.sh -d

### Импорт информации
###### Импорт всей базы о инвестиционных и памятных монетах с сайта Центрального Банка России
    /var/www/coins/env/bin/python manage.py cbr

###### Импорт информации о инвестиционных и памятных монетах с сайта Центрального Банка России за определенный год
    /var/www/coins/env/bin/python manage.py cbr -y 2013

###### Импорт информации о инвестиционных и памятных монетах с сайта Центрального Банка России за несколько лет
    /var/www/coins/env/bin/python manage.py cbr -y 2013,2012

###### Импорт информации о инвестиционной или памятной монете с сайта Центрального Банка России по ее каталожному номеру
    /var/www/coins/env/bin/python manage.py cbr -n 5216-0060

###### Импорт информации о странах и валютах
    /var/www/coins/env/bin/python manage.py countries
