import math
from typing import List, Dict


def calcular_cobertura(mixer_litros: float, tasa_l_ha: float) -> float:
    """
    Calcula cuántas hectáreas cubre un mixer completo
    """
    if tasa_l_ha <= 0:
        return 0
    return mixer_litros / tasa_l_ha


def calcular_mixers_totales(hectareas: float, tasa_l_ha: float, mixer_litros: float) -> int:
    """
    Calcula cuántos mixers son necesarios para cubrir el lote
    """
    if hectareas <= 0 or tasa_l_ha <= 0 or mixer_litros <= 0:
        return 0
    return math.ceil((hectareas * tasa_l_ha) / mixer_litros)


def calcular_dosis_productos(
    productos: List[Dict],
    cobertura_ha: float,
    hectareas: float
) -> Dict[str, List[Dict]]:
    """
    Calcula dosis por mixer y total por lote
    """
    por_mixer = []
    total_lote = []

    for p in productos:
        dosis = p.get("dosis", 0)
        if dosis > 0:
            nombre = p.get("nombre", "Producto")
            unidad = p.get("unidad", "")

            por_mixer.append({
                "producto": nombre,
                "cantidad": round(dosis * cobertura_ha, 3),
                "unidad": unidad
            })

            total_lote.append({
                "producto": nombre,
                "cantidad": round(dosis * hectareas, 3),
                "unidad": unidad
            })

    return {
        "por_mixer": por_mixer,
        "total_lote": total_lote
    }
