### Установка
    /var/www/coins/env/bin/python /var/www/coins/manage.py syncdb
    /var/www/coins/env/bin/python /var/www/coins/manage.py loaddata /var/www/coins/coins/fixtures/country_currency.json
    cd /var/www/coins/coins
    /var/www/coins/env/bin/python /var/www/coins/manage.py compilemessages -l ru

### Импорт информации о инвестиционных и памятных монетах с сайта Центрального Банка России
###### Импорт всей базы

    /var/www/coins/env/bin/python /var/www/coins/manage.py cbr

###### Импорт монет за определенный год

    /var/www/coins/env/bin/python /var/www/coins/manage.py cbr -y 2013