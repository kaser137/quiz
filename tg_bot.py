import logging
import os
import redis
import telegram

from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from functools import wraps
from dotenv import load_dotenv

from functions import exam

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)


@send_typing_action
def start(update: Update, context: CallbackContext, redis_client) -> None:
    chat_id = update.message.chat_id
    if not redis_client.get(f'c{chat_id}'):
        redis_client.set(f'c{chat_id}', 0)
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт', 'Обнулить счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Здравствуйте', reply_markup=reply_markup)


@send_typing_action
def echo(update: Update, context: CallbackContext, redis_client) -> None:
    chat_id = update.message.chat_id
    if update.message.text == 'Новый вопрос':
        question, answer = exam()
        redis_client.set(f'q{chat_id}', question)
        redis_client.set(f'a{chat_id}', answer)
        update.message.reply_text(question)
    elif update.message.text == 'Обнулить счёт':
        redis_client.set(f'c{chat_id}', 0)
        update.message.reply_text('Твой счёт обнулён.'
                                  'Для следующего вопроса нажми «Новый вопрос')
    elif update.message.text == 'Мой счёт':
        count = redis_client.get(f'c{chat_id}').decode()
        update.message.reply_text(f' Твой счёт: {count}')
    elif update.message.text == 'Сдаться':
        count = int(redis_client.get(f'c{chat_id}').decode()) - 1
        redis_client.set(f'c{chat_id}', count)
        update.message.reply_text(f'Очень жаль :(( Твой счёт: {count}.\n'
                                  f'{redis_client.get(f"a{chat_id}").decode()}\n'
                                  'Для следующего вопроса нажми «Новый вопрос')
    elif redis_client.get(f'a{chat_id}'):
        right_answer = min(
            redis_client.get(f'a{chat_id}').decode().split('(')[0].casefold(),
            redis_client.get(f'a{chat_id}').decode().split('.')[0].casefold()
        )
        if (update.message.text.casefold().find(right_answer) == -1 and
                right_answer.find(update.message.text.casefold()) == -1):
            update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        else:
            count = int(redis_client.get(f'c{chat_id}').decode()) + 1
            redis_client.set(f'c{chat_id}', count)
            update.message.reply_text(f'Правильно! Поздравляю! Твой счёт: {count}.'
                                      'Для следующего вопроса нажми «Новый вопрос')
    else:
        update.message.reply_text(update.message.text)


def main() -> None:
    load_dotenv()
    token = os.getenv('TG_BOT_TOKEN')
    password = os.getenv('REDIS_PASSWORD')
    username = os.getenv('REDIS_USERNAME')
    host = os.getenv('REDIS_HOST')
    port = os.getenv('REDIS_PORT')
    redis_client = redis.Redis(host=host, password=password, port=port, username=username)
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        CommandHandler(
            "start",
            callback=lambda update, _: start(update, _, redis_client)
        )
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.text('/start'),
            callback=lambda update, _: echo(update, _, redis_client)
        )
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
