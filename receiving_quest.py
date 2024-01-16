import os
import random
from dotenv import load_dotenv


def choosing_quest(quiz_files_path):
    files_list = sorted(os.listdir(quiz_files_path))
    file_for_open = random.choice(files_list)
    quiz = []
    with open(f'{quiz_files_path}/{file_for_open}', encoding='KOI8-R') as quiz_file:
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
    random_pair = random.choice(quiz)
    question = random_pair['question']
    answer = random_pair['answer']
    return question, answer


def main():
    load_dotenv()
    quiz_files_path = os.getenv('QUIZ_FILES_PATH', 'quiz-questions')
    choosing_quest(quiz_files_path)


if __name__ == '__main__':
    main()
