import ee
import geopandas as gpd
import pandas as pd
import os
import geemap
import numpy as np

# Autenticar e inicializar Google Earth Engine
ee.Authenticate()
ee.Initialize(project='proyectocuvallesmanchau25')

# Lista de rutas a los archivos shapefile
shapefile_paths = [
    'Recursos/2020_Guadalupe.shp',
    'Recursos/2020_Morelos.shp',
    'Recursos/2020_Vetagrande.shp',
    "Recursos/2020_Zacatecas.shp"
]

# Años de interés
years = [1987, 1997, 2007, 2017, 2025]


# Función para obtener imágenes Landsat o Sentinel
def get_satellite_image(roi, year):
    try:
        # Seleccionar la colección de Landsat según el año
        if year <= 1999:
            collection_id = 'LANDSAT/LT05/C02/T1_L2'  # Landsat 5
            bands = ['SR_B4', 'SR_B3', 'SR_B2']  # RGB
        elif 2000 <= year <= 2013:
            collection_id = 'LANDSAT/LE07/C02/T1_L2'  # Landsat 7
            bands = ['SR_B4', 'SR_B3', 'SR_B2']
        else:
            collection_id = 'LANDSAT/LC08/C02/T1_L2'  # Landsat 8
            bands = ['SR_B4', 'SR_B3', 'SR_B2']

        # Filtrar colección
        image = (
            ee.ImageCollection(collection_id)
            .filterBounds(roi)
            .filterDate(f'{year}-01-01', f'{year}-12-31')
            .sort('CLOUD_COVER', True)
            .first()
        )

        if image:
            print(f"Imagen Landsat encontrada para {year}.")
            return image.select(bands), 'Landsat'
        else:
            raise Exception("No se encontró imagen en Landsat.")

    except Exception as e:
        print(f"Error con Landsat para {year}: {e}. Intentando Sentinel-2...")
        try:
            collection_id = 'COPERNICUS/S2_SR'
            bands = ['B4', 'B3', 'B2']  # Sentinel usa estas bandas para RGB

            image = (
                ee.ImageCollection(collection_id)
                .filterBounds(roi)
                .filterDate(f'{year}-01-01', f'{year}-12-31')
                .sort('CLOUDY_PIXEL_PERCENTAGE', True)
                .first()
            )

            if image:
                print(f"Imagen Sentinel-2 encontrada para {year}.")
                return image.select(bands), 'Sentinel-2'
            else:
                raise Exception("No se encontró imagen en Sentinel-2.")

        except Exception as e:
            print(f"Error con Sentinel-2 para {year}: {e}.")
            return None, None


# Función para calcular el cambio urbano
def calculate_urban_change(image1, image2):
    # Calcular la diferencia entre las imágenes
    difference = image2.subtract(image1)
    return difference


# Unir todos los shapes en un solo GeoDataFrame
all_gdf = gpd.GeoDataFrame()
for shapefile_path in shapefile_paths:
    gdf = gpd.read_file(shapefile_path)

    # Verificar y transformar el CRS a un estándar común (por ejemplo, WGS84 EPSG:4326)
    if gdf.crs is None:
        print(f"Advertencia: El shapefile {shapefile_path} no tiene CRS definido. Asumiendo WGS84.")
        gdf.set_crs(epsg=4326, inplace=True)
    else:
        gdf = gdf.to_crs(epsg=4326)  # Transformar a WGS84

    all_gdf = pd.concat([all_gdf, gdf], ignore_index=True)  # Usar pd.concat

# Extraer coordenadas del área total
coords = all_gdf.geometry.bounds.values.tolist()[0]  # Primer rectángulo delimitador
roi = ee.Geometry.Rectangle(coords)

# Obtener imágenes para cada año y calcular cambios
images = {}
for year in years:
    print(f"\nObteniendo imagen para {year}...")
    image, source = get_satellite_image(roi, year)
    if image:
        images[year] = image

# Calcular cambios entre años consecutivos
for i in range(len(years) - 1):
    year1 = years[i]
    year2 = years[i + 1]
    if year1 in images and year2 in images:
        change = calculate_urban_change(images[year1], images[year2])
        output_file = os.path.join('output', f'cambio_{year1}_{year2}.tif')
        geemap.ee_export_image(
            change,
            filename=output_file,
            scale=30,
            region=roi,
            file_per_band=False
        )
        print(f"Cambio urbano entre {year1} y {year2} guardado como {output_file}")

# Visualizar el crecimiento urbano completo
Map = geemap.Map()
Map.addLayer(images[years[-1]], {'bands': ['SR_B4', 'SR_B3', 'SR_B2'], 'min': 0, 'max': 3000}, 'Última imagen')
Map.addLayer(change, {'min': -1000, 'max': 1000, 'palette': ['red', 'yellow', 'green']}, 'Cambio urbano')
Map.centerObject(roi, zoom=10)