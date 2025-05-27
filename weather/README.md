# Weather_forecast_Django

Сайт просмотра прогнозы погоды по городу.

_Техническое задание:_

```text
Сделать web приложение, оно же сайт, где пользователь вводит название города, и получает прогноз погоды в этом городе на ближайшее время.
```

Полный текст ТЗ можно прочесть здесь: [ТЗ_o-complex.docx](%D2%C7_o-complex.docx)

__Доступные адреса (эндпоинты) и функции:__

* `/admin/` - адрес административной панели
* `/` - адрес стартовой страницы (она же страница авторизации)
* `/get-weather/` - адрес получения прогноза погоды для выбранного города
* `/history/` - адрес просмотра истории для текущего пользователя
* `/api/history/` - адрес API-функционала просмотра истории для текущего пользователя
* `/api/schema/` - адрес yaml-схемы API-функционала
* `/api/swagger/` - адрес swagger-схемы API-функционала
* `/api/redoc/` - адрес redoc-схемы API-функционала

## Примеры:

* #### _Стартовая страница (без авторизацией, авторизация, с авторизированным пользователем):_
* ![index_no_auth.JPG](README%2Findex_no_auth.JPG)
* ![index_login.JPG](README%2Findex_login.JPG)
* ![index_auth.JPG](README%2Findex_auth.JPG)
* #### _Страница с прогнозом погоды:_
* ![weather.JPG](README%2Fweather.JPG)
* #### _Страница истории запросов:_
* ![history.JPG](README%2Fhistory.JPG)
* #### _Страница сваггера:_
* ![swagger.JPG](README%2Fswagger.JPG)

## Порядок запуска:

* Клонировать: `git clone https://github.com/ildarius116/Weather_forecast_Django`

### Вариант без учета Docker-compose:

* Установить зависимости: `pip install -r requirements.txt`
* Применить миграции: `python manage.py migrate`
* Запустить сервер: `python manage.py runserver`
* Создать суперпользователя (администратора): `python manage.py createsuperuser`

### Вариант через Docker-compose:

* Собрать контейнер проекта и запустить его: `docker-compose up --build`
* Войти в контейнер приложения кафе: `docker exec -it weather_app bash `
* Создать суперпользователя (администратора): `python manage.py createsuperuser`

### _Примечания:_

1. При создании суперпользователя, потребуется ввести следующие данные:

* ```text
    Имя пользователя:
    Адрес электронной почты: (не обязательно)
    Password: 
    Password (again):
    ```

2. По необходимости, запустить тесты: `python manage.py test`
