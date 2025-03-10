# Usa la imagen oficial de Python 3.8 como base
FROM python:3.8

# Establece la variable de entorno PYTHONUNBUFFERED para ver logs en tiempo real
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo (esto crea el directorio automáticamente)
WORKDIR /code_free

# Crear un entorno virtual dentro del contenedor
RUN python -m venv /opt/venv

# Activar el entorno virtual
ENV PATH="/opt/venv/bin:$PATH"

# Copiar dependencias e instalarlas dentro del entorno virtual
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente al contenedor
COPY . .

# Exponer el puerto de Django
EXPOSE 8000

# Comando para ejecutar Django con Gunicorn
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--threads=2"]
