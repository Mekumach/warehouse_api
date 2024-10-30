# Используем официальный образ Python
FROM python:3.11.5

# Устанавливаем переменную окружения для того, чтобы вывод был сразу виден в логах
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию в контейнере
WORKDIR /warehpuse_api

# Копируем файлы проекта в контейнер
COPY . /warehpuse_api

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду запуска приложения
CMD ["uvicorn", "warehouse_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
