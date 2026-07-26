import os
from flask import Flask, request, jsonify, render_template_string
import moto  # Tu lógica de base de datos existente

app = Flask(__name__)

if hasattr(moto, 'inicializar_base_datos'):
    moto.inicializar_base_datos()

# Estado Global en memoria para sincronizar Pasajero y Conductor
ESTADO_CONDUCTOR = {
    "registrado": False,
    "nombre": "",
    "vehiculo": "Moto",
    "disponible": False,
    "ubicacion": "Sin GPS",
    "saldo": 0.0,
    "solicitud_activa": None,
    "estado_viaje": "esperando" # esperando, en_camino, llego, finalizado
}

HTML_APP = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>VeloCity App</title>
    <meta name="theme-color" content="#0A0A0B">
    <style>
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background-color: #0A0A0B; color: #F4F4F7; margin: 0; padding: 15px; 
            display: flex; justify-content: center; align-items: center; min-height: 100vh;
        }
        .card { 
            background: #141416; padding: 22px; border-radius: 24px; width: 100%; max-width: 420px; 
            border: 1px solid #232428; box-shadow: 0 10px 30px rgba(0,0,0,0.8); position: relative; overflow: hidden;
        }
        h1 { color: #00E5FF; text-align: center; margin: 0 0 2px 0; font-size: 26px; letter-spacing: 1px; }
        p.subtitle { text-align: center; color: #72767D; margin: 0 0 18px 0; font-size: 12px; }
        
        .dash-banner {
            background: linear-gradient(135deg, #00E5FF 0%, #0088FF 100%);
            color: #0A0A0B; padding: 18px; border-radius: 18px; text-align: center; margin-bottom: 15px;
        }
        .dash-banner h2 { margin: 0; font-size: 18px; font-weight: 800; }
        .dash-banner p { margin: 3px 0 0 0; font-size: 11px; font-weight: 600; }

        .menu-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 15px; }
        .menu-card {
            background: #1C1C1F; border: 1px solid #28292E; padding: 16px 12px; border-radius: 16px;
            text-align: center; cursor: pointer; transition: 0.2s;
        }
        .menu-card:active { border-color: #00E5FF; background: #232428; transform: scale(0.98); }
        .menu-card .icon { font-size: 24px; margin-bottom: 6px; display: block; }
        .menu-card .title { font-size: 12px; font-weight: bold; color: #F4F4F7; }

        label { display: block; margin-top: 12px; font-size: 11px; font-weight: bold; color: #72767D; text-transform: uppercase; }
        input, select { width: 100%; padding: 12px; margin-top: 5px; background: #1C1C1F; border: 1px solid #28292E; border-radius: 10px; color: #F4F4F7; font-size: 13px; outline: none; }
        input:focus, select:focus { border-color: #00E5FF; }

        .row-gps { display: flex; gap: 8px; margin-top: 5px; }
        .row-gps input { margin-top: 0; }
        .btn-gps { background: #232428; color: #00E5FF; border: 1px solid #00E5FF; padding: 0 12px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 12px; }

        .btn-main { width: 100%; padding: 14px; margin-top: 16px; background: #00E5FF; color: #0A0A0B; border: none; border-radius: 12px; font-weight: bold; font-size: 14px; cursor: pointer; }
        .btn-secondary { width: 100%; padding: 12px; margin-top: 10px; background: #1C1C1F; color: #72767D; border: 1px solid #28292E; border-radius: 12px; font-weight: bold; font-size: 12px; cursor: pointer; }

        .search-results { background: #1C1C1F; border: 1px solid #28292E; border-radius: 10px; margin-top: 5px; max-height: 120px; overflow-y: auto; }
        .search-item { padding: 10px; border-bottom: 1px solid #28292E; font-size: 12px; cursor: pointer; }
        .search-item:hover { background: #00E5FF; color: #0A0A0B; }

        .trip-summary { background: #1C1C1F; border: 1px solid #00E5FF; padding: 14px; border-radius: 14px; margin-top: 15px; }
        .summary-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px; }
        .price-tag { font-size: 22px; font-weight: 800; color: #00E5FF; text-align: center; margin-top: 8px; }

        .pago-datos-box { background: #1C1C1F; border: 1px dashed #00E5FF; border-radius: 12px; padding: 12px; margin-top: 10px; font-size: 12px; }
        .pago-datos-row { display: flex; justify-content: space-between; margin-bottom: 5px; }

        .file-upload { border: 2px dashed #28292E; padding: 12px; text-align: center; border-radius: 10px; margin-top: 10px; cursor: pointer; font-size: 11px; color: #72767D; }

        /* Switch para Disponibilidad Conductor */
        .switch-container { display: flex; justify-content: space-between; align-items: center; background: #1C1C1F; padding: 14px; border-radius: 12px; margin-top: 12px; }
        .switch { position: relative; display: inline-block; width: 46px; height: 24px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #333; transition: .4s; border-radius: 34px; }
        .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: #00E5FF; }
        input:checked + .slider:before { transform: translateX(22px); }

        /* Wallet Box */
        .wallet-box { background: linear-gradient(135deg, #1C1C1F 0%, #232428 100%); border: 1px solid #00E5FF; border-radius: 14px; padding: 15px; text-align: center; margin-top: 12px; }
        .wallet-amount { font-size: 26px; font-weight: 800; color: #00E5FF; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="card">
        <h1>VELOCITY</h1>
        <p class="subtitle">Tu app de transporte de confianza</p>

        <!-- 1. PANTALLA INICIAL DE SELECCIÓN DE ROL -->
        <div id="viewRolSelector">
            <p style="text-align:center; font-size:13px; color:#72767D;">¿Cómo deseas ingresar hoy?</p>
            <div class="menu-card" onclick="mostrarVista('viewDashboardPasajero')" style="margin-bottom:12px;">
                <span class="icon">🙋‍♂️</span>
                <span class="title">Entrar como Pasajero</span>
            </div>
            <div class="menu-card" onclick="iniciarModuloConductor()">
                <span class="icon">🏍️</span>
                <span class="title">Entrar como Motorizado / Conductor</span>
            </div>
        </div>

        <!-- ================= MÓDULO PASAJERO ================= -->
        <div id="viewDashboardPasajero" style="display:none;">
            <div class="dash-banner">
                <h2>¡Modo Pasajero!</h2>
                <p>Viaja seguro y rápido</p>
            </div>
            <div class="menu-grid">
                <div class="menu-card" onclick="mostrarVista('viewPaso1Origen')"><span class="icon">🚗</span><span class="title">Solicitar Viaje</span></div>
                <div class="menu-card" onclick="mostrarVista('viewMensajes')"><span class="icon">💬</span><span class="title">Mensajes</span></div>
                <div class="menu-card" onclick="mostrarVista('viewConfiguracion')"><span class="icon">⚙️</span><span class="title">Configuración</span></div>
                <div class="menu-card" onclick="mostrarVista('viewRolSelector')"><span class="icon">🔄</span><span class="title">Cambiar Rol</span></div>
            </div>
        </div>

        <!-- PASO 1 ORIGEN PASAJERO -->
        <div id="viewPaso1Origen" style="display: none;">
            <p class="subtitle">Paso 1: Tu Ubicación Actual</p>
            <div class="row-gps">
                <input type="text" id="origenInput" value="📍 Mi Ubicación (Barcelona, Anzoátegui)">
                <button type="button" class="btn-gps" onclick="obtenerGPS('origenInput')">📍 GPS</button>
            </div>
            <button class="btn-main" onclick="confirmarOrigen()">CONFIRMAR ORIGEN</button>
            <button class="btn-secondary" onclick="mostrarVista('viewDashboardPasajero')">Cancelar</button>
        </div>

        <!-- PASO 2 DESTINO PASAJERO -->
        <div id="viewPaso2Destino" style="display: none;">
            <p class="subtitle">Paso 2: ¿A dónde deseas ir?</p>
            <input type="text" id="destinoInput" placeholder="Escribe tu destino..." oninput="buscarLugar(this.value)">
            <div id="searchResults" class="search-results" style="display:none;"></div>
            <button class="btn-secondary" onclick="mostrarVista('viewPaso1Origen')">Atrás</button>
        </div>

        <!-- PASO 3 VEHÍCULO Y TARIFA -->
        <div id="viewPaso3Vehiculo" style="display: none;">
            <p class="subtitle">Paso 3: Elige tu Transporte</p>
            <select id="selectVehiculo" onchange="calcularViaje()">
                <option value="Moto">🏍️ Moto Rapid</option>
                <option value="Carro">🚗 Carro Confort</option>
            </select>
            <div class="trip-summary">
                <div class="summary-row"><span>Origen:</span> <b id="sumOrigen">-</b></div>
                <div class="summary-row"><span>Destino:</span> <b id="sumDestino">-</b></div>
                <div class="summary-row"><span>Distancia:</span> <b id="sumDistancia">4.2 km</b></div>
                <div class="summary-row"><span>Tiempo de Viaje:</span> <b id="sumDuracion">8 min</b></div>
                <div class="price-tag" id="sumPrecio">$3.50 USD</div>
            </div>
            <button class="btn-main" onclick="mostrarVista('viewPaso4Pago')">CONTINUAR AL PAGO</button>
            <button class="btn-secondary" onclick="mostrarVista('viewPaso2Destino')">Atrás</button>
        </div>

        <!-- PASO 4 PAGO Y CAPTURE -->
        <div id="viewPaso4Pago" style="display: none;">
            <p class="subtitle">Paso 4: Método de Pago</p>
            <select id="metodoPago" onchange="toggleCapture(this.value)">
                <option value="destino">💵 Pagar en efectivo al llegar</option>
                <option value="durante">📲 Pago Móvil / Transferencia</option>
            </select>

            <div id="boxPagoMovil" style="display:none;">
                <div class="pago-datos-box">
                    <b style="color:#00E5FF; display:block; text-align:center; margin-bottom:5px;">DATOS PAGO MÓVIL BANESCO</b>
                    <div class="pago-datos-row"><span>Banco:</span> <b>0134</b></div>
                    <div class="pago-datos-row"><span>Cédula:</span> <b>32.685.624</b></div>
                    <div class="pago-datos-row"><span>Teléfono:</span> <b>0414-8154751</b></div>
                </div>
                <div class="file-upload" onclick="document.getElementById('fileCapture').click()">
                    📸 Adjuntar Capture de Pago
                    <input type="file" id="fileCapture" style="display:none" onchange="document.getElementById('lblCap').innerText='✅ Capture Adjuntado'">
                </div>
                <p id="lblCap" style="font-size:11px; color:#00E5FF; text-align:center; margin-top:4px;"></p>
            </div>

            <button class="btn-main" onclick="solicitarViajeServidor()">CONFIRMAR Y SOLICITAR</button>
            <button class="btn-secondary" onclick="mostrarVista('viewPaso3Vehiculo')">Atrás</button>
        </div>

        <!-- SEGUIMIENTO EN TIEMPO REAL PASAJERO -->
        <div id="viewStatusPasajero" style="display: none; text-align:center;">
            <p class="subtitle">Estado de tu Solicitud</p>
            <div id="boxStatusPasajeroContent" style="padding:15px; background:#1C1C1F; border:1px solid #00E5FF; border-radius:14px;">
                Buscando conductor cercano...
            </div>
            <button class="btn-secondary" onclick="mostrarVista('viewDashboardPasajero')" style="margin-top:15px;">Volver al Inicio</button>
        </div>


        <!-- ================= MÓDULO CONDUCTOR ================= -->
        <!-- REGISTRO / ONBOARDING CONDUCTOR -->
        <div id="viewRegistroConductor" style="display: none;">
            <p class="subtitle">Registro de Conductor / Motorizado</p>
            <label>Tu Nombre Completo</label>
            <input type="text" id="regNombreCond" placeholder="Ej: Carlos Mendoza">

            <label>Tipo de Vehículo</label>
            <select id="regTipoVehiculo" onchange="toggleRequisitosMoto(this.value)">
                <option value="Moto">🏍️ Moto</option>
                <option value="Carro">🚗 Carro</option>
            </select>

            <label>Foto del Vehículo</label>
            <div class="file-upload" onclick="document.getElementById('fileVehiculo').click()">
                📸 Subir foto de la Moto / Carro
                <input type="file" id="fileVehiculo" style="display:none" onchange="document.getElementById('lblV').innerText='✅ Foto de Vehículo Lista'">
            </div>
            <p id="lblV" style="font-size:11px; color:#00E5FF; text-align:center;"></p>

            <div id="boxCascos">
                <label>Foto de los 2 Cascos (Requisito Seguridad Moto)</label>
                <div class="file-upload" onclick="document.getElementById('fileCascos').click()">
                    🪖 Subir foto de los 2 Cascos
                    <input type="file" id="fileCascos" style="display:none" onchange="document.getElementById('lblC').innerText='✅ Foto de Cascos Lista'">
                </div>
                <p id="lblC" style="font-size:11px; color:#00E5FF; text-align:center;"></p>
            </div>

            <label>Compartir tu Ubicación GPS</label>
            <div class="row-gps">
                <input type="text" id="gpsCondInput" placeholder="Toca GPS para vincular">
                <button type="button" class="btn-gps" onclick="obtenerGPS('gpsCondInput')">📍 GPS</button>
            </div>

            <button class="btn-main" onclick="completarRegistroConductor()">COMPLETAR REGISTRO</button>
            <button class="btn-secondary" onclick="mostrarVista('viewRolSelector')">Volver</button>
        </div>

        <!-- PANEL DASHBOARD CONDUCTOR -->
        <div id="viewDashboardConductor" style="display: none;">
            <div class="dash-banner">
                <h2>Panel de Conductor</h2>
                <p id="lblNombreCondHeader">Conductor Activo</p>
            </div>

            <div class="switch-container">
                <span style="font-weight: bold; font-size: 13px;">Estado: <span id="lblEstadoCond" style="color:#ff4b4b;">DESCONECTADO</span></span>
                <label class="switch">
                    <input type="checkbox" id="chkDispoCond" onchange="toggleDispoCond(this.checked)">
                    <span class="slider"></span>
                </label>
            </div>

            <!-- BILLETERA DIGITAL (WALLET) -->
            <div class="wallet-box">
                <div style="font-size:11px; color:#72767D; font-weight:bold;">MI BILLETERA / SALDO ACUMULADO</div>
                <div class="wallet-amount" id="lblSaldoWallet">$0.00 USD</div>
                <div style="font-size:10px; color:#72767D; margin-bottom:8px;">* Se descuenta el 5% de comisión por cada viaje.</div>
                <button class="btn-main" style="padding:8px; font-size:11px; margin-top:0;" onclick="retirarSaldo()">💸 RETIRAR DINERO</button>
            </div>

            <!-- CONTENEDOR DE ALERTAS DE VIAJE EN VIVO -->
            <div id="boxSolicitudesCond" style="margin-top:15px;">
                <p style="text-align:center; font-size:12px; color:#72767D;">Conéctate para recibir solicitudes de viaje...</p>
            </div>

            <button class="btn-secondary" onclick="mostrarVista('viewRolSelector')">Cambiar de Rol</button>
        </div>

        <!-- VISTAS AUXILIARES -->
        <div id="viewConfiguracion" style="display: none;">
            <p class="subtitle">Ajustes</p>
            <button class="btn-secondary" onclick="mostrarVista('viewRolSelector')">Volver</button>
        </div>
        <div id="viewMensajes" style="display: none;">
            <p class="subtitle">Mensajes</p>
            <button class="btn-secondary" onclick="mostrarVista('viewRolSelector')">Volver</button>
        </div>
    </div>

    <script>
        let viajeActual = { origen: "", destino: "", vehiculo: "Moto", precio: 3.50, duracion: 8 };

        function mostrarVista(id) {
            const vistas = ['viewRolSelector', 'viewDashboardPasajero', 'viewPaso1Origen', 'viewPaso2Destino', 'viewPaso3Vehiculo', 'viewPaso4Pago', 'viewStatusPasajero', 'viewRegistroConductor', 'viewDashboardConductor', 'viewConfiguracion', 'viewMensajes'];
            vistas.forEach(v => document.getElementById(v).style.display = 'none');
            document.getElementById(id).style.display = 'block';
        }

        function obtenerGPS(inputId) {
            const el = document.getElementById(inputId);
            el.value = "Obteniendo GPS...";
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    pos => { el.value = `📍 GPS (${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)})`; },
                    err => { el.value = "📍 GPS Activo (Barcelona, Anzoátegui)"; }
                );
            } else { el.value = "📍 GPS Activo (Barcelona, Anzoátegui)"; }
        }

        // --- PASAJERO LOGIC ---
        function confirmarOrigen() {
            viajeActual.origen = document.getElementById('origenInput').value;
            mostrarVista('viewPaso2Destino');
        }

        function buscarLugar(val) {
            const resBox = document.getElementById('searchResults');
            if(!val) { resBox.style.display = 'none'; return; }
            const lugares = ["C.C. Puente Real (Barcelona)", "Plaza Bolívar (Barcelona)", "C.C. Plaza Mayor (Lechería)", "Puerto La Cruz Centro"];
            resBox.innerHTML = '';
            lugares.filter(l => l.toLowerCase().includes(val.toLowerCase())).forEach(l => {
                let div = document.createElement('div');
                div.className = 'search-item';
                div.innerText = '📍 ' + l;
                div.onclick = () => {
                    document.getElementById('destinoInput').value = l;
                    resBox.style.display = 'none';
                    viajeActual.destino = l;
                    calcularViaje();
                    mostrarVista('viewPaso3Vehiculo');
                };
                resBox.appendChild(div);
            });
            resBox.style.display = 'block';
        }

        function calcularViaje() {
            let tipo = document.getElementById('selectVehiculo').value;
            viajeActual.vehiculo = tipo;
            viajeActual.precio = tipo === 'Moto' ? 3.50 : 6.00;
            document.getElementById('sumOrigen').innerText = viajeActual.origen;
            document.getElementById('sumDestino').innerText = viajeActual.destino;
            document.getElementById('sumPrecio').innerText = `$${viajeActual.precio.toFixed(2)} USD`;
        }

        function toggleCapture(metodo) {
            document.getElementById('boxPagoMovil').style.display = metodo === 'durante' ? 'block' : 'none';
        }

        async function solicitarViajeServidor() {
            mostrarVista('viewStatusPasajero');
            await fetch('/api/pasajero/solicitar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(viajeActual)
            });
            pollEstadoPasajero();
        }

        async function pollEstadoPasajero() {
            const res = await fetch('/api/pasajero/estado');
            const data = await res.json();
            const box = document.getElementById('boxStatusPasajeroContent');

            if (data.estado === 'esperando') {
                box.innerHTML = `<b style="color:#00E5FF;">Buscando conductor disponible...</b>`;
                setTimeout(pollEstadoPasajero, 2000);
            } else if (data.estado === 'en_camino') {
                box.innerHTML = `<h3 style="color:#00E5FF; margin:0;">¡CONDUCTOR EN CAMINO!</h3><p style="font-size:12px;">Él ya aceptó tu viaje y se dirige a tu punto de origen.</p>`;
                setTimeout(pollEstadoPasajero, 2000);
            } else if (data.estado === 'llego') {
                box.innerHTML = `<h3 style="color:#00E5FF; margin:0;">¡EL CONDUCTOR HA LLEGADO!</h3><p style="font-size:12px;">Por favor sale a encontrarlo en tu punto de origen.</p>`;
                setTimeout(pollEstadoPasajero, 2000);
            } else if (data.estado === 'finalizado') {
                box.innerHTML = `<h3 style="color:#00E5FF; margin:0;">¡VIAJE FINALIZADO!</h3><p style="font-size:12px;">Gracias por viajar con VeloCity.</p>`;
            }
        }


        // --- CONDUCTOR LOGIC ---
        function iniciarModuloConductor() {
            fetch('/api/conductor/datos').then(r => r.json()).then(data => {
                if(data.registrado) {
                    document.getElementById('lblNombreCondHeader').innerText = `${data.nombre} (${data.vehiculo})`;
                    document.getElementById('lblSaldoWallet').innerText = `$${data.saldo.toFixed(2)} USD`;
                    mostrarVista('viewDashboardConductor');
                } else {
                    mostrarVista('viewRegistroConductor');
                }
            });
        }

        function toggleRequisitosMoto(val) {
            document.getElementById('boxCascos').style.display = val === 'Moto' ? 'block' : 'none';
        }

        async function completarRegistroConductor() {
            const nombre = document.getElementById('regNombreCond').value;
            const vehiculo = document.getElementById('regTipoVehiculo').value;
            const gps = document.getElementById('gpsCondInput').value;

            if(!nombre || !gps) { alert("Por favor completa los campos y comparte el GPS."); return; }

            await fetch('/api/conductor/registrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ nombre: nombre, vehiculo: vehiculo, ubicacion: gps })
            });

            iniciarModuloConductor();
        }

        async function toggleDispoCond(val) {
            const lbl = document.getElementById('lblEstadoCond');
            lbl.innerText = val ? "DISPONIBLE" : "DESCONECTADO";
            lbl.style.color = val ? "#00E5FF" : "#ff4b4b";

            await fetch('/api/conductor/disponibilidad', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ disponible: val })
            });

            if(val) pollSolicitudesConductor();
        }

        async function pollSolicitudesConductor() {
            if(!document.getElementById('chkDispoCond').checked) return;

            const res = await fetch('/api/conductor/ver_solicitud');
            const data = await res.json();
            const box = document.getElementById('boxSolicitudesCond');

            if(data.solicitud) {
                const sol = data.solicitud;
                box.innerHTML = `
                    <div style="background:#1C1C1F; border:1px solid #00E5FF; padding:15px; border-radius:14px; text-align:left;">
                        <b style="color:#00E5FF; font-size:14px;">⚡ ¡NUEVA SOLICITUD DE VIAJE!</b>
                        <p style="margin:5px 0; font-size:12px;">📍 <b>Origen:</b> ${sol.origen}</p>
                        <p style="margin:3px 0; font-size:12px;">🏁 <b>Destino:</b> ${sol.destino}</p>
                        <p style="margin:3px 0; font-size:12px;">💰 <b>Ganancia Net:</b> $${(sol.precio * 0.95).toFixed(2)} USD</p>
                        ${data.estado === 'esperando' ? `<button class="btn-main" onclick="cambiarEstadoConductor('en_camino')">ACEPTAR Y IR EN CAMINO</button>` : ''}
                        ${data.estado === 'en_camino' ? `<button class="btn-main" onclick="cambiarEstadoConductor('llego')">LLEGUÉ AL ORIGEN</button>` : ''}
                        ${data.estado === 'llego' ? `<button class="btn-main" onclick="cambiarEstadoConductor('finalizado')">FINALIZAR VIAJE Y COBRAR</button>` : ''}
                    </div>
                `;
            } else {
                box.innerHTML = `<p style="text-align:center; font-size:12px; color:#72767D;">Buscando solicitudes cercanas...</p>`;
            }

            setTimeout(pollSolicitudesConductor, 2000);
        }

        async function cambiarEstadoConductor(nuevoEstado) {
            const res = await fetch('/api/conductor/cambiar_estado_viaje', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ estado: nuevoEstado })
            });
            const data = await res.json();
            if(data.saldo !== undefined) {
                document.getElementById('lblSaldoWallet').innerText = `$${data.saldo.toFixed(2)} USD`;
            }
        }

        function retirarSaldo() {
            alert("Solicitud de retiro procesada a tu Pago Móvil personal.");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_APP)

# --- RUTAS DE API INTERACTIVAS ---

@app.route('/api/pasajero/solicitar', methods=['POST'])
def solicitar_pasajero():
    datos = request.json
    ESTADO_CONDUCTOR['solicitud_activa'] = datos
    ESTADO_CONDUCTOR['estado_viaje'] = 'esperando'
    return jsonify({'status': 'ok'})

@app.route('/api/pasajero/estado', methods=['GET'])
def estado_pasajero():
    return jsonify({'estado': ESTADO_CONDUCTOR['estado_viaje']})

@app.route('/api/conductor/datos', methods=['GET'])
def datos_conductor():
    return jsonify(ESTADO_CONDUCTOR)

@app.route('/api/conductor/registrar', methods=['POST'])
def registrar_conductor():
    datos = request.json
    ESTADO_CONDUCTOR['nombre'] = datos.get('nombre')
    ESTADO_CONDUCTOR['vehiculo'] = datos.get('vehiculo')
    ESTADO_CONDUCTOR['ubicacion'] = datos.get('ubicacion')
    ESTADO_CONDUCTOR['registrado'] = True
    return jsonify({'status': 'ok'})

@app.route('/api/conductor/disponibilidad', methods=['POST'])
def disponibilidad_conductor():
    datos = request.json
    ESTADO_CONDUCTOR['disponible'] = datos.get('disponible')
    return jsonify({'status': 'ok'})

@app.route('/api/conductor/ver_solicitud', methods=['GET'])
def ver_solicitud_cond():
    return jsonify({
        'solicitud': ESTADO_CONDUCTOR['solicitud_activa'],
        'estado': ESTADO_CONDUCTOR['estado_viaje']
    })

@app.route('/api/conductor/cambiar_estado_viaje', methods=['POST'])
def cambiar_estado_viaje():
    estado = request.json.get('estado')
    ESTADO_CONDUCTOR['estado_viaje'] = estado
    
    # Al finalizar el viaje, calcular el 95% para el conductor y 5% de comisión
    if estado == 'finalizado' and ESTADO_CONDUCTOR['solicitud_activa']:
        precio_total = float(ESTADO_CONDUCTOR['solicitud_activa'].get('precio', 3.50))
        ganancia_net = precio_total * 0.95
        ESTADO_CONDUCTOR['saldo'] += ganancia_net
        ESTADO_CONDUCTOR['solicitud_activa'] = None

    return jsonify({'status': 'ok', 'saldo': ESTADO_CONDUCTOR['saldo']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)