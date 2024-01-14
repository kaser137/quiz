# QUIZ
викторина, боты для Телеграм и ВК

[VK bot](https://vk.com/quiz_devman)  
[Telegram bot](https://t.me/AiogramHelpBot)

## Установка

Скачайте код с репозитория. Распакуйте и перейдите в папку проекта.


В папке проекта создайте виртуальное окружение:
```commandline
python3 -m venv venv
```

Установите зависимости:
```commandline
pip install -r requirements.txt
```
### Настройка базы данных

[Зарегистрируйтесь и создайте базу данных на Redis](https://redislabs.com/)

### Определите переменные окружения.
Создайте файл `.env` в папке проекта  и заполните его следующими данными:
```commandline
TG_BOT_TOKEN = токен для телеграм-бота
REDIS_PASSWORD = пароль к базе данных на Redis
REDIS_USERNAME = имя пользователя  базы данных на Redis
REDIS_HOST = хост базы данных на Redis
REDIS_PORT = порт базы данных на Redis
VK_KEY = ключ доступа по API к сообществу в ВК
QUIZ_FILES_PATH = путь к файлам с ввопросами и ответами для викторины
```

Для запуска Телеграм бота наберите команду:
```commandline
python3 tg_bot.py
```
Для ВК бота:
```commandline
python3 vk_bot.py
```
