from urllib.parse import quote
import pandas as pd
import io


def generar_mensaje_whatsapp(lote, cobertura, por_mixer, total_lote) -> str:
    """
    Genera el link de WhatsApp con el reporte completo
    """
    lineas_mixer = [
        f"- {p['producto']}: {p['cantidad']} {p['unidad']}"
        for p in por_mixer
    ]

    lineas_total = [
        f"- {p['producto']}: {p['cantidad']} {p['unidad']}"
        for p in total_lote
    ]

    mensaje = (
        f"*DRONE SPRAYLOGIC*\n"
        f"*Lote:* {lote.nombre}\n"
        f"Mixer: {lote.mixer_litros}L | Cubre: {cobertura:.2f}Ha\n"
        f"--- POR MIXER ---\n"
        + "\n".join(lineas_mixer)
        + f"\n--- TOTAL LOTE ({lote.hectareas}Ha) ---\n"
        + "\n".join(lineas_total)
    )

    return f"https://wa.me/?text={quote(mensaje)}"


def generar_excel(nombre_lote: str, total_lote: list) -> bytes:
    """
    Genera archivo Excel en memoria
    """
    data = []

    for p in total_lote:
        data.append({
            "Lote": nombre_lote,
            "Producto": p["producto"],
            "Cantidad": p["cantidad"],
            "Unidad": p["unidad"]
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
with pd.ExcelWriter(output) as writer:
    df.to_excel(writer, index=False, sheet_name="Reporte")


    return output.getvalue()
