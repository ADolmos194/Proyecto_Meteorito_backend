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
def listar_clientes(request):
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Clientes no encontradas",
        "message_user": "Clientes no encontradas",
        "data": [],
    }

    if request.method == "GET":
        try:

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id,
                        c.tipodocumento_id,
                        c.nro_documento,
                        c.nombre_completo,
                        c.correo_electronico,
                        c.nro_celular,
                        c.estado_id,
                        TO_CHAR(c.fecha_creacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_creacion,
                        TO_CHAR(c.fecha_modificacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_modificacion
                    FROM Clientes c
                    WHERE c.estado_id IN (1, 2)
                    ORDER BY c.id DESC
                    """
                )
                dic_clientes = ConvertirQueryADiccionarioDato(cursor)
                cursor.close()


            dic_response.update(
                {
                    "code": 200,
                    "status": "success",
                    "message_user": "Clientes obtenidas correctamente",
                    "message": "Clientes obtenidas correctamente",
                    "data": dic_clientes,
                }
            )
            return JsonResponse(dic_response, status=200)

        except DatabaseError as e:
            logger.error(f"Error al listar los clientes: {str(e)}")
            dic_response.update(
                {"message": "Error al listar los clientes", "data": str(e)}
            )
            return JsonResponse(dic_response, status=500)

    return JsonResponse([], safe=False, status=status.HTTP_200_OK)

@api_view(["POST"])
@transaction.atomic
def crear_cliente(request):
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Error al crear al cliente",
        "message_user": "Error al crear al cliente",
        "data": [],
    }

    if request.method == "POST":
        try:

            data = json.loads(request.body)
            data["estado"] = 1
            data["fecha_creacion"] = datetime.now()
            data["fecha_modificacion"] = datetime.now()
            
            estado_nombre = obtener_nombre_por_id('Estado', data["estado"])

            serializer = ClientesSerializer(data=data)

            if serializer.is_valid():

                with connection.cursor() as cursor:

                    nro_documento = data["nro_documento"]
                    nombre_completo = data["nombre_completo"]
                    cursor.execute("SELECT nro_documento, nombre_completo FROM clientes WHERE (nro_documento='{0}' or nombre_completo='{1}')  and estado_id IN (1, 2)".format(nro_documento, nombre_completo))

                    if (len(cursor.fetchall())>0):
                        dic_response.update(
                            {"message_user": "Ya existe un cliente con el mismo N° de documento o Nombre ", "message": "Ya hay un dato existente."}
                        )
                        return JsonResponse(dic_response, status=400)
                    
                    cursor.close()
                    
                serializer.save()
            
                dic_response.update(
                    {
                        "code": 201,
                        "status": "success",
                        "message_user": "Cliente creado exitosamente",
                        "message": "Cliente creado exitosamente",
                        "data": serializer.data
                    }
                )

                logger.info(
                    f"Cliente creado exitosamente: {data['nro_documento']} - {data['nombre_completo']} - {estado_nombre} (ID: {serializer.data['id']})"
                )
                
                return JsonResponse(dic_response, status=201)

            dic_response.update(
                {
                    "data": serializer.errors,
                }
            )
            return JsonResponse(dic_response, status=400)

        except Exception as e:
            logger.error(f"Error inesperado al crear al cliente: {str(e)}")
            dic_response.update(
                {"message_user": "Error inesperado", "data": {"error": str(e)}}
            )
            return JsonResponse(dic_response, status=500)

    return Response([], status=status.HTTP_200_OK)


@api_view(["PUT"])
@transaction.atomic
def actualizar_cliente(request, id):
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Error al actualizar el cliente",
        "message_user": "Error al actualizar el cliente",
        "data": [],
    }

    if request.method == "PUT":
        try:
            data = json.loads(request.body)            
            data["fecha_modificacion"] = datetime.now()

            estado_nombre = obtener_nombre_por_id('Estado', data["estado"])
            
            try:
                queryset = Clientes.objects.using('default').get(id=id)
            except Clientes.DoesNotExist:
                return JsonResponse(dic_response, safe=False, status=status.HTTP_404_NOT_FOUND)

            serializer = ClientesSerializer(queryset, data=data)

            if serializer.is_valid():
                
                with connection.cursor() as cursor:

                    nro_documento = data["nro_documento"]
                    nombre_completo = data["nombre_completo"]
                    estado = data["estado"]
                    cursor.execute("SELECT nro_documento, nombre_completo FROM Clientes WHERE (nro_documento='{0}' or nombre_completo='{1}')  and estado_id = {2} and id <> {3}".format(nro_documento, nombre_completo, estado, id))

                    if (len(cursor.fetchall())>0):
                        dic_response.update(
                            {"message_user": "Ya existe un cliente con el mismo n° de documento o nombre completo", "message": "Ya hay un dato existente."}
                        )
                        return JsonResponse(dic_response, status=400)
                    
                    cursor.close()
                    
                serializer.save()

                dic_response.update(
                    {
                        "code": 200,
                        "status": "success",
                        "message_user": "Cliente actualizado exitosamente",
                        "message": "Cliente actualizado exitosamente",
                        "data": serializer.data
                    }
                )
                logger.info(
                    f"Cliente actualizado exitosamente: {nro_documento} - {nombre_completo} - {estado_nombre} (ID: {id})"
                )
                return JsonResponse(dic_response, status=200)

            dic_response.update(
                {
                    "message_user": "Datos inválidos.",
                    "data": serializer.errors,
                }
            )
            return JsonResponse(dic_response, status=400)

        except Exception as e:
            logger.error(f"Error inesperado al actualizar el cliente: {str(e)}")
            dic_response.update(
                {"message_user": "Error inesperado", "data": {"error": str(e)}}
            )
            return JsonResponse(dic_response, status=500)

    return JsonResponse([], status=200)


@api_view(["DELETE"])
@transaction.atomic
def eliminar_cliente(request, id):
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Error al eliminar el cliente",
        "message_user": "Error al eliminar el cliente",
        "data": [],
    }

    if request.method == "DELETE":
        try:
            data = {"estado": 3}        
            try:
                queryset = Clientes.objects.using('default').get(id=id)
                queryset.estado= Estado.objects.using('default').get(id=data["estado"])
                queryset.fecha_modificacion= datetime.now()
                queryset.save()
                serializer = ClientesSerializer(queryset)

                dic_response.update(
                    {
                        "code": 200,
                        "status": "success",
                        "message_user": "Cliente eliminado lógicamente",
                        "message": "Cliente eliminado lógicamente",
                        "data": serializer.data,
                    }
                )

                logger.info(f"Cliente eliminado logicamente: (ID: {id})")
                return JsonResponse(dic_response, status=200)

            except Clientes.DoesNotExist:
                return JsonResponse(dic_response, safe=False, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error inesperado al eliminar el cliente: {str(e)}")
            dic_response["message"] = "Error inesperado"
            return JsonResponse(dic_response, status=500)

    return JsonResponse(dic_response, status=200)

