import os
import random
from dotenv import load_dotenv


load_dotenv()
quiz_files_path = os.getenv('QUIZ_FILES_PATH', 'quiz-questions')
files_list = sorted(os.listdir(quiz_files_path))
print(len(files_list))
quiz = []
for file in files_list:
    with open(f'{quiz_files_path}/{file}', encoding='KOI8-R') as quiz_file:
        components = quiz_file.read().split('\n\n')
        i = 0
    while i < len(components) - 1:
        if components[i].strip().startswith('Вопрос'):
            quiz.append({
                'question': components[i].strip(),
                'answer': components[i + 1].strip()
            })
            i += 2
        else:
            i += 1


def choosing_quest():
    random_pair = random.choice(quiz)
    question = random_pair['question']
    answer = random_pair['answer']
    return question, answer
