FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["sh", "-c", "python bot.py & gunicorn -b 0.0.0.0:8080 app:app"]
