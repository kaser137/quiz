import logging
import os
import redis
import telegram
from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from functools import wraps
from dotenv import load_dotenv

from parse_quiz_files import parse_quiz_files
from receive_quest import choose_quest

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

MESSAGE = 0


@send_typing_action
def start(update, _, redis_client) -> None:
    chat_id = update.message.chat_id
    if not redis_client.get(f'c{chat_id}'):
        redis_client.set(f'c{chat_id}', 0)
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт', 'Закончить'],]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Здравствуйте', reply_markup=reply_markup)
    logger.info('Quiz is started')
    return MESSAGE


@send_typing_action
def new_question(update, _, redis_client, quiz):
    chat_id = update.message.chat_id
    question, answer = choose_quest(quiz)
    redis_client.set(f'a{chat_id}', answer)
    update.message.reply_text(question)
    logger.info(f'{update.message.from_user.first_name} requests the new question')
    return MESSAGE


@send_typing_action
def count(update, _, redis_client):
    chat_id = update.message.chat_id
    count = redis_client.get(f'c{chat_id}').decode()
    update.message.reply_text(f' Твой счёт: {count}')
    logger.info(f'{update.message.from_user.first_name} requests his count')
    return MESSAGE


@send_typing_action
def give_up(update, _, redis_client, quiz):
    chat_id = update.message.chat_id
    full_answer = redis_client.get(f'a{chat_id}').decode()
    count = int(redis_client.get(f'c{chat_id}').decode())
    right_answer = full_answer if full_answer else 'Ты не выбрал вопрос'
    question, answer = choose_quest(quiz)
    redis_client.set(f'a{chat_id}', answer)
    update.message.reply_text(f'Правильный ответ: {right_answer}\nТвой счёт = {count}\nСледующий вопрос:\n{question}')
    logger.info(f'{update.message.from_user.first_name} gave up')
    return MESSAGE


@send_typing_action
def answer_handler(update, _, redis_client):
    chat_id = update.message.chat_id
    full_answer = redis_client.get(f'a{chat_id}').decode()
    if full_answer:
        right_answer = min(
            full_answer.split('(')[0].casefold(),
            full_answer.split('.')[0].casefold()
        )
        if (update.message.text.casefold().find(right_answer) == -1 and
                right_answer.find(update.message.text.casefold()) == -1):
            update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        else:
            count = int(redis_client.get(f'c{chat_id}').decode()) + 1
            redis_client.set(f'c{chat_id}', count)
            update.message.reply_text(f'Правильно! Поздравляю! Твой счёт: {count}.'
                                      'Для следующего вопроса нажми "Новый вопрос"')

    else:
        update.message.reply_text('Зачем зря писать? Жми "Новый вопрос"')
    logger.info(f'{update.message.from_user.first_name} is trying to take the answer')
    return MESSAGE


@send_typing_action
def end_quiz(update, _, redis_client):
    chat_id = update.message.chat_id
    count = int(redis_client.get(f'c{chat_id}').decode())
    redis_client.set(f'a{chat_id}', '')
    update.message.reply_text(f'Игра окончена. Твой счёт: {count}.\n'
                              f'Нажми /start, чтобы ещё сыграть')
    logger.info(f'{update.message.from_user.first_name} has finished')
    return ConversationHandler.END


def main() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    load_dotenv()
    quiz_files_path = os.getenv('QUIZ_FILES_PATH', 'quiz-questions')
    quiz = parse_quiz_files(quiz_files_path)
    token = os.getenv('TG_BOT_TOKEN')
    password = os.getenv('REDIS_PASSWORD')
    username = os.getenv('REDIS_USERNAME')
    host = os.getenv('REDIS_HOST')
    port = os.getenv('REDIS_PORT')
    redis_client = redis.Redis(host=host, password=password, port=port, username=username)
    updater = Updater(token)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                'start',
                callback=lambda update, _: start(update, _, redis_client)
            ),
        ],

        states={
            MESSAGE: [
                MessageHandler(
                    Filters.text & ~Filters.text(['/start', 'Новый вопрос', 'Сдаться', 'Мой счёт', 'Закончить']),
                    callback=lambda update, _: answer_handler(update, _, redis_client)),
                MessageHandler(
                    Filters.text('Новый вопрос'),
                    callback=lambda update, _: new_question(update, _, redis_client, quiz)),
                MessageHandler(
                    Filters.text('Мой счёт'),
                    callback=lambda update, _: count(update, _, redis_client)),
                MessageHandler(
                    Filters.text('Сдаться'),
                    callback=lambda update, _: give_up(update, _, redis_client, quiz))
            ]
        },

        fallbacks=[MessageHandler(
            Filters.text('Закончить'),
            callback=lambda update, _: end_quiz(update, _, redis_client)),
        ]
    )
    dispatcher.add_handler(
        conv_handler
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
