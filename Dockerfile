FROM python:3.10.4
WORKDIR /attendance
COPY ./requirements.txt /attendance/requirements.txt
RUN pip install -r /attendance/requirements.txt
COPY ./app /attendance/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]