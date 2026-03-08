<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Planificador Aplicación Drone</title>

<style>

body{
font-family: Arial, sans-serif;
background:#f7f9e8;
margin:0;
padding:0;
color:#1f2d16;
}

header{
background:#6a9f3a;
color:white;
padding:15px;
text-align:center;
font-size:22px;
font-weight:bold;
}

.container{
padding:15px;
max-width:600px;
margin:auto;
}

.card{
background:white;
padding:15px;
margin-bottom:15px;
border-radius:10px;
box-shadow:0 2px 6px rgba(0,0,0,0.1);
}

.card h2{
margin-top:0;
color:#4f772d;
}

input{
width:100%;
padding:10px;
margin-top:5px;
margin-bottom:10px;
border-radius:6px;
border:1px solid #ccc;
font-size:16px;
}

button{
width:100%;
padding:12px;
border:none;
background:#6a9f3a;
color:white;
font-size:18px;
border-radius:8px;
cursor:pointer;
}

button:hover{
background:#588528;
}

.result{
font-size:18px;
margin:6px 0;
}

.big{
font-size:24px;
font-weight:bold;
}

.links a{
display:block;
margin:5px 0;
color:#2d6a4f;
font-weight:bold;
text-decoration:none;
}

</style>

</head>
<body>

<header>
Planificador Aplicación Drone
</header>

<div class="container">

<div class="card">

<h2>Datos del lote</h2>

<label>Hectáreas</label>
<input id="hectareas" type="number">

<label>Litros por hectárea</label>
<input id="litros_ha" type="number">

<label>Dosis producto (cc/ha)</label>
<input id="dosis" type="number">

<label>Capacidad tanque mixer (L)</label>
<input id="mixer" type="number">

<button onclick="calcular()">Calcular</button>

</div>

<div class="card">

<h2>Resumen logístico</h2>

<div class="result big" id="agua_total"></div>
<div class="result" id="producto_total"></div>
<div class="result" id="mezclas"></div>
<div class="result" id="tanques"></div>

</div>

<div class="card">

<h2>Mezcla por tanque</h2>

<div class="result" id="mezcla_tanque"></div>

</div>

<div class="card">

<h2>Clima y condiciones</h2>

<div class="links">

<a href="https://www.windy.com" target="_blank">
Pronóstico Windy
</a>

<a href="https://www.meteoblue.com" target="_blank">
Pronóstico Meteoblue
</a>

<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank">
Índice geomagnético KP (NOAA)
</a>

</div>

</div>

</div>

<script>

function calcular(){

let hectareas = parseFloat(document.getElementById("hectareas").value);
let litros_ha = parseFloat(document.getElementById("litros_ha").value);
let dosis = parseFloat(document.getElementById("dosis").value);
let mixer = parseFloat(document.getElementById("mixer").value);

let agua_total = hectareas * litros_ha;

let producto_total_cc = hectareas * dosis;
let producto_total_l = producto_total_cc / 1000;

let mezclas = agua_total / mixer;

let tanques = Math.ceil(mezclas);

let producto_por_tanque = (producto_total_l / mezclas).toFixed(2);

document.getElementById("agua_total").innerHTML =
"Total agua: " + agua_total.toFixed(1) + " L";

document.getElementById("producto_total").innerHTML =
"Producto total: " + producto_total_l.toFixed(2) + " L";

document.getElementById("mezclas").innerHTML =
"Mezclas de mixer: " + mezclas.toFixed(2);

document.getElementById("tanques").innerHTML =
"Tanques completos necesarios: " + tanques;

document.getElementById("mezcla_tanque").innerHTML =
"Cada tanque: " + mixer + " L agua + " + producto_por_tanque + " L producto";

}

</script>

</body>
</html>
