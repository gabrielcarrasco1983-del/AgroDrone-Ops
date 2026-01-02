import math


def calculate_delta_t(temp: float, hum: float) -> float:
    """
    Calcula Delta T a partir de temperatura y humedad
    """
    if hum <= 0:
        return 0

    tw = (
        temp * math.atan(0.151977 * (hum + 8.313659) ** 0.5)
        + math.atan(temp + hum)
        - math.atan(hum - 1.676331)
        + 0.00391838 * (hum ** 1.5) * math.atan(0.023101 * hum)
        - 4.686035
    )
    return round(temp - tw, 2)
