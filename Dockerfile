FROM python:3-slim
WORKDIR /app
RUN pip install minio
COPY code.py .
ENV MINIO_ACCESS_KEY=user1234
ENV MINIO_SECRET_KEY=password
CMD ["python", "code.py"]


