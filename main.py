import os
import random

files_list = sorted(os.listdir('quiz-questions'))
file_for_open = random.choice(files_list)
quiz = []
with open(f'quiz-questions/{file_for_open}', encoding='KOI8-R') as quiz_file:
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
# FOR MAKING WHOLE LIST OF PAIRS=====================================================================================
# for file in files_list:
#     with open(f'quiz-questions/{file}', encoding='KOI8-R') as quiz_file:
#         components = quiz_file.read().split('\n\n')
#         i = 0
#         while i < len(components) - 1:
#             if components[i].strip().startswith('Вопрос'):
#                 quiz.append({
#                     'question': components[i].strip(),
#                     'answer': components[i + 1].strip()
#                 })
#                 i += 2
#             else:
#                 i +=1
# ====================================================================================================================
random_pair = random.choice(quiz)
print(random_pair['question'], '\n\n', random_pair['answer'])
print(len(files_list))
