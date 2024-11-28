FROM python:3.12.6-slim
WORKDIR /TTapp
COPY . /TTapp
ENV PYTHONPATH /TTapp
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "-m", "src.app"]