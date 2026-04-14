FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY presentation_service /app/presentation_service

WORKDIR /app/presentation_service

CMD ["python", "app.py"]

EXPOSE 5000