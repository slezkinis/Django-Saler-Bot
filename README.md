# Django-Saler-Bot
 
Бот для продаж аккаунтов игр в телеграмме

# Установка 
1. Для установки зависимостей нужно ввести команду:
   ``` sh
   pip3 install -r requirements.txt
   ```
2. Нужно установить переменные окружения в файле `.env`. Вот пример:
   ```
   TG_TOKEN=Токен бота
   ADMIN_TG_ID= ID телеграмм админа
   CRYPTOMUS_MERCHANT_ID = Merchant ID [Cryptomus](https://cryptomus.com/)
   CRYPTOMUS_API_KEY = "Токен из [Cryptomus](https://cryptomus.com/)"
   ```
3. Затем провести миграцию базы данных:
   ``` sh
   python3 manage.py migrate
   ```
4. Потом создать аккаунт суперадмина в админке:
   ``` sh
   python3 manage.py createsuperuser
   ```
5. Запустить админку командой:
   ``` sh
   python3 manage.py runserver IP:PORT
   ```
6. В админке во вкладе "Нстройки" изменить время ожидания на своё
7. В отдельном окне терминала запустить самого бота:
   ``` sh
   python3 manage.py start_bot
   ```

# Команды админа:
1. `/send_all text` - Отправить рассылку Пример: `/send_all HI!`
2. `/send tg_id text`- Отправить персональное сообщение Пример: `/send 123321 Привет!`
3. `/stat` - Получить статистику
4. `/upload_accounts id продукта` - Загрузить аккаунты. Нужно отправить текстовый документ и в подписи написать команду. Id продукта можно увидеть в админке. Пример: `/upload_accounts 1`
