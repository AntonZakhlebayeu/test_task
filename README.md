# Test Task API

### Quickstart

#### Clone the repository:

```sh
git clone https://github.com/AntonZakhlebayeu/test_task.git
cd test_task
```

#### Generate secret key

```sh
python -c 'import secrets; print("".join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)))'
```

#### Create `.env` file in project root and set environment variables for application: ::

```shell
touch .env
# Set Application port
echo "APPLICATION_PORT=8000" >> .env

# Configure Postgresql creds
echo "DB_ENGINE=django.db.backends.postgresql" >> .env
echo "DB_USER=postgres_user" >> .env
echo "DB_PASSWORD=strong_password_here" >> .env
echo "DB_NAME=b2broker_db" >> .env
echo "DB_PORT=5432" >> .env
echo "DB_HOST=db" >> .env

# Configure redis creds
echo "REDIS_DB=1" >> .env
echo "REDIS_HOST=redis" >> .env
echo "REDIS_PORT=6379" >> .env
echo "REDIS_USERNAME=redis_user" >> .env
echo "REDIS_PASSWORD=strong_password_here" >> .env

# Configure django secrets
echo "DJANGO_SECRET_KEY=<SECRET THAT YOU GENERATED ABOVE>" >> .env
echo "DJANGO_DEBUG=True" >> .env
echo "DJANGO_TEST=False" >> .env
echo "DJANGO_ADMIN_USERNAME=admin" >> .env
echo "DJANGO_ADMIN_EMAIL=admin@example.com" >> .env
echo "DJANGO_ADMIN_PASSWORD=super_secure_password" >> .env
echo "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1" >> .env
```

### Set up pre-commit hook

#### Code Quality Tools (via pre-commit)

This project uses pre-commit for consistent formatting and linting:

- black — code formatter

- isort — import sorting

- flake8 — linting

- pytest — tests (in pre-push hook)

#### Install hooks:

```sh
pre-commit install
```

#### Set up docker container

```bash
docker-compose up -d --build
```

### Check Swagger Documentation

You can access the automatically generated Swagger documentation for the API at http://localhost:${APPLICATION_PORT}/api/docs/

### Tests

This project uses `pytest` for testing.

#### Run the tests using Poetry

```sh
poetry install
poetry run pytest tests
```

#### Run tests using docker

```sh
docker-compose up pytest
```
