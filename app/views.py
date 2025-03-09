import json
import logging
import pandas as pd
from django.http import JsonResponse

import psycopg2
from rest_framework import status
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection, transaction, DatabaseError

from .serializer import *
from .models import *

# Configuración del logger para manejar errores
logger = logging.getLogger(__name__)

# Función para convertir un cursor de base de datos a un diccionario
def ConvertirQueryADiccionarioDato(cursor):
    """
    Convierte el resultado de una consulta SQL en un diccionario, donde las claves son
    los nombres de las columnas y los valores son los datos de las filas.

    :param cursor: Cursor de la base de datos que contiene los resultados de la consulta.
    :return: Una lista de diccionarios donde cada diccionario representa una fila de la consulta.
    """
    columna = [desc[0] for desc in cursor.description]
    return [dict(zip(columna, fila)) for fila in cursor.fetchall()]

# Función para obtener el nombre de un registro dado su ID
def obtener_nombre_por_id(tabla, id):
    """
    Obtiene el nombre de un registro de una tabla específica en la base de datos por su ID.

    :param tabla: Nombre de la tabla de donde obtener el nombre.
    :param id: ID del registro cuyo nombre se desea obtener.
    :return: El nombre del registro o un mensaje de error si no se encuentra el registro.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT nombre FROM {tabla} WHERE id = %s", [id])
            resultado = cursor.fetchone()
            if resultado:
                return resultado[0]
            else:
                return "Desconocido"
    except Exception as e:
        logger.error(f"Error al obtener el nombre de {tabla} con id {id}: {str(e)}")
        return "Error al obtener nombre"

    
# Vista para listar los tipos de documentos, usando una consulta SQL directa
@api_view(["GET"])
@transaction.atomic
def listar_tipodocumento(request):
    """
    Lista los tipos de documentos de la base de datos. Realiza una consulta SQL para obtener los tipos de documento con IDs específicos.
    Devuelve una respuesta en formato JSON con los tipos de documentos encontrados.

    :param request: La solicitud HTTP GET que activa esta vista.
    :return: Una respuesta JSON con los tipos de documentos encontrados o un error.
    """
    
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Tipos documentos no encontradas",
        "message_user": "Tipos documentos no encontradas",
        "data": [],
    }

    if request.method == "GET":
        try:
            
            # Realiza la consulta SQL para obtener los tipos de documentos
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        td.id,
                        td.nombre,
                        TO_CHAR(td.fecha_creacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_creacion,
                        TO_CHAR(td.fecha_modificacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_modificacion
                    FROM Tipodocumento td
                    WHERE td.id IN (1, 2)
                    ORDER BY td.id DESC
                    """
                )
                dic_tipodocumento = ConvertirQueryADiccionarioDato(cursor)
                cursor.close()

            # Actualiza la respuesta con los datos obtenidos
            dic_response.update(
                {
                    "code": 200,
                    "status": "success",
                    "message_user": "Tipos documentos obtenidas correctamente",
                    "message": "Tipos documentos obtenidas correctamente",
                    "data": dic_tipodocumento,
                }
            )
            return JsonResponse(dic_response, status=200)

        except DatabaseError as e:
            logger.error(f"Error al listar los Tipos documentos: {str(e)}")
            dic_response.update(
                {"message": "Error al listar los Tipos documentos", "data": str(e)}
            )
            return JsonResponse(dic_response, status=500)

    # Retorna una respuesta vacía si el método no es GET
    return JsonResponse([], safe=False, status=status.HTTP_200_OK)


@api_view(["GET"])
@transaction.atomic
def listar_estado(request):
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Estado no encontradas",
        "message_user": "Estado no encontradas",
        "data": [],
    }

    if request.method == "GET":
        try:

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        e.id,
                        e.nombre,
                        TO_CHAR(e.fecha_creacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_creacion,
                        TO_CHAR(e.fecha_modificacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_modificacion
                    FROM Estado e
                    WHERE e.id IN (1, 2)
                    ORDER BY e.id DESC
                    """
                )
                dic_estado = ConvertirQueryADiccionarioDato(cursor)
                cursor.close()


            dic_response.update(
                {
                    "code": 200,
                    "status": "success",
                    "message_user": "Estados obtenidas correctamente",
                    "message": "Estados obtenidas correctamente",
                    "data": dic_estado,
                }
            )
            return JsonResponse(dic_response, status=200)

        except DatabaseError as e:
            logger.error(f"Error al listar el estado: {str(e)}")
            dic_response.update(
                {"message": "Error al listar el estado", "data": str(e)}
            )
            return JsonResponse(dic_response, status=500)

    return JsonResponse([], safe=False, status=status.HTTP_200_OK)

