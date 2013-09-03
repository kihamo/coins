### Установка
    build.sh -i

### Обновление
    build.sh -d

### Импорт информации
###### Импорт всей базы о инвестиционных и памятных монетах с сайта Центрального Банка России
    cd /var/www/coins
    source /var/www/coins/env/bin/active
    ./manage.py cbr

###### Импорт информации о инвестиционных и памятных монетах с сайта Центрального Банка России за определенный год
    cd /var/www/coins
    source /var/www/coins/env/bin/active
    ./manage.py cbr -y 2013

###### Импорт информации о странах и валютах
    cd /var/www/coins
    source /var/www/coins/env/bin/active
    ./manage.py countries
