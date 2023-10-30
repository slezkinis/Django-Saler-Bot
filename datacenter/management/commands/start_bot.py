from django.core.management.base import BaseCommand
from project.settings import TG_TOKEN
from datacenter.models import *


class Command(BaseCommand):
    help = 'Стартовать бота'
    
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print('START')
        start_bot()

register = []
def start_bot():
    import telebot
    from telebot import types

    bot = telebot.TeleBot(TG_TOKEN)
    
    @bot.callback_query_handler(lambda m: m.data == 'close')
    def close(message):
        bot.delete_message(message.message.chat.id, message.message.message_id)
        bot.answer_callback_query(message.id)


    @bot.message_handler(commands=['start'])
    def start(message):
        user = User.objects.filter(tg_id=message.chat.id)
        markup = types.ReplyKeyboardMarkup(True)
        if user:
            markup = types.ReplyKeyboardMarkup(True)
            if user[0].selected_language == 'ru':
                products = types.KeyboardButton('🛒 Каталог')
                change_language_button = types.KeyboardButton('🔁 Изменить язык')
                profile = types.KeyboardButton('📱 Профиль')
                markup.add(products, change_language_button, profile)
                text = ''
                if user[0].username:
                    text = f'Привет, {user[0].username}!'
                else:
                    text = f'Привет, {message.chat.first_name}!'
            else:
                products = types.KeyboardButton('🛒 Catalog')
                change_language_button = types.KeyboardButton('🔁 Change the language')
                profile = types.KeyboardButton('📱 Profile')
                markup.add(products, change_language_button, profile)
                if user[0].username:
                    text = f'Hi, {user[0].username}!'
                else:
                    text = f'Hi, {message.chat.first_name}!'
            bot.send_message(message.chat.id, text, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            ru = types.InlineKeyboardButton('🇷🇺 Русский', callback_data='register_language_ru')
            en = types.InlineKeyboardButton('🇬🇧 English', callback_data='register_language_en')
            markup.add(ru)
            markup.row()
            markup.add(en)
            bot.send_message(message.chat.id, f'Привет! Выбери язык бота:\n\nHello! Select bot language:', reply_markup=markup)

    
    @bot.message_handler(content_types=['text'], func=lambda m: m.text == '🔁 Change the language' or m.text == '🔁 Изменить язык')
    def change_language(message):
        try:
            user = User.objects.get(tg_id=message.chat.id)
        except:
            start(message)
            return
        markup = types.InlineKeyboardMarkup()
        if user.selected_language == 'ru':
            select_ru = types.InlineKeyboardButton('✅ Да', callback_data='change_language_en')
            markup.add(select_ru)
            bot.send_message(message.chat.id, 'Сейчас у тебя установлен русский язык. Ты уверен, что хочешь поменять его на английский?', reply_markup=markup)
        else:
            select_ru = types.InlineKeyboardButton('✅ Yes', callback_data='change_language_ru')
            markup.add(select_ru)
            bot.send_message(message.chat.id, 'Your language is now set to English. Are you sure you want to change it to Russian?', reply_markup=markup)


    @bot.callback_query_handler(lambda m: 'change_language_' in m.data)
    def change_language_ok(message):
        bot.delete_message(message.message.chat.id, message.message.message_id)
        user = User.objects.get(tg_id=message.message.chat.id)
        user.selected_language = str(message.data).replace('change_language_', '')
        user.save()
        markup = types.ReplyKeyboardMarkup(True)
        if user.selected_language == 'ru':
            products = types.KeyboardButton('🛒 Каталог')
            change_language_button = types.KeyboardButton('🔁 Изменить язык')
            profile = types.KeyboardButton('📱 Профиль')
            markup.add(products, change_language_button, profile)
            bot.send_message(message.message.chat.id, f'Ты выбрал русский язык как основной! Если вдруг захочешь изменить язык, то нажми кнопку в меню!', reply_markup=markup)
        else:
            products = types.KeyboardButton('🛒 Catalog')
            change_language_button = types.KeyboardButton('🔁 Change the language')
            profile = types.KeyboardButton('📱 Profile')
            markup.add(products, change_language_button, profile)
            bot.send_message(message.message.chat.id, f'You chose English as your main language! If you suddenly want to change the language, then press the button in the menu!', reply_markup=markup)

    @bot.callback_query_handler(lambda m: 'register_language' in m.data)
    def select_language(message):
        bot.delete_message(message.message.chat.id, message.message.message_id)
        user = User.objects.create(
            tg_id=message.message.chat.id,
            username=message.message.chat.username,
            selected_language=message.data.replace('register_language_', '')
        )
        if user.selected_language == 'ru':
            markup = types.ReplyKeyboardMarkup(True)
            products = types.KeyboardButton('🛒 Каталог')
            change_language_button = types.KeyboardButton('🔁 Изменить язык')
            profile = types.KeyboardButton('📱 Профиль')
            markup.add(products, change_language_button, profile)
            bot.send_message(message.message.chat.id, f'Ты выбрал русский язык как основной! Если вдруг захочешь изменить язык, то нажми кнопку в меню!', reply_markup=markup)
        else:
            markup = types.ReplyKeyboardMarkup(True)
            products = types.KeyboardButton('🛒 Catalog')
            change_language_button = types.KeyboardButton('🔁 Change the language')
            profile = types.KeyboardButton('📱 Profile')
            markup.add(products, change_language_button, profile)
            bot.send_message(message.message.chat.id, f'You chose English as your main language! If you suddenly want to change the language, then press the button in the menu!', reply_markup=markup)
    
    
    @bot.message_handler(content_types=['text'], func=lambda m: m.text == '🛒 Каталог' or m.text == '🛒 Catalog')
    def show_categories_message(message):
        try:
            user = User.objects.get(tg_id=message.chat.id)
        except:
            start(message)
            return
        markup = types.InlineKeyboardMarkup()
        categories = Category.objects.all()
        if user.selected_language == 'ru':
            for category in categories:
                markup.add(types.InlineKeyboardButton(category.name_ru, callback_data=f'category_{category.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.send_message(message.chat.id, 'Вот список геолокаций:', reply_markup=markup)
        else:
            for category in categories:
                markup.add(types.InlineKeyboardButton(category.name_en, callback_data=f'category_{category.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            bot.send_message(message.chat.id, 'Here is a list of geolocations:', reply_markup=markup)

    @bot.callback_query_handler(lambda m: m.data == 'home')
    def show_categories_callback(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        markup = types.InlineKeyboardMarkup()
        categories = Category.objects.all()
        if user.selected_language == 'ru':
            for category in categories:
                markup.add(types.InlineKeyboardButton(category.name_ru, callback_data=f'category_{category.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            # bot.send_message(message.chat.id, 'Вот список геолокаций:', reply_markup=markup)
            bot.edit_message_text('Вот список геолокаций:', message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            for category in categories:
                markup.add(types.InlineKeyboardButton(category.name_en, callback_data=f'category_{category.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            # bot.send_message(message.chat.id, 'Here is a list of geolocations:', reply_markup=markup)
            bot.edit_message_text('Here is a list of geolocations:', message.message.chat.id, message.message.message_id, reply_markup=markup)


    @bot.callback_query_handler(lambda m: 'category_' in m.data)
    def show_products_in_category(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        category = Category.objects.get(id=message.data.replace('category_', ''))
        markup = types.InlineKeyboardMarkup()
        if user.selected_language == 'ru':
            for product in category.products.all():
                markup.add(types.InlineKeyboardButton(product.name_ru, callback_data=f'get_product_{product.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('Назад 🔙', callback_data=f'home'))
            # bot.send_message(message.message.chat.id, f'Вот список товаров в категории "{category.name_ru}:', reply_markup=markup)
            bot.edit_message_text(f'Вот список товаров в геолокации "{category.name_ru}":', message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            for product in category.products.all():
                markup.add(types.InlineKeyboardButton(product.name_en, callback_data=f'get_product_{product.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('Back 🔙', callback_data=f'home'))
            # bot.send_message(message.message.chat.id, f'Here is a list of products in the category "{category.name_en}:', reply_markup=markup)
            bot.edit_message_text(f'Here is a list of products in the geolocation "{category.name_en}":', message.message.chat.id, message.message.message_id, reply_markup=markup)

        
    @bot.callback_query_handler(lambda m: 'get_product_' in m.data)
    def show_product(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        product = Product.objects.get(id=message.data.replace('get_product_', ''))
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            if len(product.accounts.filter(is_enabled=True)) and user.money >= product.price:
                markup.add(types.InlineKeyboardButton('Показать аккаунты', callback_data=f'show_accounts_{product.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('Назад 🔙', callback_data=f'category_{product.category.id}'))
            text = f'''
Название: {product.name_ru}
Описание: {product.description_ru}
Цена: {product.price} $
Аккаунтов осталось: {len(product.accounts.filter(is_enabled=True))} шт.
'''
            if len(product.accounts.filter(is_enabled=True)) == 0:
                text += '\n\nК сожалению, все аккаунты закончились. 😞 Но не расстраивайся, скоро они пополнятся'
            if user.money < product.price:
                text += '\n\nК сожалению, у тебя не достаточно денег!😞'
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)    
        else:
            markup = types.InlineKeyboardMarkup()
            if len(product.accounts.filter(is_enabled=True)) and user.money >= product.price:
                markup.add(types.InlineKeyboardButton('Show accounts', callback_data=f'show_accounts_{product.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('Back 🔙', callback_data=f'category_{product.category.id}'))
            text = f"""
Title: {product.name_en}
Description: {product.description_en}
Price: {product.price} $
Accounts left: {len(product.accounts.filter(is_enabled=True))}
"""
            if product.accounts.count() == 0:
                text += "\n\nUnfortunately, all accounts have expired. 😞 But don't worry, they'll be replenished soon."
            if user.money < product.price:
                text += "\n\nUnfortunately, you don't have enough money!😞"
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)

    @bot.callback_query_handler(lambda m: 'show_accounts_' in m.data)
    def all_accounts_for_product(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        product = Product.objects.get(id=message.data.replace('show_accounts_', ''))
        accounts = product.accounts.filter(is_enabled=True)
        if len(accounts) > 10:
            accounts = accounts[:10]
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            text = f"""
Вот аккаунты, которые доступны для товара {product.name_ru}:
            """
            num = 1
            for account in accounts:
                markup.add(types.InlineKeyboardButton(num, callback_data=f'select_account_{account.id}'))
                if num % 3 == 0:
                    markup.row()
                account_data = account.file.read().decode("utf-8").replace('\n', '').split(' : ', 2)
                account_data[0] = list(account_data[0])
                account_data[1] = list(account_data[1])
                account_data[0][-3:] = '***'
                account_data[1][-len(account_data[1]) + 3:] = '*' * abs(-len(account_data[1]) + 3)
                # print(-len(account_data[1]) + 3)
                # account_data[1][-len(account_data[1]) + 3]
                account_data[0] = ''.join(account_data[0])
                account_data[1] = ''.join(account_data[1])
                text += f'\n{num}) Логин: {account_data[0]}  Пароль: {account_data[1]}'
                num += 1
            if (num - 1) % 2 != 0:
                markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            text += '\n Нажми на номер аккаунта, который тебе понравился:'
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            text = f"""
Here are the accounts that are available for {product.name_en}:
            """
            num = 1
            for account in accounts:
                markup.add(types.InlineKeyboardButton(num, callback_data=f'select_account_{account.id}'))
                if num % 3 == 0:
                    markup.row()
                account_data = account.file.read().decode("utf-8").replace('\n', '').split(' : ', 2)
                account_data[0] = list(account_data[0])
                account_data[1] = list(account_data[1])
                account_data[0][-3:] = '***'
                account_data[1][-len(account_data[1]) + 3:] = '*' * abs(-len(account_data[1]) + 3)
                # print(-len(account_data[1]) + 3)
                # account_data[1][-len(account_data[1]) + 3]
                account_data[0] = ''.join(account_data[0])
                account_data[1] = ''.join(account_data[1])
                text += f'\n{num}) Login: {account_data[0]}  Password: {account_data[1]}'
                num += 1
            if (num - 1) % 2 != 0:
                markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            text += '\n Click on the account number you like:'
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)
    
    @bot.callback_query_handler(lambda m: 'select_account_' in m.data)
    def are_u_sure(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        markup = types.InlineKeyboardMarkup()
        account = Account.objects.get(id=message.data.replace('select_account_', ''))
        yes = types.InlineKeyboardButton('✅', callback_data=f'yes_buy_{account.id}')
        no = types.InlineKeyboardButton('❌', callback_data=f'no_send_to_all_{account.id}')
        markup.add(yes, no)
        account_data = account.file.read().decode("utf-8").replace('\n', '').split(' : ', 2)
        account_data[0] = list(account_data[0])
        account_data[1] = list(account_data[1])
        account_data[0][-3:] = '***'
        account_data[1][-len(account_data[1]) + 3:] = '*' * abs(-len(account_data[1]) + 3)
        # print(-len(account_data[1]) + 3)
        # account_data[1][-len(account_data[1]) + 3]
        account_data[0] = ''.join(account_data[0])
        account_data[1] = ''.join(account_data[1])
        if user.selected_language == 'ru':
            text = f"""
Ты уверен, что хочешь купить этот аккаунт:
Логин: {account_data[0]}
Пароль: {account_data[1]}
Цена: {account.product.price} $

"""
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            text = f"""
Are you sure you want to buy this account?
Login: {account_data[0]}
Password: {account_data[1]}
Price: {account.product.price} $

"""
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)
    bot.infinity_polling(skip_pending = True)
