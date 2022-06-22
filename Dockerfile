FROM python:3.7
ENV TZ=Europe/Moscow
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]