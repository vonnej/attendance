FROM python:3.10.4
RUN apt-get update && apt-get upgrade -y && pip3 install pipenv
WORKDIR /attendance
COPY . .
RUN pipenv install --system --deploy
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]