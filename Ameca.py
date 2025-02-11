import rasterio
import numpy as np
import matplotlib.pyplot as plt

def calculate_ndbi(image_path):
    with rasterio.open(image_path) as src:
        nir_band = src.read(5).astype('float32')  # Banda SWIR (ejemplo: Landsat 5 TM Banda 5 o Landsat 8 Banda 6)
        swir_band = src.read(6).astype('float32')  # Banda NIR (ejemplo: Landsat 5 TM Banda 4 o Landsat 8 Banda 5)

        ndbi = (swir_band - nir_band) / (swir_band + nir_band + 1e-10)  # Cálculo de NDBI
        return ndbi

def plot_comparison(ndbi1, ndbi2, title1, title2):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Mapa de NDBI para la primera década
    im1 = axes[0].imshow(ndbi1, cmap='RdYlBu')
    axes[0].set_title(title1)
    plt.colorbar(im1, ax=axes[0])

    # Mapa de NDBI para la segunda década
    im2 = axes[1].imshow(ndbi2, cmap='RdYlBu')
    axes[1].set_title(title2)
    plt.colorbar(im2, ax=axes[1])

    # Cálculo de la diferencia y el porcentaje de cambio
    difference = ndbi2 - ndbi1
    percentage_change = (difference / (ndbi1 + 1e-10)) * 100  # Evitar división por cero

    # Mapa de diferencias con porcentaje de cambio
    im_diff = axes[2].imshow(percentage_change, cmap='bwr', vmin=-100, vmax=100)
    axes[2].set_title("Cambio porcentual de NDBI (%)")
    plt.colorbar(im_diff, ax=axes[2])

    plt.show()

# Rutas de las imágenes por década
image_path_1 = "landsat_ameca/ameca_1987.tif"  # Reemplazar con la imagen de la primera década
image_path_2 = "landsat_ameca/ameca_2006.tif"  # Reemplazar con la imagen de la segunda década

ndbi_1980 = calculate_ndbi(image_path_1)
ndbi_2020 = calculate_ndbi(image_path_2)

plot_comparison(ndbi_1980, ndbi_2020, "NDBI 1980", "NDBI 2020")