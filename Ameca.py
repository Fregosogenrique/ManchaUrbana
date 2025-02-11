import os
from landsatxplore.earthexplorer import EarthExplorer
from landsatxplore.api import API

# Configuración de credenciales de USGS
USGS_USERNAME = "tu_usuario"  # Reemplaza con tu usuario de USGS
USGS_PASSWORD = "tu_contraseña"  # Reemplaza con tu contraseña de USGS

# Configuración de la ubicación de Ameca, Jalisco, México
LATITUDE = 20.55  # Latitud de Ameca
LONGITUDE = -104.04  # Longitud de Ameca

# Configuración del dataset de Landsat
DATASET = "landsat_tm_c2_l2"  # Landsat 5 TM (1984-2012)


# Para Landsat 8, usa "landsat_ot_c2_l2"

# Función para descargar imágenes por década
def descargar_imagenes_decada(decada, output_dir="images"):
    """
    Descarga imágenes de Landsat para una década específica.

    Parámetros:
        decada (str): Década en formato '1980', '1990', etc.
        output_dir (str): Directorio de salida para las imágenes.
    """
    # Crear directorio de salida si no existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iniciar sesión en USGS Earth Explorer
    api = API(USGS_USERNAME, USGS_PASSWORD)
    ee = EarthExplorer(USGS_USERNAME, USGS_PASSWORD)

    # Definir rango de fechas para la década
    start_date = f"{decada}-01-01"
    end_date = f"{int(decada) + 9}-12-31"

    # Buscar escenas disponibles
    print(f"Buscando imágenes para la década {decada}...")
    scenes = api.search(
        dataset=DATASET,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=10  # Máximo 10% de nubosidad
    )

    # Descargar cada escena
    for scene in scenes:
        scene_id = scene["entityId"]
        year = scene["acquisitionDate"].split("-")[0]  # Extraer el año
        scene_dir = os.path.join(output_dir, year)

        # Crear directorio para el año si no existe
        if not os.path.exists(scene_dir):
            os.makedirs(scene_dir)

        # Descargar la escena
        print(f"Descargando {scene_id} ({year})...")
        try:
            ee.download(scene_id, output_dir=scene_dir)
        except Exception as e:
            print(f"Error al descargar {scene_id}: {e}")

    # Cerrar sesión
    api.logout()
    ee.logout()
    print(f"Descarga de la década {decada} completada.")


# Función principal
def main():
    # Definir las décadas a descargar
    decadas = ["1980", "1990", "2000", "2010"]

    # Descargar imágenes para cada década
    for decada in decadas:
        descargar_imagenes_decada(decada)


if __name__ == "__main__":
    main()