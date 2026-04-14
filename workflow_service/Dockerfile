FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY workflow_service /app/workflow_service
COPY functions /app/functions

WORKDIR /app/workflow_service

CMD ["python", "app.py"]

EXPOSE 5002