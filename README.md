### Установка
    /var/www/coins/env/bin/python /var/www/coins/manage.py syncdb
    /var/www/coins/env/bin/python /var/www/coins/manage.py loaddata /var/www/coins/coins/fixtures/country_currency.json
    cd /var/www/coins/coins
    /var/www/coins/env/bin/python /var/www/coins/manage.py compilemessages -l ru

### Импорт информации
###### Импорт всей базы о инвестиционных и памятных монетах с сайта Центрального Банка России
    /var/www/coins/env/bin/python /var/www/coins/manage.py cbr

###### Импорт информации о инвестиционных и памятных монетах с сайта Центрального Банка России за определенный год
    /var/www/coins/env/bin/python /var/www/coins/manage.py cbr -y 2013

###### Импорт информации о странах и валютах
    /var/www/coins/env/bin/python /var/www/coins/manage.py countries