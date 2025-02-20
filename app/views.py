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

logger = logging.getLogger(__name__)

# Create your views here.
def ConvertirQueryADiccionarioDato(cursor):
    columna = [desc[0] for desc in cursor.description]
    return [dict(zip(columna, fila)) for fila in cursor.fetchall()]

def obtener_nombre_por_id(tabla, id):
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


@api_view(["GET"])
@transaction.atomic
def listar_tipodocumento(request):
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Tipos documentos no encontradas",
        "message_user": "Tipos documentos no encontradas",
        "data": [],
    }

    if request.method == "GET":
        try:

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

    return JsonResponse([], safe=False, status=status.HTTP_200_OK)
