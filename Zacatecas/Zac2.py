import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.enums import Resampling

def calculate_ndbi(image_path, output_path):
    with rasterio.open(image_path) as src:
        band_count = src.count
        print(f"Imagen: {image_path} | Número de bandas disponibles: {band_count}")

        # Verificar si tiene suficientes bandas
        if band_count >= 6:
            swir_band = src.read(6).astype('float32')  # Banda SWIR
            nir_band = src.read(5).astype('float32')  # Banda NIR
        elif band_count == 3:
            print("⚠ Imagen RGB detectada. Usando banda 3 como SWIR y banda 2 como NIR.")
            swir_band = src.read(3).astype('float32')
            nir_band = src.read(2).astype('float32')
        else:
            raise ValueError(f"⚠ {image_path} no tiene suficientes bandas para calcular NDBI.")

        # Calcular NDBI
        ndbi = (swir_band - nir_band) / (swir_band + nir_band + 1e-10)

        # Guardar imagen NDBI
        save_ndbi_as_tif(ndbi, src, output_path)

        return ndbi, src

def save_ndbi_as_tif(ndbi_array, src, output_path):
    """Guarda el NDBI como un archivo .tif usando la misma referencia espacial de la imagen original"""
    profile = src.profile
    profile.update(dtype=rasterio.float32, count=1)

    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndbi_array, 1)

    print(f"NDBI guardado en: {output_path}")

def match_raster_sizes(ndbi1, src1, ndbi2, src2):
    """Reescalar la segunda imagen para que coincida con la primera"""
    if ndbi1.shape == ndbi2.shape:
        return ndbi1, ndbi2

    print("⚠ Dimensiones diferentes. Ajustando resolución...")
    with rasterio.open(src2.name) as src:
        ndbi2_resampled = src.read(
            1,
            out_shape=(ndbi1.shape[0], ndbi1.shape[1]),
            resampling=Resampling.bilinear
        )
    return ndbi1, ndbi2_resampled

def plot_comparison(ndbi1, ndbi2, title1, title2):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Mapa de NDBI 1
    im1 = axes[0].imshow(ndbi1, cmap='RdYlBu')
    axes[0].set_title(title1)
    plt.colorbar(im1, ax=axes[0])

    # Mapa de NDBI 2
    im2 = axes[1].imshow(ndbi2, cmap='RdYlBu')
    axes[1].set_title(title2)
    plt.colorbar(im2, ax=axes[1])

    # Diferencia porcentual
    difference = ndbi2 - ndbi1
    percentage_change = (difference / (ndbi1 + 1e-10)) * 100

    # Mapa de cambios
    im_diff = axes[2].imshow(percentage_change, cmap='bwr', vmin=-100, vmax=100)
    axes[2].set_title("Cambio porcentual de NDBI (%)")
    plt.colorbar(im_diff, ax=axes[2])

    plt.show()

# Rutas de las imágenes
image_path_1 = "output/2020_Zacatecas/imagen_1997.tif"
image_path_2 = "output/2020_Zacatecas/imagen_2025.tif"

# Rutas de salida para NDBI
output_ndbi_1 = "output/2020_Zacatecas/ndbi_1997.tif"
output_ndbi_2 = "output/2020_Zacatecas/ndbi_2025.tif"

# Calcular NDBI
ndbi_1980, src1 = calculate_ndbi(image_path_1, output_ndbi_1)
ndbi_2020, src2 = calculate_ndbi(image_path_2, output_ndbi_2)

# Asegurar que ambas imágenes tengan el mismo tamaño
ndbi_1980, ndbi_2020 = match_raster_sizes(ndbi_1980, src1, ndbi_2020, src2)

# Mostrar comparación
plot_comparison(ndbi_1980, ndbi_2020, "NDBI 1987", "NDBI 2025")