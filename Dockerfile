# Usa la imagen oficial de Python 3.8 como base
FROM python:3.8

# Establece la variable de entorno PYTHONUNBUFFERED para evitar que Python almacene los logs en búfer
# Esto es útil para ver los logs de manera inmediata durante el desarrollo
ENV PYTHONUNBUFFERED 1

# Crea un directorio llamado /code_free dentro del contenedor para alojar el código
RUN mkdir /code_free

# Establece el directorio de trabajo dentro del contenedor a /code_free
# Todos los comandos posteriores se ejecutarán en este directorio
WORKDIR /code_free

# Copia el archivo requirements.txt del directorio local al directorio /code_free del contenedor
COPY requirements.txt /code_free/

# Instala las dependencias listadas en requirements.txt utilizando pip
RUN python -m pip install -r requirements.txt

# Copia todo el código fuente del directorio local al directorio /code_free del contenedor
COPY . /code_free/
