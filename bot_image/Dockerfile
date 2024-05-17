FROM python:3.10-alpine
WORKDIR /bot
COPY . .
EXPOSE 5055
COPY requirements.txt requirements.txt
RUN apk update
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
