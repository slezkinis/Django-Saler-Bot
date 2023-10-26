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
    bot.infinity_polling(skip_pending = True)
