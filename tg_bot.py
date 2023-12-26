import logging
import os

import telegram
from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from functools import wraps
from dotenv import load_dotenv

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
def start(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    chat_id = update.message.chat_id
    update.message.bot.send_message(chat_id=chat_id,
                                    text='Здравствуйте',
                                    reply_markup=reply_markup)


@send_typing_action
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def main() -> None:
    load_dotenv()
    token = os.getenv('TG_BOT_TOKEN')
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.text('/start'), echo))

    updater.start_polling()
    updater.idle()


# custom_keyboard = [['top-left', 'top-right'],
#                    ['bottom-left', 'bottom-right']]
# reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
# bot.send_message(chat_id=chat_id,
#                  text="Custom Keyboard Test",
#                  reply_markup=reply_markup)

if __name__ == '__main__':
    main()
