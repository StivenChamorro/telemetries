# ☀️ Sistema Fotovoltaico Inteligente con Telemetría IoT

Sistema embebido de generación, almacenamiento, regulación y monitoreo energético fotovoltaico acoplado a una plataforma web desarrollada en **Laravel** para la adquisición, persistencia y análisis de variables eléctricas en tiempo real.

---

## 📋 Tabla de Contenidos
1. [Descripción General y Contexto](#1-descripción-general-y-contexto)
2. [Arquitectura Física de la Maqueta](#2-arquitectura-física-de-la-maqueta)
3. [Componentes del Sistema (Hardware)](#3-componentes-del-sistema-hardware)
4. [Diagrama y Tabla de Conexiones](#4-diagrama-y-tabla-de-conexiones)
5. [Captura de Datos por Sensor y Variables del Sistema](#5-captura-de-datos-por-sensor-y-variables-del-sistema)
6. [Visualización y Gráficas del Dashboard](#6-visualización-y-gráficas-del-dashboard)
7. [Modelado Energético y Cálculos Teóricos](#7-modelado-energético-y-cálculos-teóricos)
8. [Validación Metrológica (Sensores vs. Multímetro)](#8-validación-metrológica-sensores-vs-multímetro)
9. [Flujo de Telemetría IoT (ESP32 ➔ Laravel)](#9-flujo-de-telemetría-iot-esp32--laravel)

---

## 1. Descripción General y Contexto

Este proyecto implementa una micro-red fotovoltaica autónoma instrumentada con sensores eléctricos y un microcontrolador **ESP32**. Su propósito es captar energía solar, almacenarla de forma segura en celdas de ion-litio para alimentar una carga luminosa (arreglo de 11 LEDs) y transmitir en tiempo real las variables físicas del sistema hacia un servidor local/web en **Laravel**.

El sistema permite evaluar:
* **Eficiencia de generación solar** bajo distintos ángulos de inclinación.
* **Balance neto de potencia** (energía generada vs. energía consumida).
* **Estado de carga (SoC) y autonomía** del banco de baterías.
* **Precisión metrológica** comparando las lecturas de los sensores IoT frente a un instrumento patrón (multímetro digital).

---

## 2. Arquitectura Física de la Maqueta

La estructura física está diseñada bajo un enfoque modular y funcional:
* **Techo Ajustable / Orientable:** Permite modificar el ángulo de incidencia del panel fotovoltaico respecto a la fuente lumínica para optimizar la captación de irradiancia solar.
* **Compartimento Técnico Oculto (Base):** Aísla y protege la electrónica de control (ESP32), los módulos de sensado, el cableado de potencia y el banco de baterías 18650, garantizando seguridad eléctrica y orden estructural.
* **Módulo de Carga Distribuida:** Circuito compuesto por 11 diodos LED distribuidos en la maqueta que simulan el consumo residencial o de iluminación del sistema.

---

## 3. Componentes del Sistema (Hardware)

| Componente | Definición Técnica | Función en el Proyecto |
| :--- | :--- | :--- |
| **Panel Solar Fotovoltaico** | Transductor optoelectrónico que convierte la radiación solar en corriente eléctrica continua ($DC$) mediante el efecto fotovoltaico. | Fuente primaria de generación energética del sistema. |
| **Microcontrolador ESP32** | Sistema en chip (SoC) de 32 bits con conectividad Wi-Fi/Bluetooth integrada, conversores analógico-digitales (ADC) y bus $I^2C$. | Cerebro central: lee los sensores, filtra y escala señales, calcula variables y envía los datos en formato JSON vía HTTP POST hacia Laravel. |
| **Divisor de Voltaje FZ0430** | Módulo resistivo de precisión (factor de reducción $5:1$) que atenúa tensiones de entrada hasta $25\text{ V}$ a niveles seguros ($<3.3\text{ V}$). | Acondiciona y mide el voltaje generado por el panel solar sin dañar los pines analógicos (ADC) de la ESP32. |
| **Sensor de Corriente ACS712** | Sensor lineal de corriente basado en el **Efecto Hall** que entrega una señal de voltaje proporcional al campo magnético generado por la corriente. | Mide en serie la corriente de generación ($I_{\text{solar}}$) proveniente del panel solar sin introducir pérdidas resistivas significativas. |
| **Sensor INA219 ($I^2C$)** | Monitor bidireccional de corriente y potencia en lado alto (*high-side*) con conversor ADC de 12 bits integrado y comunicación digital $I^2C$. | Mide con alta precisión el voltaje de carga/bus ($V_{\text{carga}}$), la corriente consumida por los LEDs ($I_{\text{carga}}$) y la potencia consumida ($P_{\text{carga}}$). |
| **Baterías Li-Ion 18650** | Celdas recargables de ion-litio con voltaje nominal de $3.7\text{ V}$ (rango operativo de $3.0\text{ V}$ descargada a $4.2\text{ V}$ carga completa). | Almacenamiento energético del sistema ($\sim 8.14\text{ Wh}$ de capacidad energética total). |
| **Módulo Cargador TP4056** | Controlador lineal de carga para baterías de ion-litio con sistema de protección integrado contra sobrecarga, sobredescarga y cortocircuito. | Gestiona de forma segura el flujo de carga hacia las baterías 18650 y protege su integridad electroquímica. |
| **Regulador Elevador (XL6009 / Boost)** | Convertidor DC-DC tipo *Step-Up* que eleva y estabiliza la tensión de salida hacia el riel de alimentación. | Mantiene un nivel de voltaje estable para alimentar el bus de carga y los componentes de control. |
| **Arreglo de 11 LEDs** | Diodos emisores de luz conectados en paralelo con sus respectivas resistencias limitadoras. | Representan la carga eléctrica constante del sistema ($\sim 0.08\text{ W}$ de consumo nominal). |

---

## 4. Diagrama y Tabla de Conexiones

> **Nota Crítica de Diseño:** Todos los módulos, sensores, fuente solar, baterías y la placa ESP32 comparten una **Tierra Común (`GND`)** para garantizar referencias de voltaje válidas y evitar errores de lectura o fallos en el bus $I^2C$.

### Conexiones de Sensores y Control hacia la ESP32

| Módulo / Sensor | Pin del Módulo | Pin en ESP32 | Protocolo / Tipo | Propósito de la Conexión |
| :--- | :--- | :--- | :--- | :--- |
| **FZ0430 (Voltaje Solar)** | `S` (Señal) | `GPIO 34` / `35` (ADC) | Analógico | Lectura del voltaje escalado del panel solar. |
| **FZ0430 (Voltaje Solar)** | `-` | `GND` | Alimentación | Referencia de tierra común. |
| **ACS712 (Corriente Solar)** | `OUT` | `GPIO 32` / `33` (ADC) | Analógico | Lectura de voltaje proporcional a la corriente solar. |
| **ACS712 (Corriente Solar)** | `VCC` / `GND` | `5V` (VIN) / `GND` | Alimentación | Polarización del circuito interno de efecto Hall. |
| **INA219 (Consumo Carga)** | `SDA` | `GPIO 21` (`SDA`) | Digital $I^2C$ | Línea de datos bidireccional del bus $I^2C$. |
| **INA219 (Consumo Carga)** | `SCL` | `GPIO 22` (`SCL`) | Digital $I^2C$ | Línea de reloj de sincronización del bus $I^2C$. |
| **INA219 (Consumo Carga)** | `VCC` / `GND` | `3.3V` / `GND` | Alimentación | Alimentación lógica segura compatible con ESP32. |

### Conexiones de Potencia (Flujo Energético)

1. **Rama de Generación:**
   * `Panel Solar (+)` $\rightarrow$ `Borne 1 ACS712` $\rightarrow$ `Borne 2 ACS712` $\rightarrow$ Entrada del módulo de carga (`TP4056`) y paralelo con entrada `VCC` del divisor `FZ0430`.
   * `Panel Solar (-)` $\rightarrow$ `GND` común y borne `GND` del `FZ0430`.
2. **Rama de Almacenamiento:**
   * Salida `B+` y `B-` del módulo `TP4056` conectadas directamente a los bornes positivo y negativo del portabaterías **18650**.
3. **Rama de Consumo (Carga):**
   * Salida de alimentación (`OUT+` / Elevador) $\rightarrow$ `VIN+` del sensor **INA219** $\rightarrow$ `VIN-` del sensor **INA219** $\rightarrow$ Ánodo común del arreglo de **11 LEDs**.
   * Cátodo de los **11 LEDs** $\rightarrow$ `GND` común.

---

## 5. Captura de Datos por Sensor y Variables del Sistema

### Datos Capturados Directamente por Hardware
* **Sensor FZ0430:** Captura la tensión bruta del panel solar ($V_{\text{solar}}$) en Voltios ($\text{V}$).
* **Sensor ACS712:** Captura la corriente entregada por el panel solar ($I_{\text{solar}}$) en Amperios ($\text{A}$).
* **Sensor INA219:** Captura el voltaje en el bus de carga ($V_{\text{carga}}$ en $\text{V}$) y la corriente consumida por los LEDs ($I_{\text{carga}}$ en $\text{A}$ o $\text{mA}$).

### Diccionario Completo de Variables (Backend Laravel & Frontend)

| Variable | Unidad | Origen | Descripción |
| :--- | :---: | :--- | :--- |
| `solar_voltage` | $\text{V}$ | Sensor FZ0430 | Voltaje instantáneo generado por el panel fotovoltaico. |
| `solar_current` | $\text{A}$ | Sensor ACS712 | Corriente instantánea suministrada por el panel solar. |
| `solar_power` | $\text{W}$ | Calculada | Potencia solar generada ($P_{\text{solar}} = V_{\text{solar}} \cdot I_{\text{solar}}$). |
| `load_voltage` | $\text{V}$ | Sensor INA219 | Voltaje medido en el riel de alimentación de la carga / batería. |
| `load_current` | $\text{A}$ | Sensor INA219 | Corriente instantánea demandada por los 11 LEDs. |
| `load_power` | $\text{W}$ | INA219 / Calc. | Potencia instantánea consumida por la carga ($P_{\text{carga}} = V_{\text{carga}} \cdot I_{\text{carga}}$). |
| `net_power` | $\text{W}$ | Calculada | Balance neto disponible para cargar la batería ($P_{\text{neta}} = P_{\text{solar}} - P_{\text{carga}}$). |
| `battery_percentage` | $\%$ | Calculada | Nivel estimado de carga de la batería 18650 mapeado linealmente entre $3.0\text{ V}$ ($0\%$) y $4.2\text{ V}$ ($100\%$). |
| `charge_time_hours` | $\text{h}$ | Calculada | Tiempo estimado para completar un ciclo de carga de batería ($0\%$ a $100\%$). |
| `autonomy_hours` | $\text{h}$ | Calculada | Tiempo estimado de autonomía alimentando únicamente la carga sin radiación solar. |

---

## 6. Visualización y Gráficas del Dashboard

El panel de control desarrollado en **Laravel** (`dashboard.blade.php`) organiza la telemetría en tarjetas KPI y series temporales interactivas:

1. **Tarjetas de Resumen en Tiempo Real (KPIs):**
   * Potencia Solar Máxima / Actual ($\text{W}$) y Energía Total Generada ($\text{Wh}$).
   * Consumo Actual de Carga LED ($\text{W}$) y Eficiencia de transferencia ($>90\%$).
   * **Nivel Estimado de Batería ($\%$ y $\text{V}$):** Indicador dedicado del estado de carga de la celda 18650.
   * **Tiempos Fundamentales:** Comparativa directa entre el tiempo de llenado (Panel $\rightarrow$ Batería) y el tiempo de autonomía (Batería $\rightarrow$ Carga).
2. **Gráficas Temporales (Series de Tiempo):**
   * **Gráfica de Potencia Solar Generada ($\text{W}$):** Evolución histórica de la generación fotovoltaica, permitiendo observar curvas de irradiancia y picos de producción.
   * **Gráfica de Consumo de Carga ($\text{W}$):** Estabilidad del consumo energético de los 11 LEDs a lo largo del tiempo.
   * **Gráfica de Nivel de Carga de Batería (Últimas 24h):** Curva de comportamiento porcentual y de voltaje de la batería durante ciclos de carga y descarga.

---

## 7. Modelado Energético y Cálculos Teóricos

A partir de los parámetros nominales del prototipo (capacidad de batería $\approx 8.14\text{ Wh}$, generación máxima $\approx 2.20\text{ W}$ y consumo constante de LEDs $\approx 0.08\text{ W}$):

* **Potencia Neta de Llenado:**
  $$P_{\text{neta}} = P_{\text{solar}} - P_{\text{carga}} = 2.20\text{ W} - 0.08\text{ W} = 2.12\text{ W}$$
* **Tiempo Teórico de Carga Completa (Panel $\rightarrow$ Batería):**
  $$t_{\text{carga}} = \frac{E_{\text{batería}}}{P_{\text{neta}}} = \frac{8.14\text{ Wh}}{2.12\text{ W}} \approx 3.83\text{ horas}$$
* **Tiempo de Autonomía del Sistema (Batería $\rightarrow$ Carga sin sol):**
  $$t_{\text{autonomía}} = \frac{E_{\text{batería}}}{P_{\text{carga}}} = \frac{8.14\text{ Wh}}{0.08\text{ W}} = 101.75\text{ horas} \quad (\approx 96\text{ horas reales considerando pérdidas})$$

---

## 8. Validación Metrológica (Sensores vs. Multímetro)

Para validar la confiabilidad del sistema de telemetría, se contrastaron las lecturas reportadas por la ESP32 frente a mediciones físicas directas tomadas con un **multímetro digital patrón**:

| Variable Medida | Valor Sensor (ESP32) | Valor Patrón (Multímetro) | Error / Diagnóstico Técnico |
| :--- | :---: | :---: | :--- |
| **Voltaje Solar ($V_{\text{solar}}$)** | $1.21\text{ V}$ | $1.87\text{ V}$ | **$35.29\%$** — Requiere ajuste de constante de multiplicación del divisor `FZ0430` y compensación de variación instantánea de irradiancia. |
| **Corriente Solar ($I_{\text{solar}}$)** | $1.83\text{ A}$ | $1.20\text{ A}$ | **$34.44\%$** — Deriva de punto cero (*offset*) e histéresis magnética propia del sensor de efecto Hall `ACS712`. |
| **Voltaje Carga / Batería** | $4.86\text{ V}$ *(INA219)* | $3.88\text{ V}$ *(Celda)* | **Diferencia de nodo físico:** El multímetro mide directamente la celda 18650 ($3.88\text{ V}$), mientras el `INA219` mide el riel regulado de salida ($4.86\text{ V}$). |
| **Potencia Consumida ($P_{\text{carga}}$)** | $0.084\text{ W}$ | $0.080\text{ W}$ | **$< 5.00\%$ (Alta Precisión)** — Valida la exactitud del sensor digital `INA219` y los cálculos de potencia en el firmware. |

---

## 9. Flujo de Telemetría IoT (ESP32 ➔ Laravel)

1. **Adquisición y Saneamiento (Firmware C++):** La ESP32 muestrea los pines analógicos e $I^2C$, valida que ningún valor sea `NaN` o infinito (`isnan()` / `isinf()`) para evitar errores de parseo JSON, y construye el *payload*:
   ```json
   {
     "solar_voltage": 1.8700,
     "solar_current": 1.2000,
     "load_voltage": 3.8800,
     "load_current": 0.0206
   }
   ```
2. **Transmisión HTTP:** Envío periódico mediante petición `POST` a través de red Wi-Fi hacia el endpoint `/api/telemetry` del servidor Laravel.
3. **Validación y Almacenamiento (Backend PHP/Laravel):** Laravel valida los tipos numéricos, calcula las variables derivadas (potencias, porcentajes y acumulados energéticos), almacena el registro en la base de datos y actualiza las vistas del *dashboard*.