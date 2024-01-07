FROM python:3.11-slim
RUN mkdir "quiz_bots"
WORKDIR /quiz_bots
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["bash", "bot_wrapper_script.sh"]
