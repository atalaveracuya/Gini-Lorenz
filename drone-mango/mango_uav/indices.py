"""Índices de vegetación para cámaras RGB (y NDVI si hay banda NIR).

Referencias: Woebbecke et al. (1995) ExG; Meyer & Neto (2008) ExG-ExR;
Gitelson et al. (2002) VARI; Louhaichi et al. (2001) GLI; Tucker (1979) NGRDI/NDVI.
"""
import numpy as np

EPS = 1e-6


def _canales(rgb):
    rgb = rgb.astype(np.float32)
    return rgb[..., 0], rgb[..., 1], rgb[..., 2]


def cromaticas(rgb):
    R, G, B = _canales(rgb)
    s = R + G + B + EPS
    return R / s, G / s, B / s


def exg(rgb):
    r, g, b = cromaticas(rgb)
    return 2 * g - r - b


def exgr(rgb):
    r, g, b = cromaticas(rgb)
    return (2 * g - r - b) - (1.4 * r - g)


def vari(rgb):
    R, G, B = _canales(rgb)
    return np.clip((G - R) / (G + R - B + EPS), -1, 1)


def gli(rgb):
    R, G, B = _canales(rgb)
    return (2 * G - R - B) / (2 * G + R + B + EPS)


def ngrdi(rgb):
    R, G, _ = _canales(rgb)
    return (G - R) / (G + R + EPS)


def ndvi(rojo, nir):
    rojo, nir = rojo.astype(np.float32), nir.astype(np.float32)
    return (nir - rojo) / (nir + rojo + EPS)


def todos(rgb, nir=None):
    out = {"ExG": exg(rgb), "ExGR": exgr(rgb), "VARI": vari(rgb), "GLI": gli(rgb), "NGRDI": ngrdi(rgb)}
    if nir is not None:
        out["NDVI"] = ndvi(rgb[..., 0], nir)
    return out
