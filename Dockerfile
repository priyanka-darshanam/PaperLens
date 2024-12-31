FROM python:3.11-slim

WORKDIR /app

COPY . /app/
COPY .env /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install openai faiss-cpu matplotlib pandas

EXPOSE 4000

CMD ["streamlit", "run", "main.py", "--server.port", "4000", "--server.address", "0.0.0.0"]
