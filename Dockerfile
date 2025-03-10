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

# Instalar netcat para verificar la base de datos
RUN apt-get update && apt-get install -y netcat

# Copiar el script wait-for-it.sh y darle permisos de ejecución
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Esperar a que la base de datos esté lista antes de migrar
RUN /wait-for-it.sh databaseswtesis:5432 --strict --timeout=30 -- python manage.py migrate

# Ejecutar la recolección de archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponer el puerto
EXPOSE 8000

# Comando de inicio
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--threads=2"]

