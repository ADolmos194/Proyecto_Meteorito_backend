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


def ConvertirQueryADiccionarioDato(cursor):
    """
    Convierte el resultado de una consulta SQL (cursor) en una lista de diccionarios,
    donde las claves son los nombres de las columnas y los valores son los datos obtenidos.

    :param cursor: cursor de la consulta ejecutada
    :return: Lista de diccionarios con los resultados de la consulta
    """
    columna = [desc[0] for desc in cursor.description]
    return [dict(zip(columna, fila)) for fila in cursor.fetchall()]

def obtener_nombre_por_id(tabla, id):
    """
    Obtiene el nombre correspondiente a un ID de una tabla específica.

    :param tabla: nombre de la tabla en la base de datos
    :param id: id del registro a buscar
    :return: Nombre correspondiente al ID si existe, o un mensaje de error si no se encuentra
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

################################# CRUD CLIENTES #################################
@api_view(["GET"])
@transaction.atomic
def listar_clientes(request):
    
    """
    Vista para listar los clientes. Filtra los clientes que están activos (estado_id 1 o 2).
    Retorna los datos del cliente en formato JSON.

    :param request: objeto HTTP que contiene la solicitud
    :return: Respuesta en formato JSON con los clientes listados
    """
    
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Clientes no encontradas",
        "message_user": "Clientes no encontradas",
        "data": [],
    }

    if request.method == "GET":
        try:
            
            # Realiza la consulta SQL para obtener a los clientes
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id,
                        c.tipodocumento_id,
                        td.nombre as tipodocumento_nombre,
                        c.nro_documento,
                        c.nombre_completo,
                        c.correo_electronico,
                        c.nro_celular,
                        c.estado_id,
                        TO_CHAR(c.fecha_creacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_creacion,
                        TO_CHAR(c.fecha_modificacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_modificacion
                    FROM Clientes c
                    LEFT JOIN Tipodocumento td ON c.tipodocumento_id = td.id
                    WHERE c.estado_id IN (1, 2)
                    ORDER BY c.id DESC
                    """
                )
                dic_clientes = ConvertirQueryADiccionarioDato(cursor)
                cursor.close()

            # Actualiza la respuesta con los datos obtenidos
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

    
    # Retorna una respuesta vacía si el método no es GET
    return JsonResponse([], safe=False, status=status.HTTP_200_OK)

@api_view(["POST"])
@transaction.atomic
def crear_cliente(request):
    
    """
    Vista para crear un nuevo cliente. Verifica si ya existe un cliente con el mismo número de documento o nombre completo.
    Si es válido, crea un nuevo cliente y guarda los datos en la base de datos.

    :param request: objeto HTTP que contiene la solicitud con los datos del nuevo cliente
    :return: Respuesta en formato JSON con el cliente creado o un mensaje de error
    """
    
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Error al crear al cliente",
        "message_user": "Error al crear al cliente",
        "data": [],
    }

    if request.method == "POST":
        try:
            # Cargar los datos enviados en el cuerpo de la solicitud (request body).
            data = json.loads(request.body)
        
            # Establecer valores predeterminados para los campos 'estado' y 'fecha' al momento de la creación.
            data["estado"] = 1  # Estado 'activo' por defecto
            data["fecha_creacion"] = datetime.now()  # Fecha de creación actual
            data["fecha_modificacion"] = datetime.now()  # Fecha de modificación actual

            # Obtener el nombre del estado a partir del ID (1 por defecto en este caso).
            estado_nombre = obtener_nombre_por_id('Estado', data["estado"])

            # Crear una instancia del serializador para validar los datos y convertirlos al formato requerido.
            serializer = ClientesSerializer(data=data)

            # Verificar si los datos son válidos según el serializador
            if serializer.is_valid():
            
                with connection.cursor() as cursor:
                    # Extraer los datos necesarios para la consulta de validación
                    nro_documento = data["nro_documento"]
                    nombre_completo = data["nombre_completo"]
                
                    # Realizar una consulta SQL para verificar si ya existe un cliente con el mismo número de documento
                    # o el mismo nombre completo y si el estado es 'activo' (1 o 2).
                    cursor.execute(
                        "SELECT nro_documento, nombre_completo FROM clientes WHERE (nro_documento='{0}' or nombre_completo='{1}') and estado_id IN (1, 2)".format(nro_documento, nombre_completo)
                    )

                    # Si ya existe un cliente con los mismos datos, retornar un mensaje de error.
                    if len(cursor.fetchall()) > 0:
                        dic_response.update(
                            {"message_user": "Ya existe un cliente con el mismo N° de documento o Nombre ", "message": "Ya hay un dato existente."}
                        )
                        return JsonResponse(dic_response, status=400)
                
                    cursor.close()
            
                # Si los datos son válidos y no hay conflictos con clientes existentes, proceder a guardar el nuevo cliente.
                serializer.save()

                # Actualizar la respuesta indicando que la creación fue exitosa.
                dic_response.update(
                    {
                        "code": 201,
                        "status": "success",
                        "message_user": "Cliente creado exitosamente",
                        "message": "Cliente creado exitosamente",
                        "data": serializer.data
                    }
                )

                # Log para informar la creación exitosa del cliente.
                logger.info(
                    f"Cliente creado exitosamente: {data['nro_documento']} - {data['nombre_completo']} - {estado_nombre} (ID: {serializer.data['id']})"
                )

                # Retornar la respuesta con el código de éxito y los datos del cliente creado.
                return JsonResponse(dic_response, status=201)

            # Si los datos no son válidos según el serializador, actualizar la respuesta con los errores de validación.
            dic_response.update(
                {
                    "data": serializer.errors,
                }
            )
            return JsonResponse(dic_response, status=400)

        except Exception as e:
            # En caso de un error inesperado, registrar el error y retornar una respuesta con el error.
            logger.error(f"Error inesperado al crear al cliente: {str(e)}")
            dic_response.update(
                {"message_user": "Error inesperado", "data": {"error": str(e)}}
            )
            return JsonResponse(dic_response, status=500)

    # Retorna una respuesta vacía si el método no es GET
    return Response([], status=status.HTTP_200_OK)


#EL de crear y con el de actualizar tienen casi todo la misma estructura solo cambia unas cosa pero es entendible :D 
@api_view(["PUT"])
@transaction.atomic
def actualizar_cliente(request, id):
    
    """
    Vista para actualizar los datos de un cliente existente.
    Verifica que no exista otro cliente con el mismo número de documento o nombre completo antes de realizar la actualización.

    :param request: objeto HTTP que contiene los datos para actualizar el cliente
    :param id: ID del cliente que se desea actualizar
    :return: Respuesta en formato JSON con los datos actualizados o un mensaje de error
    """
    
    # Estructura de la respuesta por defecto en caso de error
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Error al actualizar el cliente",
        "message_user": "Error al actualizar el cliente",
        "data": [],
    }

    # Verificamos si la solicitud es de tipo PUT
    if request.method == "PUT":
        try:
            # Cargamos los datos enviados en el cuerpo de la solicitud (JSON)
            data = json.loads(request.body)
            
            # Establecemos la fecha de modificación al momento de la actualización
            data["fecha_modificacion"] = datetime.now()

            # Obtenemos el nombre del estado del cliente para loguearlo
            estado_nombre = obtener_nombre_por_id('Estado', data["estado"])
            
            # Intentamos obtener el cliente con el ID proporcionado
            try:
                queryset = Clientes.objects.using('default').get(id=id)
            except Clientes.DoesNotExist:
                # Si no encontramos el cliente, retornamos un error 404
                return JsonResponse(dic_response, safe=False, status=status.HTTP_404_NOT_FOUND)

            # Usamos el serializer para validar los datos que queremos actualizar
            serializer = ClientesSerializer(queryset, data=data)

            if serializer.is_valid():
                # Usamos un cursor para verificar si ya existe un cliente con el mismo documento o nombre
                with connection.cursor() as cursor:
                    nro_documento = data["nro_documento"]
                    nombre_completo = data["nombre_completo"]
                    estado = data["estado"]
                    
                    # Ejecutamos la consulta para verificar si ya existe un cliente con el mismo documento o nombre, excluyendo el cliente actual
                    cursor.execute("SELECT nro_documento, nombre_completo FROM Clientes WHERE (nro_documento='{0}' or nombre_completo='{1}') and estado_id = {2} and id <> {3}".format(nro_documento, nombre_completo, estado, id))

                    # Si encontramos un cliente con el mismo número de documento o nombre, respondemos con un error
                    if len(cursor.fetchall()) > 0:
                        dic_response.update(
                            {"message_user": "Ya existe un cliente con el mismo n° de documento o nombre completo", "message": "Ya hay un dato existente."}
                        )
                        return JsonResponse(dic_response, status=400)

                    cursor.close()

                # Si los datos son válidos, guardamos los cambios en la base de datos
                serializer.save()
                
                # Actualizamos la respuesta con los datos obtenidos
                dic_response.update(
                    {
                        "code": 200,
                        "status": "success",
                        "message_user": "Cliente actualizado exitosamente",
                        "message": "Cliente actualizado exitosamente",
                        "data": serializer.data
                    }
                )

                # Logueamos la información de la actualización
                logger.info(
                    f"Cliente actualizado exitosamente: {nro_documento} - {nombre_completo} - {estado_nombre} (ID: {id})"
                )

                # Retornamos la respuesta con los datos actualizados del cliente
                return JsonResponse(dic_response, status=200)

            # Si los datos del serializer no son válidos, retornamos los errores
            dic_response.update(
                {
                    "message_user": "Datos inválidos.",
                    "data": serializer.errors,
                }
            )
            return JsonResponse(dic_response, status=400)

        except Exception as e:
            # Si ocurre algún error inesperado, lo registramos y retornamos un mensaje de error
            logger.error(f"Error inesperado al actualizar el cliente: {str(e)}")
            dic_response.update(
                {"message_user": "Error inesperado", "data": {"error": str(e)}}
            )
            return JsonResponse(dic_response, status=500)

    # Si el método no es PUT, retornamos una respuesta vacía con estado 200
    return JsonResponse([], status=200)


@api_view(["DELETE"])
@transaction.atomic
def eliminar_cliente(request, id):
    
    """
    Vista para eliminar lógicamente a un cliente. Cambia su estado a 'eliminado' (estado_id 3).
    
    Esta vista se encarga de actualizar el estado de un cliente en la base de datos, 
    cambiando su estado a 'eliminado' (estado_id 3). No se elimina físicamente el cliente de la base de datos, 
    sino que se realiza una eliminación lógica al cambiar su estado. La eliminación lógica permite mantener los registros 
    en la base de datos para futuros análisis o auditorías.
    
    :param request: Objeto HTTP que contiene la solicitud (en este caso, DELETE)
    :param id: ID del cliente que se desea eliminar (logicamente)
    :return: Respuesta en formato JSON con el cliente eliminado o un mensaje de error
    """
    
    # Estructura de la respuesta por defecto en caso de error
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Error al eliminar el cliente",
        "message_user": "Error al eliminar el cliente",
        "data": [],
    }

    # Verificamos si la solicitud es de tipo DELETE
    if request.method == "DELETE":
        try:
            # Asignamos el estado 3 para 'eliminado'
            data = {"estado": 3}        
            
            # Intentamos obtener el cliente de la base de datos utilizando su ID
            try:
                queryset = Clientes.objects.using('default').get(id=id)
                
                # Actualizamos el estado del cliente a 'eliminado' (estado_id = 3)
                queryset.estado = Estado.objects.using('default').get(id=data["estado"])
                queryset.fecha_modificacion = datetime.now()  # Actualizamos la fecha de modificación
                
                # Guardamos los cambios en la base de datos
                queryset.save()
                
                # Serializamos los datos del cliente actualizado
                serializer = ClientesSerializer(queryset)
                
                # Actualizamos la respuesta con los datos del cliente eliminado
                dic_response.update(
                    {
                        "code": 200,
                        "status": "success",
                        "message_user": "Cliente eliminado lógicamente",
                        "message": "Cliente eliminado lógicamente",
                        "data": serializer.data,
                    }
                )

                # Registramos un log informando que el cliente fue eliminado lógicamente
                logger.info(f"Cliente eliminado logicamente: (ID: {id})")
                
                # Retornamos la respuesta con los detalles del cliente eliminado
                return JsonResponse(dic_response, status=200)

            # Si no se encuentra el cliente con el ID proporcionado, se retorna un error 404
            except Clientes.DoesNotExist:
                return JsonResponse(dic_response, safe=False, status=status.HTTP_404_NOT_FOUND)

        # Manejo de errores inesperados durante la eliminación
        except Exception as e:
            logger.error(f"Error inesperado al eliminar el cliente: {str(e)}")
            dic_response["message"] = "Error inesperado"
            return JsonResponse(dic_response, status=500)

    # Si el método no es DELETE, retornamos la respuesta vacía
    return JsonResponse(dic_response, status=200)


#SOLO CLIENTES ACTIVOS
@api_view(["GET"])
@transaction.atomic
def listar_clientes_activos(request):
    
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Clientes activos no encontradas",
        "message_user": "Clientes activos no encontradas",
        "data": [],
    }

    if request.method == "GET":
        try:
            
            # Realiza la consulta SQL para obtener a los clientes activos
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id,
                        c.nombre_completo as nombre,
                        c.estado_id,
                        TO_CHAR(c.fecha_creacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_creacion,
                        TO_CHAR(c.fecha_modificacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_modificacion
                    FROM Clientes c
                    LEFT JOIN Tipodocumento td ON c.tipodocumento_id = td.id
                    WHERE c.estado_id IN (1)
                    ORDER BY c.id DESC
                    """
                )
                dic_clientes = ConvertirQueryADiccionarioDato(cursor)
                cursor.close()

            # Actualiza la respuesta con los datos obtenidos
            dic_response.update(
                {
                    "code": 200,
                    "status": "success",
                    "message_user": "Clientes activos obtenidas correctamente",
                    "message": "Clientes activos obtenidas correctamente",
                    "data": dic_clientes,
                }
            )
            return JsonResponse(dic_response, status=200)

        except DatabaseError as e:
            logger.error(f"Error al listar los clientes activos: {str(e)}")
            dic_response.update(
                {"message": "Error al listar los clientes activos", "data": str(e)}
            )
            return JsonResponse(dic_response, status=500)

    
    # Retorna una respuesta vacía si el método no es GET
    return JsonResponse([], safe=False, status=status.HTTP_200_OK)


################################# CRUD TESIS #################################
@api_view(["GET"])
@transaction.atomic
def listar_tesis(request):
        
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Tesis no encontradas",
        "message_user": "Tesis no encontradas",
        "data": [],
    }

    if request.method == "GET":
        try: 
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        t.id,
                        t.clientes_id,
                        c.nombre_completo,
                        t.nombre_tesis,
                        t.universidad,
                        t.usuario_plataforma,
                        t.clave_plataforma,
                        t.estado_id,
                        TO_CHAR(t.fecha_creacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_creacion,
                        TO_CHAR(t.fecha_modificacion, 'YYYY-MM-DD HH24:MI:SS') as fecha_modificacion
                    FROM Tesis t
                    LEFT JOIN Clientes c ON t.clientes_id = c.id
                    WHERE t.estado_id IN (1, 2)
                    ORDER BY t.id DESC
                    """
                )
                dic_tesis = ConvertirQueryADiccionarioDato(cursor)
                cursor.close()

            # Actualiza la respuesta con los datos obtenidos
            dic_response.update(
                {
                    "code": 200,
                    "status": "success",
                    "message_user": "Tesis obtenidas correctamente",
                    "message": "Tesis obtenidas correctamente",
                    "data": dic_tesis,
                }
            )
            return JsonResponse(dic_response, status=200)

        except DatabaseError as e:
            logger.error(f"Error al listar las Tesis: {str(e)}")
            dic_response.update(
                {"message": "Error al listar las Tesis", "data": str(e)}
            )
            return JsonResponse(dic_response, status=500)

    
    # Retorna una respuesta vacía si el método no es GET
    return JsonResponse([], safe=False, status=status.HTTP_200_OK)


@api_view(["POST"])
@transaction.atomic
def crear_tesis(request):
    
    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Error al crear la tesis",
        "message_user": "Error al crear la tesis",
        "data": [],
    }

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            data["estado"] = 1 
            data["fecha_creacion"] = datetime.now()  
            data["fecha_modificacion"] = datetime.now()  

            estado_nombre = obtener_nombre_por_id('Estado', data["estado"])

            serializer = TesisSerializer(data=data)

            if serializer.is_valid():
            
                with connection.cursor() as cursor:

                    nombre_tesis = data["nombre_tesis"]
                    
                    cursor.execute(
                        "SELECT nombre_tesis FROM Tesis WHERE (nombre_tesis='{0}') and estado_id IN (1, 2)".format(nombre_tesis)
                    )
                    if len(cursor.fetchall()) > 0:
                        dic_response.update(
                            {"message_user": "Ya existe una tesis con el mismo Nombre ", "message": "Ya hay un dato existente."}
                        )
                        return JsonResponse(dic_response, status=400)
                
                    cursor.close()

                serializer.save()

                dic_response.update(
                    {
                        "code": 201,
                        "status": "success",
                        "message_user": "Tesis creado exitosamente",
                        "message": "Tesis creado exitosamente",
                        "data": serializer.data
                    }
                )

                logger.info(
                    f"Tesis creado exitosamente: {data['nombre_tesis']} - {estado_nombre} (ID: {serializer.data['id']})"
                )

                return JsonResponse(dic_response, status=201)

            dic_response.update(
                {
                    "data": serializer.errors,
                }
            )
            return JsonResponse(dic_response, status=400)

        except Exception as e:
            logger.error(f"Error inesperado al crear al Tesis: {str(e)}")
            dic_response.update(
                {"message_user": "Error inesperado", "data": {"error": str(e)}}
            )
            return JsonResponse(dic_response, status=500)

    return Response([], status=status.HTTP_200_OK)


@api_view(["PUT"])
@transaction.atomic
def actualizar_tesis(request, id):

    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Error al actualizar la tesis",
        "message_user": "Error al actualizar la tesis",
        "data": [],
    }

    if request.method == "PUT":
        try:
            
            data = json.loads(request.body)
            
            data["fecha_modificacion"] = datetime.now()

            estado_nombre = obtener_nombre_por_id('Estado', data["estado"])
            
            try:
                queryset = Tesis.objects.using('default').get(id=id)
            except Tesis.DoesNotExist:
                
                return JsonResponse(dic_response, safe=False, status=status.HTTP_404_NOT_FOUND)

            
            serializer = TesisSerializer(queryset, data=data)

            if serializer.is_valid():

                with connection.cursor() as cursor:

                    nombre_tesis = data["nombre_tesis"]
                    estado = data["estado"]
                    
                    cursor.execute("SELECT nombre_tesis FROM Tesis WHERE (nombre_tesis='{0}') and estado_id = {1} and id <> {2}".format(nombre_tesis, estado, id))
                    if len(cursor.fetchall()) > 0:
                        dic_response.update(
                            {"message_user": "Ya existe una tesis con el mismo n° de nombre", "message": "Ya hay un dato existente."}
                        )
                        return JsonResponse(dic_response, status=400)

                    cursor.close()

                serializer.save()
                
                dic_response.update(
                    {
                        "code": 200,
                        "status": "success",
                        "message_user": "Tesis actualizado exitosamente",
                        "message": "Tesis actualizado exitosamente",
                        "data": serializer.data
                    }
                )

                logger.info(
                    f"Tesis actualizado exitosamente: {nombre_tesis} - {estado_nombre} (ID: {id})"
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

            logger.error(f"Error inesperado al actualizar el tesis: {str(e)}")
            dic_response.update(
                {"message_user": "Error inesperado", "data": {"error": str(e)}}
            )
            return JsonResponse(dic_response, status=500)

    return JsonResponse([], status=200)


@api_view(["DELETE"])
@transaction.atomic
def eliminar_tesis(request, id):

    dic_response = {
        "code": 400,
        "status": "error",
        "message": "Error al eliminar la Tesis",
        "message_user": "Error al eliminar la Tesis",
        "data": [],
    }

    if request.method == "DELETE":
        try:

            data = {"estado": 3}        

            try:
                queryset = Tesis.objects.using('default').get(id=id)

                queryset.estado = Estado.objects.using('default').get(id=data["estado"])
                queryset.fecha_modificacion = datetime.now()
                
                queryset.save()

                serializer = TesisSerializer(queryset)

                dic_response.update(
                    {
                        "code": 200,
                        "status": "success",
                        "message_user": "Tesis eliminado lógicamente",
                        "message": "Tesis eliminado lógicamente",
                        "data": serializer.data,
                    }
                )

                logger.info(f"Tesis eliminado logicamente: (ID: {id})")
                
                return JsonResponse(dic_response, status=200)

            except Tesis.DoesNotExist:
                return JsonResponse(dic_response, safe=False, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error inesperado al eliminar la Tesis: {str(e)}")
            dic_response["message"] = "Error inesperado"
            return JsonResponse(dic_response, status=500)

    return JsonResponse(dic_response, status=200)
