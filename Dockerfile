# Usa Python 3.10 como imagen base
FROM python:3.10

# Establece la variable de entorno para ver logs en tiempo real
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo
WORKDIR /code_free

# Crear y activar entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente al contenedor
COPY . .

# Exponer el puerto
EXPOSE 8000

# Asegurar que la migración y la recolección de archivos estáticos se realicen antes de iniciar
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Comando de inicio
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--threads=2"]

