FROM python:3.10

RUN pip install "poetry~=1.7"

WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi
COPY . /app

CMD ["gunicorn", "--bind", "0.0.0.0:80", "main:app"]
