from django.core.management.base import BaseCommand

from project.settings import TG_TOKEN, ADMIN_TG_ID, CRYPTOMUS_API_KEY, CRYPTOMUS_MERCHANT_ID
from datacenter.models import *
import datetime
from django.utils import timezone

import math
import requests
import base64
import hashlib
import json
import uuid
import decimal


who_add_balance = set()
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
                help = types.KeyboardButton('❓ Помощь')
                profile = types.KeyboardButton('📱 Профиль')
                markup.add(products, change_language_button, help, profile)
                text = ''
                if user[0].username:
                    text = f'Привет, {user[0].username}!'
                else:
                    text = f'Привет, {message.chat.first_name}!'
            else:
                products = types.KeyboardButton('🛒 Catalog')
                change_language_button = types.KeyboardButton('🔁 Change the language')
                help = types.KeyboardButton('❓ Help')
                profile = types.KeyboardButton('📱 Profile')
                markup.add(products, change_language_button, help, profile)
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

    @bot.message_handler(content_types=['text'], func=lambda m: m.text == '❓ Help' or m.text == '❓ Помощь')
    def help(message):
        try:
            user = User.objects.get(tg_id=message.chat.id)
        except:
            start(message)
            return
        markup = types.InlineKeyboardMarkup()
        if user.selected_language == 'ru':
            markup.add(types.InlineKeyboardButton('Перейти', url='https://t.me/Ivan_Slezkin'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.send_message(message.chat.id, '✍️ По всем возникающим вопросам пишите @Ivan_Slezkin', reply_markup=markup)
        else:
            markup.add(types.InlineKeyboardButton('Follow the link', url='https://t.me/Ivan_Slezkin'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            bot.send_message(message.chat.id, '✍️ For any questions please write to @Ivan_Slezkin', reply_markup=markup)


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
            markup.row()
            markup.add(types.InlineKeyboardButton('❌ Нет', callback_data='cancel_add_balance'))
            bot.send_message(message.chat.id, 'Сейчас у тебя установлен русский язык. Ты уверен, что хочешь поменять его на английский?', reply_markup=markup)
        else:
            select_ru = types.InlineKeyboardButton('✅ Yes', callback_data='change_language_ru')
            markup.add(select_ru)
            markup.row()
            markup.add(types.InlineKeyboardButton('❌ No', callback_data='cancel_add_balance'))
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
            help = types.KeyboardButton('❓ Помощь')
            profile = types.KeyboardButton('📱 Профиль')
            markup.add(products, change_language_button, help, profile)
            bot.send_message(message.message.chat.id, f'Ты выбрал русский язык как основной! Если вдруг захочешь изменить язык, то нажми кнопку в меню!', reply_markup=markup)
        else:
            products = types.KeyboardButton('🛒 Catalog')
            change_language_button = types.KeyboardButton('🔁 Change the language')
            help = types.KeyboardButton('❓ Help')
            profile = types.KeyboardButton('📱 Profile')
            markup.add(products, change_language_button, help, profile)
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
            if len(product.accounts.filter(is_enabled=True)) == 0:
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
    
    @bot.callback_query_handler(lambda m: 'yes_buy_' in m.data)
    def buy_account(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        account = Account.objects.get(id=message.data.replace('yes_buy_', ''))
        account_data = account.file.read().decode("utf-8").replace('\n', '').split(' : ')
        markup = types.InlineKeyboardMarkup()
        if user.money < account.product.price:
            if user.selected_language == 'ru':
                markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
                bot.edit_message_text('У тебя недостаточно денег для покупки этого аккаунта! Пополни счёт и повтори попытку!', message.message.chat.id, message.message.message_id, reply_markup=markup)
            else:
                markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
                bot.edit_message_text("You don't have enough money to purchase this account! Top up your account and try again!", message.message.chat.id, message.message.message_id, reply_markup=markup)
            return   
        settings = Setting.objects.all()[0]
        order = Order.objects.create(
            user=user,
            account=account
        )
        user.money -= account.product.price
        user.save()
        account.is_enabled = False
        account.save()
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('❗️Аккаунт не валиден', callback_data=f'not_valid_{order.id}'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            text = f'''
Поздравляю с покупкой!
Логин: {account_data[0]}
Пароль: {account_data[1]}
'''
            if len(account_data) > 2:
                text += f'Другие данные для подтверждения аккаунта: {" | ".join(account_data[2:])}'
            text += f'\nУ тебя есть ровно {settings.time_to_check} минут, чтобы проверить работоспособность аккаунта. Если не получается зайти в купленный аккаунт, то нажми кнопку ниже'
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('❗️Account is not valid', callback_data=f'not_valid_{order.id}'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            text = f'''
Congratulations on your purchase!
Login: {account_data[0]}
Password: {account_data[1]}
'''
            if len(account_data) > 2:
                text += f'Other information to confirm your account: {" | ".join(account_data[2:])}'
            text += f'\nYou have exactly {settings.time_to_check} minutes to check the functionality of your account. If you can’t log into your purchased account, click the button below!'
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)
    
    @bot.callback_query_handler(lambda m: 'see_order_' in m.data)
    def see_order(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        order = Order.objects.get(id=message.data.replace('see_order_', ''))
        account_data = order.account.file.read().decode("utf-8").replace('\n', '').split(' : ')
        settings = Setting.objects.all()[0]
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            if order.buy_time + datetime.timedelta(minutes=settings.time_to_check) >= timezone.now() and order.status == 'user_in_checking':
                markup.add(types.InlineKeyboardButton('❗️Аккаунт не валиден', callback_data=f'not_valid_{order.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='orders'))
            text = f'''
Логин: {account_data[0]}
Пароль: {account_data[1]}
'''
            if len(account_data) > 2:
                text += f'Другие данные для подтверждения аккаунта: {" | ".join(account_data[2:])}'
            text += f'\n\nСтатус: {order.status.replace("user_in_checking", "OK").replace("not_ok", "Аккаунт не валиден!").replace("admin_in_checking", "Модераторы рассматривают твою заявку").replace("canceled", "Заявка отклонена")}'
            if order.buy_time + datetime.timedelta(minutes=settings.time_to_check) >= timezone.now() and order.status == 'user_in_checking': 
                text += f'\nУ тебя есть ровно {math.ceil(abs(timezone.now() - (order.buy_time + datetime.timedelta(minutes=settings.time_to_check))).seconds / 60)} минут, чтобы проверить работоспособность аккаунта. Если не получается зайти в купленный аккаунт, то нажми кнопку ниже'
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            if order.buy_time + datetime.timedelta(minutes=settings.time_to_check) >= timezone.now() and order.status == 'user_in_checking':
                markup.add(types.InlineKeyboardButton('❗️Account is not valid', callback_data=f'not_valid_{order.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='orders'))
            text = f'''
Login: {account_data[0]}
Password: {account_data[1]}
'''
            if len(account_data) > 2:
                text += f'Other information to confirm your account: {" | ".join(account_data[2:])}'
            text += f'\n\nStatus: {order.status.replace("user_in_checking", "OK").replace("not_ok", "Account is not valid!").replace("admin_in_checking", "Moderators are reviewing your application").replace("canceled", "Application rejected")}'
            if order.buy_time + datetime.timedelta(minutes=settings.time_to_check) >= timezone.now() and order.status == 'user_in_checking': 
                text += f'\nYou have exactly {math.ceil(abs(timezone.now() - (order.buy_time + datetime.timedelta(minutes=settings.time_to_check))).seconds / 60)} minutes to check the functionality of your account. If you can’t log into your purchased account, click the button below'
            bot.edit_message_text(text, message.message.chat.id, message.message.message_id, reply_markup=markup)
    
    @bot.callback_query_handler(lambda m: 'not_valid_' in m.data)
    def not_valid(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        order = Order.objects.get(id=message.data.replace('not_valid_', ''))
        settings = Setting.objects.all()[0]
        if order.buy_time + datetime.timedelta(minutes=settings.time_to_check) >= timezone.now():
            bot.send_message(ADMIN_TG_ID, f'Пользователь {user} сказал, что аккаунт {order.account} не валиден! Проверьте!')
            order.status = 'admin_in_checking'
            order.save()
            if user.selected_language == 'ru':
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
                bot.edit_message_text('Заявка отправлена модераторам!', message.message.chat.id, message.message.message_id, reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
                bot.edit_message_text('The application has been sent to moderators!', message.message.chat.id, message.message.message_id, reply_markup=markup)
            bot.answer_callback_query(callback_query_id=message.id, text='OK')
        else:
            if user.selected_language == 'ru':
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
                bot.edit_message_text('К сожалению, время на проверку аккаунта истекло! Ты не можешь отправить заявку! Извини.', message.message.chat.id, message.message.message_id, reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
                bot.edit_message_text("Unfortunately, the time to verify your account has expired! You can't submit your application! Sorry.", message.message.chat.id, message.message.message_id, reply_markup=markup)
            bot.answer_callback_query(callback_query_id=message.id)
    
    @bot.callback_query_handler(lambda m: 'no_send_to_all_' in m.data)
    def not_buy(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.edit_message_text("Покупка отменена!", message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🚫 Сlose', callback_data='close'))
            bot.edit_message_text("Purchase cancelled!", message.message.chat.id, message.message.message_id, reply_markup=markup)
    
    @bot.message_handler(content_types=['text'], func=lambda m: m.text == '📱 Профиль' or m.text == '📱 Profile')
    def profile(message):
        try:
            user = User.objects.get(tg_id=message.chat.id)
        except:
            start(message)
            return
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('💸 Пополнить баланс', callback_data='add_balance'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🛍️ Мои покупки', callback_data='orders'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            text = f'🙍‍♂ Пользователь: {message.chat.first_name}\n🆔 ID: {message.chat.id}\n💲 Баланс: {user.money} $ \n------------------\n🛒 Количество покупок: {user.orders.count()} шт.'
            bot.send_message(message.chat.id, text, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('💸 Top up balance', callback_data='add_balance'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🛍️ My purchases', callback_data='orders'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            text = f'🙍‍♂ Username: {message.chat.first_name}\n🆔 ID: {message.chat.id}\n💲 Balance: {user.money} $ \n------------------\n🛒 Number of purchases: {user.orders.count()} шт.'
            bot.send_message(message.chat.id, text, reply_markup=markup)
    
    @bot.callback_query_handler(lambda m: m.data == 'add_balance')
    def add_balance(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        global who_add_balance
        who_add_balance.add(message.message.chat.id)
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('↩️ Отмена', callback_data='cancel_add_balance'))
            bot.edit_message_text('Введи сумму в доллапах, на которую хочешь пополнить свой баланс! Учти, что сумма должна быть больше 30 $', message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('↩️ Cancel', callback_data='cancel_add_balance'))
            bot.edit_message_text('Enter the amount in dollars you want to top up your balance with! Please note that the amount must be more than $30', message.message.chat.id, message.message.message_id, reply_markup=markup)

    @bot.callback_query_handler(lambda m: m.data == 'cancel_add_balance')
    def cancel_add_balance(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        global who_add_balance
        try:
            who_add_balance.remove(message.message.chat.id)
        except:
            _ = 1
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.edit_message_text('Операция отменена', message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            bot.edit_message_text('Operation canceled', message.message.chat.id, message.message.message_id, reply_markup=markup)


    def make_request(url, invoice_data):
        encoded_data = base64.b64encode(
            json.dumps(invoice_data).encode("utf-8")
        ).decode("utf-8")
        sign = hashlib.md5(f"{encoded_data}{CRYPTOMUS_API_KEY}".encode("utf-8")).hexdigest()
        headers = {'merchant': CRYPTOMUS_MERCHANT_ID, 'sign': sign}
        response = requests.post(url, json=invoice_data, headers=headers)
        response.raise_for_status()
        return response.json()


    @bot.message_handler(content_types=['text'], func=lambda m: m.chat.id in who_add_balance)
    def get_link_cryptomus(message):
        try:
            user = User.objects.get(tg_id=message.chat.id)
        except:
            start(message)
            return
        try:
            amount = float(message.text)
        except ValueError:
            if user.selected_language == 'ru':
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
                bot.send_message(message.chat.id, 'Отправленный текст не является числом! Проверь и попробуй ещё раз!', reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
                bot.send_message(message.chat.id, 'The sent text is not a number! Check and try again!', reply_markup=markup)
            return
        if amount < 30:
            if user.selected_language == 'ru':
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
                bot.send_message(message.chat.id, 'Как я и говорил, сумма пополнения не может быть меньше 30 $! Проверь это и повтори попытку', reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
                bot.send_message(message.chat.id, 'As I said, the top-up amount cannot be less than $30! Check it and try again', reply_markup=markup)
            return
        global who_add_balance
        try:
            who_add_balance.remove(message.message.chat.id)
        except:
            _ = 1
        invoice_data = {
            "amount": str(amount),
            "currency": "USD",
            "order_id": str(uuid.uuid4()),
            'is_payment_multiple': True
        }
        answer = make_request('https://api.cryptomus.com/v1/payment', invoice_data)
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('💲 Получить ссылку', url=answer['result']['url']))
            markup.row()
            markup.add(types.InlineKeyboardButton('Проверить платёж', callback_data=f'check_payment_{answer["result"]["order_id"]}'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.send_message(message.chat.id, 'Чтобы пополнить баланс нажми на кнопку снизу, оплати. После этого нажми кнопку "Проверить платёж". Учти, что после оплаты платёж ещё несколько минут проверяется!', reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('💲 Get the link', url=answer['result']['url']))
            markup.row()
            markup.add(types.InlineKeyboardButton('Check payment', callback_data=f'check_payment_{answer["result"]["order_id"]}'))
            markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            bot.send_message(message.chat.id, 'To top up your balance, click on the button below and pay. After that, click the “Check payment” button. Please note that after payment the payment takes a few minutes to be verified!', reply_markup=markup)
    
    @bot.callback_query_handler(lambda m: 'check_payment_' in m.data)
    def check_payment(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        answer = make_request('https://api.cryptomus.com/v1/payment/info', {'order_id': message.data.replace('check_payment_', '')})
        # answer['result']['payment_status'] = 'paid'
        if answer['result']['payment_status'] in ('paid', 'paid_over'):
            user.money += decimal.Decimal(float(answer['result']['amount']))
            user.save()
            if user.selected_language == 'ru':
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
                bot.edit_message_text(f'Поздравляю, теперь твой баланс составляет {user.money} $.', message.message.chat.id, message.message.message_id, reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
                bot.edit_message_text(f'Congratulations, your balance is now {user.money} $.', message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            if user.selected_language == 'ru':
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
                bot.send_message(message.message.chat.id, 'Я не увидел, что ты оплатил. Проверь! Если ты всё оплатил, то подожди несколько минут так как платёж проверяется!', reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
                bot.send_message(message.message.chat.id, "I didn't see that you paid. Check it out! If you have paid everything, then wait a few minutes as the payment is being verified!", reply_markup=markup)
        bot.answer_callback_query(callback_query_id=message.id)

    @bot.callback_query_handler(lambda m: m.data == 'orders')
    def orders(message):
        try:
            user = User.objects.get(tg_id=message.message.chat.id)
        except:
            start(message)
            return
        orders = user.orders.all().order_by('-id')
        markup = types.InlineKeyboardMarkup()
        if user.selected_language == 'ru':
            for order in orders:
                account_data = order.account.file.read().decode("utf-8").replace('\n', '').split(' : ')
                markup.add(types.InlineKeyboardButton(f'{order.account.product.name_ru}_{account_data[0]}', callback_data=f'see_order_{order.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.edit_message_text("Вот все твои заказы", message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            for order in orders:
                account_data = order.account.file.read().decode("utf-8").replace('\n', '').split(' : ')
                markup.add(types.InlineKeyboardButton(f'{order.account.product.name_en}_{account_data[0]}', callback_data=f'see_order_{order.id}'))
                markup.row()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            bot.edit_message_text("Here are all your orders", message.message.chat.id, message.message.message_id, reply_markup=markup)

    bot.infinity_polling(skip_pending = True)
