FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50

CMD [ "python3", "./app.py" ]

# CMD ["sh", "-c", "tail -f /dev/null"]
