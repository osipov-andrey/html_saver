# Тестовое задание для python-разработчика

[Описание задания](https://github.com/avtocod/python-developer-test-task)

![Project language][badge_language]
![Docker][badge_docker]



### Описание

Реализовать сервис, который обходит произвольный сайт с глубиной до 2 и сохраняет `html`, `url` и `title` страницы в хранилище.

Примеры сайтов:

* `https://ria.ru`
* `http://www.vesti.ru`
* `http://echo.msk.ru`
* `http://tass.ru/ural` 
* `https://lenta.ru`
* и любой другой, на котором есть ссылки
    
> При depth=0 необходимо сохранить html, title, url исходного веб-сайта.
>
> На каждом depth=i+1 качаем страницы ссылок с i страницы (то есть глубина 2 это - главная, ссылки на главной и ссылки на страницах ссылок с главной).

### CLI

* По урлу сайта и глубине обхода загружаются данные.
* По урлу сайта из хранилища можно получить `n` прогруженных страниц (`url` и `title`).
    
Пример:
```
spider.py load http://www.vesti.ru/ --depth 2
>> ok, execution time: 10s, peak memory usage: 100 Mb
spider.py get http://www.vesti.ru/ -n 2
>> http://www.vesti.ru/news/: "Вести.Ru: новости, видео и фото дня"
>> http://www.vestifinance.ru/: "Вести Экономика: Главные события российской и мировой экономики, деловые новости,  фондовый рынок"
```

* Дропнуть базу данных и удалить все скаченные HTML-файлы.
* Создать базу данных.

Пример:
```
spider.py db drop
spider.py db create
```

### Стек технологий

* python3.8
* PostgreSQL
* Docker
* Docker-compose

### HOWTO:

```bash
$ git clone ...
$ cp .env.template .env
$ docker-compose up -d
$ docker-compose run --rm app load http://www.vesti.ru/ --depth 2
$ docker-compose run --rm app get http://www.vesti.ru/ -n 5
```

### TODO:
* Tests
* Checking memory usage



[badge_language]:https://img.shields.io/badge/python-3-yellow?longCache=true
[badge_docker]:https://img.shields.io/badge/docker-enable-blue?longCache=true
