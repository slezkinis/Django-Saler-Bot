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
        if user:
            text = ''
            if user[0].username:
                if user[0].selected_language == 'ru':
                    text = f'Привет, {user[0].username}!'
                else:
                    text = f'Hi, {user[0].username}!'
            else:
                if user[0].selected_language == 'ru':
                    text = f'Привет, {message.chat.first_name}!'
                else:
                    text = f'Hi, {message.chat.first_name}!'
            bot.send_message(message.chat.id, text)
        else:
            markup = types.InlineKeyboardMarkup()
            ru = types.InlineKeyboardButton('🇷🇺 Русский', callback_data='language_ru')
            en = types.InlineKeyboardButton('🇬🇧 English', callback_data='language_en')
            markup.add(ru)
            markup.row()
            markup.add(en)
            bot.send_message(message.chat.id, f'Привет! Выбери язык бота:\n\nHello! Select bot language:', reply_markup=markup)


    @bot.callback_query_handler(lambda m: 'language' in m.data)
    def change_language(message):
        user = User.objects.create(
            tg_id=message.message.chat.id,
            username=message.message.chat.username,
            selected_language=message.data.replace('language_', '')
        )
        if user.selected_language == 'ru':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.edit_message_text(f'Ты выбрал русский язык как основной! Если вдруг захочешь изменить язык, то нажми кнопку в меню!', message.message.chat.id, message.message.message_id, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🚫 Close', callback_data='close'))
            bot.edit_message_text(f'You chose English as your main language! If you suddenly want to change the language, then press the button in the menu!', message.message.chat.id, message.message.message_id, reply_markup=markup)
    bot.infinity_polling(skip_pending = True)
