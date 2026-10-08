"""Lectura de imágenes de dron (JPG/PNG/GeoTIFF) y conversión píxel <-> coordenadas."""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # los ortomosaicos suelen superar el límite por defecto


@dataclass
class Ortomosaico:
    rgb: np.ndarray            # (alto, ancho, 3) uint8
    gsd: float                 # tamaño de píxel en metros (Ground Sample Distance)
    valido: np.ndarray         # máscara de píxeles con datos (excluye bordes negros/transparentes)
    transform: object = None   # affine de rasterio si el archivo está georreferenciado
    crs: object = None
    nir: np.ndarray = None     # banda infrarroja cercana si la cámara es multiespectral
    escala: float = 1.0        # factor de remuestreo aplicado al leer (píxeles originales * escala)

    def pixel_a_mundo(self, fila, col):
        """Convierte (fila, col) a coordenadas del CRS; sin georreferencia devuelve metros locales."""
        fila, col = np.asarray(fila, float), np.asarray(col, float)
        if self.transform is not None:
            x = self.transform.c + (col + 0.5) * self.transform.a + (fila + 0.5) * self.transform.b
            y = self.transform.f + (col + 0.5) * self.transform.d + (fila + 0.5) * self.transform.e
            return x, y
        return col * self.gsd, -fila * self.gsd

    def mundo_a_pixel(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        if self.transform is not None:
            t = ~self.transform
            col = t.a * x + t.b * y + t.c - 0.5
            fila = t.d * x + t.e * y + t.f - 0.5
            return fila, col
        return -y / self.gsd, x / self.gsd

    @property
    def area_ha(self):
        return float(self.valido.sum()) * self.gsd ** 2 / 10_000


def leer(ruta, gsd=None, banda_nir=None, escala=1.0):
    """Lee un ortomosaico.

    - GeoTIFF con rasterio instalado: toma GSD, transformación y CRS del archivo.
    - JPG/PNG/TIFF sin georreferencia: el GSD debe darse con ``gsd`` (m/píxel).
    ``banda_nir`` (1-indexado) permite leer la banda NIR de cámaras multiespectrales.
    ``escala`` < 1 reduce la resolución para ortomosaicos muy grandes.
    """
    ruta = Path(ruta)
    transform = crs = nir = None
    alpha = None
    if ruta.suffix.lower() in (".tif", ".tiff"):
        try:
            import rasterio
            with rasterio.open(ruta) as src:
                datos = src.read()
                if src.crs is not None and not src.transform.is_identity:
                    transform, crs = src.transform, src.crs
                    gsd = gsd or abs(src.transform.a)
                if banda_nir:
                    nir = datos[banda_nir - 1].astype(np.float32)
                if datos.shape[0] >= 4 and not banda_nir:
                    alpha = datos[3] > 0
                rgb = np.moveaxis(datos[:3], 0, -1)
        except ImportError:
            rgb = None
        else:
            rgb = _a_uint8(rgb)
    else:
        rgb = None
    if rgb is None:
        img = Image.open(ruta)
        if img.mode in ("RGBA", "LA"):
            alpha = np.asarray(img.split()[-1]) > 0
        rgb = np.asarray(img.convert("RGB"))
    lateral = ruta.with_suffix(".json")
    if gsd is None and lateral.exists():  # archivo auxiliar {"gsd_m": ...} junto a la imagen
        import json
        gsd = json.loads(lateral.read_text()).get("gsd_m")
    if gsd is None:
        raise ValueError(f"{ruta.name}: imagen sin georreferencia, indique --gsd (metros por píxel)")

    if escala != 1.0:
        alto, ancho = rgb.shape[:2]
        nuevo = (max(1, int(ancho * escala)), max(1, int(alto * escala)))
        rgb = np.asarray(Image.fromarray(rgb).resize(nuevo, Image.BILINEAR))
        if alpha is not None:
            alpha = np.asarray(Image.fromarray(alpha.astype(np.uint8) * 255).resize(nuevo, Image.NEAREST)) > 0
        if nir is not None:
            nir = np.asarray(Image.fromarray(nir).resize(nuevo, Image.BILINEAR))
        gsd = gsd / escala
        if transform is not None:
            transform = transform * transform.scale(1 / escala, 1 / escala)

    valido = rgb.max(axis=2) > 0 if alpha is None else alpha
    return Ortomosaico(rgb=rgb, gsd=float(gsd), valido=valido, transform=transform, crs=crs, nir=nir,
                      escala=escala)


def _a_uint8(arr):
    if arr.dtype == np.uint8:
        return arr
    arr = arr.astype(np.float32)
    lo, hi = np.percentile(arr[arr > 0], (0.5, 99.5)) if (arr > 0).any() else (0, 1)
    return (np.clip((arr - lo) / max(hi - lo, 1e-6), 0, 1) * 255).astype(np.uint8)
