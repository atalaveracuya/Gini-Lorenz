"""Segmentación de copas de árboles: vegetación (ExG + Otsu) y separación de copas (watershed).

Enfoque OBIA clásico para plantaciones arbóreas con dron (Torres-Sánchez et al. 2015;
Blaschke 2010): máscara de vegetación por umbral automático y separación de copas
contiguas con transformada de distancia + watershed (marcadores = máximos locales).
"""
import numpy as np
from scipy import ndimage as ndi
from skimage import filters, measure, morphology, segmentation
from skimage.feature import peak_local_max

from . import indices


def quitar_pequenos(etiquetas, area_min_px):
    """Elimina objetos etiquetados con menos de ``area_min_px`` píxeles (independiente de la versión de skimage)."""
    areas = np.bincount(etiquetas.ravel())
    pequenos = areas < area_min_px
    pequenos[0] = False
    out = etiquetas.copy()
    out[pequenos[etiquetas]] = 0
    return out


def mascara_vegetacion(orto, umbral=None, sigma_m=0.3, area_min_m2=1.0):
    """Máscara booleana de vegetación arbórea. ``umbral`` None = Otsu sobre ExG (o NDVI si hay NIR)."""
    if orto.nir is not None:
        idx = indices.ndvi(orto.rgb[..., 0], orto.nir)
    else:
        idx = indices.exg(orto.rgb)
    idx = filters.gaussian(idx, sigma=max(sigma_m / orto.gsd, 0.5))
    if umbral is None:
        umbral = filters.threshold_otsu(idx[orto.valido])
    veg = (idx > umbral) & orto.valido
    radio = max(1, int(round(0.3 / orto.gsd)))
    veg = ndi.binary_opening(veg, morphology.disk(radio))
    veg = ndi.binary_closing(veg, morphology.disk(radio))
    veg = ndi.binary_fill_holes(veg)
    veg = quitar_pequenos(measure.label(veg), area_min_m2 / orto.gsd ** 2) > 0
    return veg, float(umbral)


def separar_copas(veg, gsd, diametro_min_m=2.0, area_min_m2=2.0):
    """Etiqueta cada copa individual. ``diametro_min_m`` controla la distancia mínima entre centros."""
    dist = ndi.distance_transform_edt(veg)
    dist = filters.gaussian(dist, sigma=max(0.5, 0.25 / gsd))
    min_dist = max(1, int(round(diametro_min_m / 2 / gsd)))
    picos = peak_local_max(dist, min_distance=min_dist, threshold_abs=min_dist * 0.5,
                           labels=measure.label(veg), exclude_border=False)
    marcadores = np.zeros(veg.shape, np.int32)
    marcadores[tuple(picos.T)] = np.arange(1, len(picos) + 1)
    etiquetas = segmentation.watershed(-dist, marcadores, mask=veg)
    # Objetos sin marcador (copas pequeñas aisladas) se conservan como objetos propios
    sueltos = measure.label(veg & (etiquetas == 0))
    sueltos[sueltos > 0] += etiquetas.max()
    etiquetas = np.where(etiquetas > 0, etiquetas, sueltos)
    etiquetas = quitar_pequenos(etiquetas, area_min_m2 / gsd ** 2)
    etiquetas, _, _ = segmentation.relabel_sequential(etiquetas)
    return etiquetas


def segmentar(orto, umbral=None, diametro_min_m=2.0, area_min_m2=2.0):
    veg, umbral = mascara_vegetacion(orto, umbral=umbral)
    etiquetas = separar_copas(veg, orto.gsd, diametro_min_m=diametro_min_m, area_min_m2=area_min_m2)
    return etiquetas, veg, umbral
