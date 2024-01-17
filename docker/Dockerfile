# Указываем базовый образ, который содержит Python
FROM python:3.11

# Установка curl и утилиты для скачивания и установки Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Создаем и переходим в рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости проекта (файлы pyproject.toml и poetry.lock) в контейнер
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости проекта через Poetry
RUN poetry config virtualenvs.create false && poetry install --no-root

# Копируем все файлы проекта в контейнер
COPY . .

# Указываем команду, которая будет выполняться при запуске контейнера
CMD ["python", "main.py"]
