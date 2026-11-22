<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Telemetría e IoT Avanzado - Solar & Carga</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen p-4 md:p-8 font-sans">

    <div class="max-w-7xl mx-auto space-y-6">
        
        <!-- Encabezado con Fecha y Estado On/Off -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-lg gap-4">
            <div>
                <h1 class="text-3xl font-extrabold text-white tracking-tight">Centro de Control ESP32</h1>
                <p class="text-sm text-slate-400 mt-1" id="current-date-time">Cargando fecha y hora...</p>
            </div>

            <div class="flex flex-wrap items-center gap-4">
                <!-- Indicador Conexión ESP32 -->
                <div id="connection-badge" class="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-700 border border-slate-600">
                    <span class="h-3 w-3 rounded-full bg-gray-500" id="status-dot"></span>
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-300" id="status-text">Desconocido</span>
                </div>

                <!-- Botón Global de Apagado / Encendido -->
                <button id="toggle-power-btn" onclick="toggleSystemPower()" class="px-5 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    <span id="btn-power-text">Apagar Sistema</span>
                </button>
            </div>
        </div>

        <!-- SECCIÓN 1: PRODUCCIÓN SOLAR -->
        <div>
            <h2 class="text-xl font-bold text-amber-400 mb-3 flex items-center gap-2">
                <svg class="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
                Producción Solar (Panel + FZ0430 + ACS712)
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Voltaje Solar -->
                <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 relative overflow-hidden">
                    <span class="text-xs font-bold text-amber-400 tracking-wider uppercase">Voltaje Solar</span>
                    <div class="flex items-baseline gap-2 mt-2">
                        <h3 class="text-4xl font-black text-white" id="solar-voltage">--</h3>
                        <span class="text-xl font-bold text-amber-400">V</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-3" id="solar-v-time">Sin registros</p>
                </div>

                <!-- Corriente Solar -->
                <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 relative overflow-hidden">
                    <span class="text-xs font-bold text-amber-400 tracking-wider uppercase">Corriente Solar</span>
                    <div class="flex items-baseline gap-2 mt-2">
                        <h3 class="text-4xl font-black text-white" id="solar-current">--</h3>
                        <span class="text-xl font-bold text-amber-400">A</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-3" id="solar-i-time">Sin registros</p>
                </div>

                <!-- Potencia Solar -->
                <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 relative overflow-hidden">
                    <span class="text-xs font-bold text-amber-400 tracking-wider uppercase">Potencia Generada</span>
                    <div class="flex items-baseline gap-2 mt-2">
                        <h3 class="text-4xl font-black text-white" id="solar-power">--</h3>
                        <span class="text-xl font-bold text-amber-400">W</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-3" id="solar-p-time">Sin registros</p>
                </div>
            </div>
        </div>

        <!-- SECCIÓN 2: CONSUMO DE CARGA Y BATERÍA -->
        <div>
            <h2 class="text-xl font-bold text-blue-400 mb-3 flex items-center gap-2">
                <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
                Consumo de Carga y Batería (11 LEDs + INA219)
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <!-- Voltaje Carga -->
                <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 relative overflow-hidden">
                    <span class="text-xs font-bold text-blue-400 tracking-wider uppercase">Voltaje de Carga</span>
                    <div class="flex items-baseline gap-2 mt-2">
                        <h3 class="text-4xl font-black text-white" id="load-voltage">--</h3>
                        <span class="text-xl font-bold text-blue-400">V</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-3" id="load-v-time">Sin registros</p>
                </div>

                <!-- Corriente Carga -->
                <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 relative overflow-hidden">
                    <span class="text-xs font-bold text-blue-400 tracking-wider uppercase">Corriente de Carga</span>
                    <div class="flex items-baseline gap-2 mt-2">
                        <h3 class="text-4xl font-black text-white" id="load-current">--</h3>
                        <span class="text-xl font-bold text-blue-400">A</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-3" id="load-i-time">Sin registros</p>
                </div>

                <!-- Potencia Carga -->
                <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 relative overflow-hidden">
                    <span class="text-xs font-bold text-blue-400 tracking-wider uppercase">Potencia Consumida</span>
                    <div class="flex items-baseline gap-2 mt-2">
                        <h3 class="text-4xl font-black text-white" id="load-power">--</h3>
                        <span class="text-xl font-bold text-blue-400">W</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-3" id="load-p-time">Sin registros</p>
                </div>

                <!-- Tarjeta Nivel Batería -->
                <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 relative overflow-hidden">
                    <span class="text-xs font-bold text-teal-400 tracking-wider uppercase">Nivel Estimado Batería</span>
                    <div class="flex items-baseline gap-2 mt-2">
                        <h3 class="text-4xl font-black text-white" id="battery-percentage">--</h3>
                        <span class="text-xl font-bold text-teal-400">%</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-3" id="battery-status">Voltaje: -- V</p>
                </div>
            </div>
        </div>

        <!-- GRÁFICAS DEL SISTEMA -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Gráfica Voltajes Comparativos -->
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700">
                <h3 class="text-md font-bold text-slate-200 mb-4 flex items-center gap-2">
                    <span class="h-3 w-3 rounded-full bg-amber-400"></span> Voltaje Solar vs. <span class="h-3 w-3 rounded-full bg-blue-400"></span> Voltaje Carga (V)
                </h3>
                <div class="h-64"><canvas id="voltageChart"></canvas></div>
            </div>

            <!-- Gráfica Corrientes Comparativas -->
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700">
                <h3 class="text-md font-bold text-slate-200 mb-4 flex items-center gap-2">
                    <span class="h-3 w-3 rounded-full bg-amber-400"></span> Corriente Solar vs. <span class="h-3 w-3 rounded-full bg-blue-400"></span> Corriente Carga (A)
                </h3>
                <div class="h-64"><canvas id="currentChart"></canvas></div>
            </div>

            <!-- Gráfica Potencia Solar -->
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700">
                <h3 class="text-md font-bold text-slate-200 mb-4 flex items-center gap-2">
                    <span class="h-3 w-3 rounded-full bg-emerald-400"></span> Potencia Generada (Solar - W)
                </h3>
                <div class="h-64"><canvas id="solarPowerChart"></canvas></div>
            </div>

            <!-- Gráfica Potencia Carga -->
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700">
                <h3 class="text-md font-bold text-slate-200 mb-4 flex items-center gap-2">
                    <span class="h-3 w-3 rounded-full bg-purple-400"></span> Potencia Consumida (LEDs - W)
                </h3>
                <div class="h-64"><canvas id="loadPowerChart"></canvas></div>
            </div>

            <!-- Gráfica Tendencia Batería -->
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 lg:col-span-2">
                <h3 class="text-md font-bold text-slate-200 mb-4 flex items-center gap-2">
                    <span class="h-3 w-3 rounded-full bg-teal-400"></span> Comportamiento de Batería / Voltaje Carga (V)
                </h3>
                <div class="h-64"><canvas id="batteryChart"></canvas></div>
            </div>
        </div>

        <!-- PANEL DE MÉTRICAS AGREGADAS -->
        <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700">
            <h3 class="text-lg font-bold text-white mb-4">Métricas Agregadas del Sistema</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div class="p-4 rounded-xl bg-slate-900/50 border border-slate-700/50">
                    <p class="text-xs text-slate-400 uppercase">Promedio V. Solar / Carga</p>
                    <p class="text-lg font-bold text-amber-400 mt-1"><span id="avg-v-solar">--</span> V / <span id="avg-v-load" class="text-blue-400">--</span> V</p>
                </div>
                <div class="p-4 rounded-xl bg-slate-900/50 border border-slate-700/50">
                    <p class="text-xs text-slate-400 uppercase">Pico Máx. Voltaje Solar</p>
                    <p class="text-lg font-bold text-amber-400 mt-1"><span id="max-v-solar">--</span> V</p>
                </div>
                <div class="p-4 rounded-xl bg-slate-900/50 border border-slate-700/50">
                    <p class="text-xs text-slate-400 uppercase">Promedio I. Solar / Carga</p>
                    <p class="text-lg font-bold text-amber-400 mt-1"><span id="avg-i-solar">--</span> A / <span id="avg-i-load" class="text-blue-400">--</span> A</p>
                </div>
                <div class="p-4 rounded-xl bg-slate-900/50 border border-slate-700/50">
                    <p class="text-xs text-slate-400 uppercase">Pico Máx. Corriente Carga</p>
                    <p class="text-lg font-bold text-blue-400 mt-1"><span id="max-i-load">--</span> A</p>
                </div>
            </div>
        </div>

    </div>

    <script>
        let currentSystemStatus = 'ON';
        let lastUpdateTimestamp = null;

        // Reloj en tiempo real
        function updateClock() {
            const now = new Date();
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
            document.getElementById('current-date-time').innerText = now.toLocaleDateString('es-ES', options);
        }
        setInterval(updateClock, 1000);
        updateClock();

        // Configuración Gráfica Voltajes
        const vCtx = document.getElementById('voltageChart').getContext('2d');
        const voltageChart = new Chart(vCtx, {
            type: 'line',
            data: { 
                labels: [], 
                datasets: [
                    { label: 'V. Solar (V)', borderColor: '#f59e0b', backgroundColor: 'rgba(245, 158, 11, 0.1)', data: [], fill: true, tension: 0.3 },
                    { label: 'V. Carga (V)', borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', data: [], fill: true, tension: 0.3 }
                ] 
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }, x: { ticks: { color: '#94a3b8' }, grid: { display: false } } } }
        });

        // Configuración Gráfica Corrientes
        const iCtx = document.getElementById('currentChart').getContext('2d');
        const currentChart = new Chart(iCtx, {
            type: 'line',
            data: { 
                labels: [], 
                datasets: [
                    { label: 'I. Solar (A)', borderColor: '#f59e0b', backgroundColor: 'rgba(245, 158, 11, 0.1)', data: [], fill: true, tension: 0.3 },
                    { label: 'I. Carga (A)', borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', data: [], fill: true, tension: 0.3 }
                ] 
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }, x: { ticks: { color: '#94a3b8' }, grid: { display: false } } } }
        });

        // Configuración Gráfica Potencia Solar
        const spCtx = document.getElementById('solarPowerChart').getContext('2d');
        const solarPowerChart = new Chart(spCtx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Potencia Solar (W)', borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', data: [], fill: true, tension: 0.3 }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }, x: { ticks: { color: '#94a3b8' }, grid: { display: false } } } }
        });

        // Configuración Gráfica Potencia Carga
        const lpCtx = document.getElementById('loadPowerChart').getContext('2d');
        const loadPowerChart = new Chart(lpCtx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Potencia Carga (W)', borderColor: '#c084fc', backgroundColor: 'rgba(192, 132, 252, 0.1)', data: [], fill: true, tension: 0.3 }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }, x: { ticks: { color: '#94a3b8' }, grid: { display: false } } } }
        });

        // Configuración Gráfica Batería
        const bCtx = document.getElementById('batteryChart').getContext('2d');
        const batteryChart = new Chart(bCtx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Voltaje Batería (V)', borderColor: '#2dd4bf', backgroundColor: 'rgba(45, 212, 191, 0.1)', data: [], fill: true, tension: 0.3 }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }, x: { ticks: { color: '#94a3b8' }, grid: { display: false } } } }
        });

        // Consultar datos de la API
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/telemetry');
                const data = await response.json();

                currentSystemStatus = data.system_status || 'ON';
                updatePowerButtonUI(currentSystemStatus);

                if (data.readings && data.readings.length > 0) {
                    const latest = data.readings[0];
                    lastUpdateTimestamp = new Date(latest.created_at).getTime();

                    // Lecturas Solar
                    const solarV = parseFloat(latest.solar_voltage || latest.voltage || 0);
                    const solarI = parseFloat(latest.solar_current || latest.current || 0);
                    const solarP = parseFloat(latest.solar_power || (solarV * solarI) || 0);

                    // Lecturas Carga
                    const loadV = parseFloat(latest.load_voltage || 0);
                    const loadI = parseFloat(latest.load_current || 0);
                    const loadP = parseFloat(latest.load_power || (loadV * loadI) || 0);

                    // Actualizar UI Solar
                    document.getElementById('solar-voltage').innerText = solarV.toFixed(2);
                    document.getElementById('solar-current').innerText = solarI.toFixed(2);
                    document.getElementById('solar-power').innerText = solarP.toFixed(2);

                    // Actualizar UI Carga
                    document.getElementById('load-voltage').innerText = loadV.toFixed(2);
                    document.getElementById('load-current').innerText = loadI.toFixed(2);
                    document.getElementById('load-power').innerText = loadP.toFixed(2);

                    // --- CÁLCULO DE BATERÍA ---
                    const vBateria = loadV; 
                    let porcentajeBateria = 0;
                    let vMin = 3.0; // Celda descargada
                    let vMax = 4.2; // Celda cargada al 100%

                    if (vBateria >= vMax) {
                        porcentajeBateria = 100;
                    } else if (vBateria <= vMin) {
                        porcentajeBateria = 0;
                    } else {
                        porcentajeBateria = ((vBateria - vMin) / (vMax - vMin)) * 100;
                    }

                    document.getElementById('battery-percentage').innerText = porcentajeBateria.toFixed(1);
                    document.getElementById('battery-status').innerText = `Voltaje actual: ${vBateria.toFixed(2)} V`;

                    const timeStr = new Date(latest.created_at).toLocaleTimeString();
                    document.getElementById('solar-v-time').innerText = `Última lectura: ${timeStr}`;
                    document.getElementById('solar-i-time').innerText = `Última lectura: ${timeStr}`;
                    document.getElementById('solar-p-time').innerText = `Última lectura: ${timeStr}`;
                    document.getElementById('load-v-time').innerText = `Última lectura: ${timeStr}`;
                    document.getElementById('load-i-time').innerText = `Última lectura: ${timeStr}`;
                    document.getElementById('load-p-time').innerText = `Última lectura: ${timeStr}`;

                    // Invertir orden para gráficas (de antiguo a nuevo)
                    const reversed = [...data.readings].reverse();
                    const labels = reversed.map(r => new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));

                    // Gráfica Voltajes
                    voltageChart.data.labels = labels;
                    voltageChart.data.datasets[0].data = reversed.map(r => r.solar_voltage || r.voltage || 0);
                    voltageChart.data.datasets[1].data = reversed.map(r => r.load_voltage || 0);
                    voltageChart.update('none');

                    // Gráfica Corrientes
                    currentChart.data.labels = labels;
                    currentChart.data.datasets[0].data = reversed.map(r => r.solar_current || r.current || 0);
                    currentChart.data.datasets[1].data = reversed.map(r => r.load_current || 0);
                    currentChart.update('none');

                    // Gráfica Potencia Solar
                    solarPowerChart.data.labels = labels;
                    solarPowerChart.data.datasets[0].data = reversed.map(r => r.solar_power || ((r.solar_voltage || r.voltage || 0) * (r.solar_current || r.current || 0)));
                    solarPowerChart.update('none');

                    // Gráfica Potencia Carga
                    loadPowerChart.data.labels = labels;
                    loadPowerChart.data.datasets[0].data = reversed.map(r => r.load_power || ((r.load_voltage || 0) * (r.load_current || 0)));
                    loadPowerChart.update('none');

                    // Gráfica Batería
                    batteryChart.data.labels = labels;
                    batteryChart.data.datasets[0].data = reversed.map(r => parseFloat(r.load_voltage || r.voltage || 0));
                    batteryChart.update('none');
                }

                // Actualizar Métricas Agregadas
                if (data.stats) {
                    document.getElementById('avg-v-solar').innerText = data.stats.avg_solar_voltage || data.stats.avg_voltage || '--';
                    document.getElementById('avg-v-load').innerText = data.stats.avg_load_voltage || '--';
                    document.getElementById('max-v-solar').innerText = data.stats.max_solar_voltage || data.stats.max_voltage || '--';
                    document.getElementById('avg-i-solar').innerText = data.stats.avg_solar_current || data.stats.avg_current || '--';
                    document.getElementById('avg-i-load').innerText = data.stats.avg_load_current || '--';
                    document.getElementById('max-i-load').innerText = data.stats.max_load_current || '--';
                }

                checkMicrocontrollerStatus();

            } catch (error) {
                console.error('Error cargando el dashboard:', error);
            }
        }

        // Verificar si el microcontrolador está respondiendo u "Offline"
        function checkMicrocontrollerStatus() {
            const badge = document.getElementById('connection-badge');
            const dot = document.getElementById('status-dot');
            const text = document.getElementById('status-text');

            const now = new Date().getTime();
            if (currentSystemStatus === 'OFF') {
                dot.className = "h-3 w-3 rounded-full bg-orange-500";
                text.innerText = "Sistema Desactivado";
                badge.className = "flex items-center space-x-2 px-3 py-1.5 rounded-full bg-orange-950/50 border border-orange-800 text-orange-400";
            } else if (!lastUpdateTimestamp || (now - lastUpdateTimestamp) > 10000) {
                dot.className = "h-3 w-3 rounded-full bg-red-500";
                text.innerText = "Apagado / Offline";
                badge.className = "flex items-center space-x-2 px-3 py-1.5 rounded-full bg-red-950/50 border border-red-800 text-red-400";
            } else {
                dot.className = "h-3 w-3 rounded-full bg-green-400 animate-pulse";
                text.innerText = "En Vivo";
                badge.className = "flex items-center space-x-2 px-3 py-1.5 rounded-full bg-green-950/50 border border-green-800 text-green-400";
            }
        }

        // Cambiar Estado Encendido/Apagado desde el Botón
        async function toggleSystemPower() {
            const nextStatus = currentSystemStatus === 'ON' ? 'OFF' : 'ON';
            try {
                const res = await fetch('/api/system/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify({ status: nextStatus })
                });
                const json = await res.json();
                currentSystemStatus = json.system_status;
                updatePowerButtonUI(currentSystemStatus);
                checkMicrocontrollerStatus();
            } catch (e) {
                alert('Error cambiando estado del sistema');
            }
        }

        function updatePowerButtonUI(status) {
            const btn = document.getElementById('toggle-power-btn');
            const btnText = document.getElementById('btn-power-text');

            if (status === 'ON') {
                btn.className = "px-5 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white";
                btnText.innerText = "Apagar Sistema";
            } else {
                btn.className = "px-5 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white";
                btnText.innerText = "Encender Sistema";
            }
        }

        // Ciclos de refresco
        loadDashboardData();
        setInterval(loadDashboardData, 3000); 
        setInterval(checkMicrocontrollerStatus, 1000); 
    </script>
</body>
</html>

```