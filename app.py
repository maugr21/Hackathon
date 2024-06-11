from fastapi import FastAPI, HTTPException
import urllib.parse
import requests

app = FastAPI()

map_url = "http://www.mapquestapi.com/directions/v2/route?"
key = "FpQMlz7vleXdOl0byQjomVZ6aQfavrbL"

@app.get("/direcciones/")
def obtener_direcciones(origen: str, destino: str):
    try:
        # Codificar valores de origen y destino
        origen_codificado = urllib.parse.quote(origen)
        destino_codificado = urllib.parse.quote(destino)

        # Parámetros para la URL
        parametros = {
            "key": key,
            "from": origen_codificado,
            "to": destino_codificado
        }

        # Combinar la URL con los parámetros codificados
        url = map_url + urllib.parse.urlencode(parametros)

        # Realizar la solicitud HTTP usando requests
        respuesta = requests.get(url)

        # Verificar el estado de la respuesta
        respuesta.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa

        # Obtener los datos de respuesta en formato JSON
        datos_json = respuesta.json()
        codigo_estado = datos_json["info"]["statuscode"]  # Acceder al valor del diccionario

        if codigo_estado == 0:
            duracion_viaje = datos_json["route"]["formattedTime"]
            distancia = datos_json["route"]["distance"] * 1.61  # Convertir la distancia a kilómetros

            datos_respuesta = {
                "origen": origen.capitalize(),
                "destino": destino.capitalize(),
                "duracion_viaje": duracion_viaje,
                "distancia_km": distancia
            }

            maniobras = []
            # Iterar sobre las maniobras del viaje
            for paso in datos_json["route"]["legs"][0]["maneuvers"]:
                distancia_restante = distancia - paso["distance"] * 1.61
                maniobras.append({
                    "narrativa": paso["narrative"],
                    "distancia_restante_km": distancia_restante
                })
                distancia = distancia_restante

            datos_respuesta["maniobras"] = maniobras

            return datos_respuesta
        else:
            raise HTTPException(status_code=404, detail="Hubo un problema al obtener la ruta.")

    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al hacer la solicitud HTTP: {e}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la respuesta JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error inesperado: {e}")