import random


def choose_quest(quiz):
    random_pair = random.choice(quiz)
    question = random_pair['question']
    answer = random_pair['answer']
    return question, answer
