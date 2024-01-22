import os
import redis
import vk_api
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from parse_quiz_files import parse_quiz_files
from receive_quest import choose_quest


def send_message(event, text, **kwargs):
    vk = kwargs['vk']
    keyboard = kwargs['keyboard']
    vk.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )


def begin(event, **kwargs):
    vk = kwargs['vk']
    keyboard = kwargs['keyboard']
    message = 'Давай сыграем. Жми "Новый вопрос"'
    send_message(event, message, vk=vk, keyboard=keyboard)


def give_up(event, **kwargs):
    quiz = kwargs['quiz']
    vk = kwargs['vk']
    keyboard = kwargs['keyboard']
    chat_id = event.user_id
    redis_client = kwargs['redis_client']
    full_answer = redis_client.get(f'a{chat_id}').decode()
    count = int(redis_client.get(f'c{chat_id}').decode())
    right_answer = full_answer if full_answer else 'Ты не выбрал вопрос'
    question, answer = choose_quest(quiz)
    redis_client.set(f'a{chat_id}', answer)
    message = f'Правильный ответ: {right_answer}\nТвой счёт = {count}\nСледующий вопрос:\n{question}'
    send_message(event, message, vk=vk, keyboard=keyboard)


def new_question(event, **kwargs):
    quiz = kwargs['quiz']
    vk = kwargs['vk']
    keyboard = kwargs['keyboard']
    chat_id = event.user_id
    redis_client = kwargs['redis_client']
    question, answer = choose_quest(quiz)
    redis_client.set(f'a{chat_id}', answer)
    message = f'{question}'
    send_message(event, message, vk=vk, keyboard=keyboard)


def count(event, **kwargs):
    vk = kwargs['vk']
    keyboard = kwargs['keyboard']
    chat_id = event.user_id
    redis_client = kwargs['redis_client']
    count = int(redis_client.get(f'c{chat_id}').decode())
    message = f'Твой счёт: {count}'
    send_message(event, message, vk=vk, keyboard=keyboard)


def answer(event, **kwargs):
    vk = kwargs['vk']
    keyboard = kwargs['keyboard']
    chat_id = event.user_id
    redis_client = kwargs['redis_client']
    full_answer = redis_client.get(f'a{chat_id}').decode()
    if not full_answer:
        message = 'Зачем зря писать? Жми "Новый вопрос"'
        send_message(event, message, vk=vk, keyboard=keyboard)

    right_answer = min(
        full_answer.split('(')[0].casefold(),
        full_answer.split('.')[0].casefold()
    )
    if (event.text.casefold().find(right_answer) == -1 and
            right_answer.find(event.text.casefold()) == -1):
        message = 'Неправильно… Попробуешь ещё раз?'
        send_message(event, message, vk=vk, keyboard=keyboard)
    else:
        count = int(redis_client.get(f'c{chat_id}').decode()) + 1
        redis_client.set(f'c{chat_id}', count)
        message = f'Правильно! Поздравляю! Твой счёт: {count}. '
        f'Для следующего вопроса нажми "Новый вопрос"'
        send_message(event, message, vk=vk, keyboard=keyboard)


def main():
    load_dotenv()
    quiz_files_path = os.getenv('QUIZ_FILES_PATH', 'quiz-questions')
    quiz = parse_quiz_files(quiz_files_path)
    token = os.getenv('VK_KEY')
    password = os.getenv('REDIS_PASSWORD')
    username = os.getenv('REDIS_USERNAME')
    host = os.getenv('REDIS_HOST')
    port = os.getenv('REDIS_PORT')
    redis_client = redis.Redis(host=host, password=password, port=port, username=username)
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Начать':
                begin(event, redis_client=redis_client, vk=vk, keyboard=keyboard)
            elif event.text == 'Сдаться':
                give_up(event, quiz=quiz, redis_client=redis_client, vk=vk, keyboard=keyboard)
            elif event.text == 'Новый вопрос':
                new_question(event, quiz=quiz, redis_client=redis_client, vk=vk, keyboard=keyboard)
            elif event.text == 'Мой счёт':
                count(event, redis_client=redis_client, vk=vk, keyboard=keyboard)
            else:
                answer(event, redis_client=redis_client, vk=vk, keyboard=keyboard)


if __name__ == '__main__':
    main()
