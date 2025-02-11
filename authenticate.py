import ee
import geemap
import os

ee.Initialize(project='proyectocuvallesmanchau25')
# Definir la región de interés (Ameca, Jalisco)
roi = ee.Geometry.Point([-104.0453, 20.5464]).buffer(5000)

# Definir los años de interés
decades = [1987, 1994, 2004, 2014, 2020]


# Función para obtener la imagen representativa de cada década
def get_landsat_image(year):
    start_date = f"{year}-01-01"
    end_date = f"{year + 9}-12-31"

    collection = (ee.ImageCollection("LANDSAT/LT05/C01/T1_SR")
                  .filterBounds(roi)
                  .filterDate(start_date, end_date)
                  .median()
                  )
    return collection.clip(roi)


# Carpeta de salida
output_folder = "landsat_ameca"
os.makedirs(output_folder, exist_ok=True)

# Descargar imágenes por década
for year in decades:
    img = get_landsat_image(year)
    filename = os.path.join(output_folder, f"ameca_{year}.tif")

    geemap.ee_export_image(img, filename=filename, scale=30, region=roi, file_per_band=False)
    print(f"Imagen de {year} descargada en {filename}")
