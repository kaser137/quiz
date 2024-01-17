import random
from parse_quiz_files import QUIZ


def choose_quest():
    random_pair = random.choice(QUIZ)
    question = random_pair['question']
    answer = random_pair['answer']
    return question, answer


if __name__ == '__main__':
    choose_quest()
