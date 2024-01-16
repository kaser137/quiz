import os
import redis
import vk_api
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from receiving_quest import choosing_quest


def make_keyboard():
    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)
    return keyboard


def main():
    load_dotenv()
    token = os.getenv('VK_KEY')
    password = os.getenv('REDIS_PASSWORD')
    username = os.getenv('REDIS_USERNAME')
    host = os.getenv('REDIS_HOST')
    port = os.getenv('REDIS_PORT')
    redis_client = redis.Redis(host=host, password=password, port=port, username=username)
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    keyboard = make_keyboard()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            chat_id = event.user_id
            full_answer = redis_client.get(f'a{chat_id}').decode()
            if not redis_client.get(f'c{chat_id}'):
                redis_client.set(f'c{chat_id}', 0)

            if event.text == 'Начать':
                vk.messages.send(
                    user_id=event.user_id,
                    message='Давай сыграем. Жми "Новый вопрос"',
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard()
                )

            elif event.text == 'Сдаться':
                count = int(redis_client.get(f'c{chat_id}').decode())
                right_answer = redis_client.get(f'a{chat_id}').decode() if redis_client.get(f'a{chat_id}') else (
                    'Ты не выбрал вопрос')
                question, answer = choosing_quest()
                redis_client.set(f'a{chat_id}', answer)
                redis_client.set(f'c{chat_id}', 0)
                vk.messages.send(
                    user_id=event.user_id,
                    message=f'Правильный ответ: {right_answer}\nТвой счёт = {count}\nСледующий вопрос:\n{question}',
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard()
                )

            elif event.text == 'Новый вопрос':
                question, answer = choosing_quest()
                redis_client.set(f'a{chat_id}', answer)
                vk.messages.send(
                    user_id=event.user_id,
                    message=f'{question}',
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard()
                )

            elif event.text == 'Мой счёт':
                count = int(redis_client.get(f'c{chat_id}').decode())
                vk.messages.send(
                    user_id=event.user_id,
                    message=f'Твой счёт: {count}',
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard()
                )

            elif full_answer:
                right_answer = min(
                    full_answer.split('(')[0].casefold(),
                    full_answer.split('.')[0].casefold()
                )
                if (event.text.casefold().find(right_answer) == -1 and
                        right_answer.find(event.text.casefold()) == -1):
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Неправильно… Попробуешь ещё раз?',
                        random_id=get_random_id(),
                        keyboard=keyboard.get_keyboard()
                    )
                else:
                    count = int(redis_client.get(f'c{chat_id}').decode()) + 1
                    redis_client.set(f'c{chat_id}', count)
                    vk.messages.send(
                        user_id=event.user_id,
                        message=f'Правильно! Поздравляю! Твой счёт: {count}. '
                                f'Для следующего вопроса нажми "Новый вопрос"',
                        random_id=get_random_id(),
                        keyboard=keyboard.get_keyboard()
                    )

            else:
                vk.messages.send(
                    user_id=event.user_id,
                    message='Зачем зря писать? Жми "Новый вопрос"',
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard()
                )


if __name__ == '__main__':
    main()
