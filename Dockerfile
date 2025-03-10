# Usa la imagen oficial de Python 3.8 como base
FROM python:3.8

# Establece la variable de entorno PYTHONUNBUFFERED para ver logs en tiempo real
ENV PYTHONUNBUFFERED 1

# Crea un directorio para la aplicación
RUN mkdir /code_free

# Establece el directorio de trabajo
WORKDIR /code_free

# Crear un entorno virtual dentro del contenedor
RUN python -m venv /opt/venv

# Activar el entorno virtual
ENV PATH="/opt/venv/bin:$PATH"

# Copiar dependencias e instalarlas dentro del entorno virtual
COPY requirements.txt /code_free/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente al contenedor
COPY . /code_free/

# Exponer el puerto de Django (generalmente 8000)
EXPOSE 8000

# Comando para ejecutar Django con Gunicorn (puedes cambiarlo si usas otro servidor)
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
