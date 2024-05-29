FROM python:3.11

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv --no-cache-dir

RUN pipenv install --system --deploy

COPY . .

ENTRYPOINT ["bash", "entrypoint.sh"]