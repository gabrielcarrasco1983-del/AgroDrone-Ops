from flask import Flask, render_template_string, request
import math

app = Flask(__name__)

HTML = """

<!DOCTYPE html>
<html>
<head>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>

body{
font-family: Arial;
background:#f7f9e8;
padding:20px;
color:#1f2d16;
}

.card{
background:white;
padding:15px;
border-radius:10px;
margin-bottom:15px;
box-shadow:0 2px 6px rgba(0,0,0,0.1);
}

h1{
background:#6a9f3a;
color:white;
padding:10px;
border-radius:8px;
}

input{
width:100%;
padding:8px;
margin:5px 0 10px 0;
}

button{
background:#6a9f3a;
color:white;
border:none;
padding:10px;
width:100%;
font-size:16px;
border-radius:6px;
}

a{
display:block;
margin:5px 0;
}

</style>

</head>

<body>

<h1>Planificador Drone</h1>

<div class="card">

<form method="post">

Hectáreas
<input name="hectareas" required>

Litros por hectárea
<input name="litros_ha" required>

Dosis producto (cc/ha)
<input name="dosis" required>

Capacidad tanque mixer (L)
<input name="mixer" required>

<button type="submit">Calcular</button>

</form>

</div>

{% if resultado %}

<div class="card">

<h3>Resumen</h3>

<p><b>Total agua:</b> {{resultado.agua}} L</p>
<p><b>Producto total:</b> {{resultado.producto}} L</p>
<p><b>Mezclas de mixer:</b> {{resultado.mezclas}}</p>
<p><b>Tanques necesarios:</b> {{resultado.tanques}}</p>

</div>

<div class="card">

<h3>Mezcla por tanque</h3>

<p>{{resultado.mixer}} L agua</p>
<p>{{resultado.producto_tanque}} L producto</p>

</div>

{% endif %}

<div class="card">

<h3>Clima</h3>

<a href="https://www.windy.com" target="_blank">Windy</a>
<a href="https://www.meteoblue.com" target="_blank">Meteoblue</a>
<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank">NOAA KP Index</a>

</div>

</body>
</html>

"""

@app.route("/", methods=["GET","POST"])
def home():

    resultado = None

    if request.method == "POST":

        hectareas = float(request.form["hectareas"])
        litros_ha = float(request.form["litros_ha"])
        dosis = float(request.form["dosis"])
        mixer = float(request.form["mixer"])

        agua_total = hectareas * litros_ha
        producto_total_l = (hectareas * dosis) / 1000

        mezclas = agua_total / mixer
        tanques = math.ceil(mezclas)

        producto_por_tanque = producto_total_l / mezclas

        resultado = {
            "agua": round(agua_total,2),
            "producto": round(producto_total_l,2),
            "mezclas": round(mezclas,2),
            "tanques": tanques,
            "mixer": mixer,
            "producto_tanque": round(producto_por_tanque,2)
        }

    return render_template_string(HTML, resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)
