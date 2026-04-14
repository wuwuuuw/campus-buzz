FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY data_service /app/data_service

WORKDIR /app/data_service

CMD ["python", "app.py"]

EXPOSE 5001
