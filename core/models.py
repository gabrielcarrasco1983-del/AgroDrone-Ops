from dataclasses import dataclass


@dataclass
class Producto:
    nombre: str
    dosis: float
    unidad: str


@dataclass
class Lote:
    nombre: str
    hectareas: float
    tasa_l_ha: float
    mixer_litros: float
