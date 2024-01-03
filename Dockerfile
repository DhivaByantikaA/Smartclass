FROM python:3.11-slim-bookworm

WORKDIR /app

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./ /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]