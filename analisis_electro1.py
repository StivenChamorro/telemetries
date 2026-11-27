import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def trapz_compat(y, x):
    """Integra y respecto a x compatible con distintas versiones de NumPy."""
    if hasattr(np, "trapezoid"):
        return np.trapezoid(y, x)
    return np.trapz(y, x)


# ==============================================================================
# REQUERIMIENTO 1: PROCESAMIENTO DE DATOS Y MODELADO FÍSICO EN PYTHON
# ==============================================================================

def ley_ohm(voltaje=None, corriente=None, resistencia=None):
    """1.1 Calcula voltaje (V=I*R), corriente (I=V/R) o resistencia (R=V/I)."""
    v = np.asarray(voltaje, dtype=float) if voltaje is not None else None
    i = np.asarray(corriente, dtype=float) if corriente is not None else None
    r = np.asarray(resistencia, dtype=float) if resistencia is not None else None

    if v is None and i is not None and r is not None:
        return i * r
    if i is None and v is not None and r is not None:
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(np.abs(r) > 1e-12, v / r, np.nan)
    if r is None and v is not None and i is not None:
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(np.abs(i) > 1e-12, v / i, np.nan)
    raise ValueError("Proporciona exactamente dos variables: voltaje, corriente o resistencia.")


def calcular_potencia(voltaje, corriente):
    """1.1 Calcula potencia eléctrica instantánea P = V * I (en Watts)."""
    return np.asarray(voltaje, dtype=float) * np.asarray(corriente, dtype=float)


def calcular_energia_wh(potencia_w, tiempo_s):
    """1.1 Integra potencia (W) en el tiempo (s) mediante regla del trapecio y retorna Wh."""
    p = np.asarray(potencia_w, dtype=float)
    t = np.asarray(tiempo_s, dtype=float)
    if len(p) < 2:
        return 0.0
    return float(trapz_compat(p, t) / 3600.0)


def cargar_dataset(ruta_json):
    """1.2 Importa lecturas de sensores desde JSON en un DataFrame de Pandas."""
    with open(ruta_json, "r", encoding="utf-8") as f:
        raw = json.load(f)

    records = None
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and item.get("type") == "table" and isinstance(item.get("data"), list):
                records = item["data"]
                break
        if records is None:
            records = raw
    else:
        raise ValueError(f"Estructura JSON no reconocida en {ruta_json}")

    df = pd.DataFrame(records)
    num_cols = ["solar_voltage", "solar_current", "solar_power", "load_voltage", "load_current", "load_power"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["id"] = pd.to_numeric(df["id"], errors="coerce") if "id" in df.columns else np.arange(1, len(df) + 1)

    if "created_at" in df.columns:
        df["timestamp"] = pd.to_datetime(df["created_at"], errors="coerce")
        df = df.sort_values("timestamp").reset_index(drop=True)
        df["tiempo_s"] = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().astype(float)
    else:
        df["tiempo_s"] = np.arange(len(df), dtype=float) * 5.0

    df["tiempo_h"] = df["tiempo_s"] / 3600.0
    return df


def simular_datos_fotovoltaicos(
    n_muestras=400,
    dt_s=5.0,
    v_solar_base=5.0,
    i_solar_pico=0.4,
    r_carga_ohm=250.0,
    v_carga_inicial=4.85,
    ruido_std=0.02,
    semilla=42,
):
    """Simula un dataset fotovoltaico usando Ley de Ohm, potencia y energía acumulada."""
    rng = np.random.default_rng(semilla)
    t_s = np.arange(n_muestras, dtype=float) * dt_s
    t_h = t_s / 3600.0

    perfil_solar = np.clip(np.sin(np.linspace(0, np.pi, n_muestras)), 0.05, 1.0)
    v_solar_sim = np.maximum(
        0.0, float(v_solar_base) * (0.4 + 0.6 * perfil_solar) + rng.normal(0.0, ruido_std * 2.0, n_muestras)
    )
    i_solar_sim = np.maximum(
        0.0, float(i_solar_pico) * perfil_solar + rng.normal(0.0, ruido_std * 0.2, n_muestras)
    )
    p_solar_sim = calcular_potencia(v_solar_sim, i_solar_sim)

    v_carga_sim = np.clip(
        float(v_carga_inicial) - 0.15 * (t_s / max(t_s[-1], 1.0)) + 0.05 * perfil_solar + rng.normal(0.0, ruido_std * 0.5, n_muestras),
        2.5,
        12.0,
    )
    r_arr = np.full(n_muestras, max(float(r_carga_ohm), 1e-3))
    i_carga_sim = ley_ohm(voltaje=v_carga_sim, resistencia=r_arr)
    p_carga_sim = calcular_potencia(v_carga_sim, i_carga_sim)

    n = len(t_s)
    e_solar_wh = np.zeros(n)
    e_carga_wh = np.zeros(n)
    if n > 1:
        dt_h = np.diff(t_s) / 3600.0
        e_solar_wh[1:] = np.cumsum(0.5 * (p_solar_sim[:-1] + p_solar_sim[1:]) * dt_h)
        e_carga_wh[1:] = np.cumsum(0.5 * (p_carga_sim[:-1] + p_carga_sim[1:]) * dt_h)

    return pd.DataFrame({
        "id": np.arange(1, n_muestras + 1),
        "tiempo_s": t_s,
        "tiempo_h": t_h,
        "solar_voltage": v_solar_sim,
        "solar_current": i_solar_sim,
        "solar_power": p_solar_sim,
        "load_voltage": v_carga_sim,
        "load_current": i_carga_sim,
        "resistencia_carga_ohm": r_arr,
        "load_power": p_carga_sim,
        "energia_solar_sim_wh": e_solar_wh,
        "energia_carga_sim_wh": e_carga_wh,
    })


def procesar_variables(df):
    """1.3 Calcula potencias, resistencia equivalente y energía acumulada (Wh)."""
    out = df.copy()
    out["potencia_solar_calc_w"] = calcular_potencia(out["solar_voltage"], out["solar_current"])
    out["potencia_carga_calc_w"] = calcular_potencia(out["load_voltage"], out["load_current"])
    out["resistencia_carga_ohm"] = ley_ohm(voltaje=out["load_voltage"], corriente=out["load_current"])

    n = len(out)
    e_solar_wh = np.zeros(n)
    e_carga_wh = np.zeros(n)
    if n > 1:
        dt_h = np.diff(out["tiempo_s"].values) / 3600.0
        p_s_avg = 0.5 * (out["potencia_solar_calc_w"].values[:-1] + out["potencia_solar_calc_w"].values[1:])
        p_l_avg = 0.5 * (out["potencia_carga_calc_w"].values[:-1] + out["potencia_carga_calc_w"].values[1:])
        e_solar_wh[1:] = np.cumsum(p_s_avg * dt_h)
        e_carga_wh[1:] = np.cumsum(p_l_avg * dt_h)

    out["energia_solar_wh"] = e_solar_wh
    out["energia_carga_wh"] = e_carga_wh
    return out


def filtrar_ruido(df, ventana=5, sigma_umbral=3.0):
    """1.4 Filtra ruido impulsivo con MAD robusto y suaviza con media móvil."""
    out = df.copy()
    ventana = max(1, int(ventana))
    cols = ["solar_voltage", "solar_current", "load_voltage", "load_current", "potencia_solar_calc_w", "potencia_carga_calc_w"]
    for col in cols:
        serie = out[col].values.astype(float)
        mediana = np.nanmedian(serie)
        mad = np.nanmedian(np.abs(serie - mediana))
        escala = 1.4826 * mad if mad > 1e-12 else (np.nanstd(serie) if np.nanstd(serie) > 1e-12 else 1.0)
        z_rob = np.abs(serie - mediana) / escala
        sin_impulsos = np.where(z_rob > sigma_umbral, mediana, serie)
        out[f"{col}_limpia"] = pd.Series(sin_impulsos).rolling(window=ventana, min_periods=1, center=True).mean().values
    return out


# ==============================================================================
# REQUERIMIENTO 2: ANÁLISIS DE DATOS Y EFICIENCIA EN PYTHON
# ==============================================================================

def calcular_eficiencia_convertidor(df):
    """2.1 Calcula eficiencia porcentual eta = (P_carga / P_solar) * 100."""
    out = df.copy()
    p_in = out["potencia_solar_calc_w_limpia"].values
    p_out = out["potencia_carga_calc_w_limpia"].values
    with np.errstate(divide="ignore", invalid="ignore"):
        ef = np.where(p_in > 0.05, (p_out / p_in) * 100.0, np.nan)
    out["eficiencia_pct_raw"] = ef
    out["eficiencia_pct"] = np.where((ef >= 0.0) & (ef <= 100.0), ef, np.nan)
    return out


def calcular_errores_teorico_real(df):
    """2.2 Calcula diferencia absoluta y porcentual entre potencia cruda y filtrada."""
    out = df.copy()
    p_ref = out["potencia_carga_calc_w_limpia"].values
    p_raw = out["load_power"].values
    with np.errstate(divide="ignore", invalid="ignore"):
        err_pct = np.where(np.abs(p_ref) > 1e-6, ((p_raw - p_ref) / p_ref) * 100.0, 0.0)
    out["error_potencia_abs_w"] = np.abs(p_raw - p_ref)
    out["error_potencia_pct"] = err_pct
    return out


def modelar_descarga_bateria(df, v_corte=3.3):
    """2.3 Ajusta regresión lineal de voltaje vs. tiempo y estima autonomía al voltaje de corte."""
    t = df["tiempo_s"].values
    v = df["load_voltage_limpia"].values
    mask = np.isfinite(t) & np.isfinite(v)
    t_m, v_m = t[mask], v[mask]

    if len(t_m) >= 2 and np.ptp(t_m) > 0:
        pendiente_v_s, intercepto_v = np.polyfit(t_m, v_m, 1)
        v_pred = pendiente_v_s * t_m + intercepto_v
        ss_res = np.sum((v_m - v_pred) ** 2)
        ss_tot = np.sum((v_m - np.mean(v_m)) ** 2)
        r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else 0.0
        autonomia_h = max(0.0, (v_corte - intercepto_v) / pendiente_v_s) / 3600.0 if pendiente_v_s < -1e-9 else None
    else:
        pendiente_v_s, intercepto_v, r2, autonomia_h = 0.0, float(v_m[0]) if len(v_m) else 0.0, 0.0, None

    out = df.copy()
    out["voltaje_regresion_v"] = pendiente_v_s * t + intercepto_v
    resumen = {
        "pendiente_v_por_h": float(pendiente_v_s * 3600.0),
        "intercepto_v": float(intercepto_v),
        "r2": r2,
        "v_corte": float(v_corte),
        "autonomia_estimada_h": float(autonomia_h) if autonomia_h is not None else None,
    }
    return out, resumen


def detectar_perdidas_tension(df, umbral_caida_pct=5.0):
    """2.4 Detecta caídas de tensión mediante análisis de arrays con NumPy."""
    v = df["load_voltage_limpia"].values
    dv = np.diff(v, prepend=v[0])
    v_prev = np.roll(v, 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        pct_cambio = np.where(np.abs(v_prev) > 1e-6, (dv / v_prev) * 100.0, 0.0)
    pct_cambio[0] = 0.0

    p5_v = float(np.percentile(v, 5))
    caida_brusca = pct_cambio < -umbral_caida_pct

    out = df.copy()
    out["delta_v_paso"] = dv
    out["caida_tension_detectada"] = caida_brusca
    resumen = {
        "total_eventos_caida_brusca": int(np.sum(caida_brusca)),
        "voltaje_min_v": float(np.min(v)),
        "voltaje_max_v": float(np.max(v)),
        "percentil_5_v": p5_v,
        "registros_en_o_bajo_p5": int(np.sum(v <= p5_v)),
    }
    return out, resumen


def comparar_simulado_vs_real(df_real, df_sim, r_carga_ohm=250.0):
    """Compara datos reales vs. simulados usando Ley de Ohm, potencia y energía en Wh."""
    n_puntos = min(len(df_real), len(df_sim), 400)
    t_norm = np.linspace(0.0, 1.0, n_puntos)

    v_real = np.interp(t_norm, np.linspace(0.0, 1.0, len(df_real)), df_real["load_voltage"].astype(float).values)
    i_real_ohm = ley_ohm(voltaje=v_real, resistencia=np.full(n_puntos, float(r_carga_ohm)))
    p_real_ohm = calcular_potencia(v_real, i_real_ohm)

    v_sim = np.interp(t_norm, np.linspace(0.0, 1.0, len(df_sim)), df_sim["load_voltage"].astype(float).values)
    i_sim_ohm = ley_ohm(voltaje=v_sim, resistencia=np.full(n_puntos, float(r_carga_ohm)))
    p_sim_ohm = calcular_potencia(v_sim, i_sim_ohm)

    duracion_real_s = max(float(df_real["tiempo_s"].iloc[-1]) if len(df_real) > 1 else n_puntos * 5.0, 1.0)
    duracion_sim_s = max(float(df_sim["tiempo_s"].iloc[-1]) if len(df_sim) > 1 else n_puntos * 5.0, 1.0)
    t_real_s = t_norm * duracion_real_s
    t_sim_s = t_norm * duracion_sim_s

    e_real_wh = calcular_energia_wh(p_real_ohm, t_real_s)
    e_sim_wh = calcular_energia_wh(p_sim_ohm, t_sim_s)

    pct_sim_voltaje = float(np.mean(np.minimum(v_sim, v_real) / np.maximum(np.maximum(v_sim, v_real), 1e-9)) * 100.0)
    pct_sim_potencia = float(np.mean(np.minimum(p_sim_ohm, p_real_ohm) / np.maximum(np.maximum(p_sim_ohm, p_real_ohm), 1e-9)) * 100.0)
    pct_sim_energia = float((min(e_sim_wh, e_real_wh) / max(max(e_sim_wh, e_real_wh), 1e-9)) * 100.0)
    pct_sim_global = float(np.mean([pct_sim_voltaje, pct_sim_potencia, pct_sim_energia]))

    return {
        "progreso_pct": t_norm * 100.0,
        "v_real": v_real,
        "v_sim": v_sim,
        "i_real_ohm": i_real_ohm,
        "i_sim_ohm": i_sim_ohm,
        "p_real_ohm": p_real_ohm,
        "p_sim_ohm": p_sim_ohm,
        "e_real_wh": e_real_wh,
        "e_sim_wh": e_sim_wh,
        "pct_sim_voltaje": pct_sim_voltaje,
        "pct_sim_potencia": pct_sim_potencia,
        "pct_sim_energia": pct_sim_energia,
        "pct_sim_global": pct_sim_global,
    }


# ==============================================================================
# REQUERIMIENTO 3: VISUALIZACIÓN, VALIDACIÓN E INTERFAZ GRÁFICA (TKINTER)
# ==============================================================================

def generar_tabla_resumen(nombre, df, res_descarga, res_perdidas):
    """3.2 & 3.3 Construye DataFrame resumen con desviación estándar vía NumPy."""
    return pd.DataFrame([{
        "dataset": nombre,
        "muestras": int(len(df)),
        "v_solar_media_v": round(float(np.mean(df["solar_voltage_limpia"].values)), 4),
        "v_solar_std_np_v": round(float(np.std(df["solar_voltage_limpia"].values, ddof=1)), 4),
        "v_carga_media_v": round(float(np.mean(df["load_voltage_limpia"].values)), 4),
        "v_carga_std_np_v": round(float(np.std(df["load_voltage_limpia"].values, ddof=1)), 4),
        "p_carga_media_w": round(float(np.mean(df["potencia_carga_calc_w_limpia"].values)), 4),
        "energia_solar_wh": round(float(df["energia_solar_wh"].iloc[-1]), 6),
        "energia_carga_wh": round(float(df["energia_carga_wh"].iloc[-1]), 6),
        "eficiencia_media_pct": round(float(np.nanmean(df["eficiencia_pct"].values)), 2),
        "error_abs_medio_w": round(float(np.mean(df["error_potencia_abs_w"].values)), 6),
        "r2_descarga": round(res_descarga["r2"], 4),
        "eventos_caida_v": res_perdidas["total_eventos_caida_brusca"],
    }])


class AplicacionElectro1:
    """Interfaz gráfica interactiva para análisis, simulación y validación ELECTRO-1."""

    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Fotovoltaico y Validación ELECTRO-1")
        self.root.geometry("1320x860")
        self.root.configure(bg="#1e222a")

        self.datasets_raw = {}
        self.procesados = {}
        self.detalles = {}
        self.df_resumen_actual = pd.DataFrame()
        self.comparacion_actual = None

        self._cargar_archivos_iniciales()
        self._construir_ui()
        self.actualizar_analisis()

    def _cargar_archivos_iniciales(self):
        for nombre, archivo in [("sim_solar_400-v2", "sim_solar_400-v2.json"), ("telemetries", "telemetries.json")]:
            if os.path.exists(archivo):
                try:
                    self.datasets_raw[nombre] = cargar_dataset(archivo)
                except Exception as e:
                    messagebox.showwarning("Aviso de carga", f"No se pudo cargar {archivo}: {e}")

        if "simulado_ohm" not in self.datasets_raw:
            self.datasets_raw["simulado_ohm"] = simular_datos_fotovoltaicos(n_muestras=400)

    def _construir_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e222a")
        style.configure("TLabelframe", background="#252a34", foreground="#eaeaea")
        style.configure("TLabelframe.Label", background="#252a34", foreground="#4fc3f7", font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background="#252a34", foreground="#eaeaea", font=("Segoe UI", 9))
        style.configure("Header.TLabel", background="#1e222a", foreground="#4fc3f7", font=("Segoe UI", 13, "bold"))
        style.configure("TButton", font=("Segoe UI", 9, "bold"))

        top_bar = ttk.Frame(self.root, padding=(12, 8))
        top_bar.pack(fill=tk.X)
        ttk.Label(top_bar, text="Panel Interactivo de Telemetría Solar (ELECTRO-1)", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Simular Nuevos Datos", command=self.regenerar_simulacion).pack(side=tk.RIGHT, padx=4)
        ttk.Button(top_bar, text="Cargar otro JSON...", command=self.cargar_json_externo).pack(side=tk.RIGHT, padx=4)
        ttk.Button(top_bar, text="Exportar CSV Resumen", command=self.exportar_csv).pack(side=tk.RIGHT, padx=4)
        ttk.Button(top_bar, text="Guardar Gráfica PNG", command=self.exportar_png).pack(side=tk.RIGHT, padx=4)

        main_frame = ttk.Frame(self.root, padding=(10, 5))
        main_frame.pack(fill=tk.BOTH, expand=True)

        ctrl_panel = ttk.LabelFrame(main_frame, text="Parámetros del Pipeline", padding=10, width=305)
        ctrl_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        ctrl_panel.pack_propagate(False)

        ttk.Label(ctrl_panel, text="Dataset activo para inspección:").pack(anchor=tk.W, pady=(2, 3))
        self.var_dataset = tk.StringVar(value=next(iter(self.datasets_raw.keys()), ""))
        self.combo_dataset = ttk.Combobox(ctrl_panel, textvariable=self.var_dataset, values=list(self.datasets_raw.keys()), state="readonly")
        self.combo_dataset.pack(fill=tk.X, pady=(0, 8))
        self.combo_dataset.bind("<<ComboboxSelected>>", lambda e: self.actualizar_analisis())

        self.var_ventana = tk.IntVar(value=5)
        self.lbl_ventana = ttk.Label(ctrl_panel, text="Ventana Media Móvil: 5 muestras")
        self.lbl_ventana.pack(anchor=tk.W)
        ttk.Scale(ctrl_panel, from_=1, to=25, variable=self.var_ventana, command=self._on_slider).pack(fill=tk.X, pady=(1, 6))

        self.var_sigma = tk.DoubleVar(value=3.0)
        self.lbl_sigma = ttk.Label(ctrl_panel, text="Umbral Ruido MAD (σ): 3.00")
        self.lbl_sigma.pack(anchor=tk.W)
        ttk.Scale(ctrl_panel, from_=1.0, to=6.0, variable=self.var_sigma, command=self._on_slider).pack(fill=tk.X, pady=(1, 6))

        self.var_caida = tk.DoubleVar(value=5.0)
        self.lbl_caida = ttk.Label(ctrl_panel, text="Umbral Caída Tensión: 5.00 %")
        self.lbl_caida.pack(anchor=tk.W)
        ttk.Scale(ctrl_panel, from_=0.5, to=15.0, variable=self.var_caida, command=self._on_slider).pack(fill=tk.X, pady=(1, 6))

        self.var_vcorte = tk.DoubleVar(value=3.3)
        self.lbl_vcorte = ttk.Label(ctrl_panel, text="Voltaje Corte Batería: 3.30 V")
        self.lbl_vcorte.pack(anchor=tk.W)
        ttk.Scale(ctrl_panel, from_=2.8, to=4.2, variable=self.var_vcorte, command=self._on_slider).pack(fill=tk.X, pady=(1, 8))

        ttk.Label(ctrl_panel, text="Simulación — Voltaje Solar Base (V):").pack(anchor=tk.W, pady=(2, 2))
        self.var_vsolar_sim = tk.DoubleVar(value=5.0)
        ttk.Entry(ctrl_panel, textvariable=self.var_vsolar_sim).pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ctrl_panel, text="Simulación — Corriente Solar Pico (A):").pack(anchor=tk.W, pady=(2, 2))
        self.var_isolar_sim = tk.DoubleVar(value=0.4)
        ttk.Entry(ctrl_panel, textvariable=self.var_isolar_sim).pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ctrl_panel, text="Simulación — Resistencia Carga (Ω):").pack(anchor=tk.W, pady=(2, 2))
        self.var_rcarga_sim = tk.DoubleVar(value=250.0)
        ttk.Entry(ctrl_panel, textvariable=self.var_rcarga_sim).pack(fill=tk.X, pady=(0, 8))

        ttk.Button(ctrl_panel, text="Recalcular Pipeline", command=self.actualizar_analisis).pack(fill=tk.X, pady=(0, 8))

        ttk.Label(ctrl_panel, text="Diagnóstico Rápido:", font=("Segoe UI", 9, "bold"), foreground="#81c784").pack(anchor=tk.W, pady=(2, 3))
        self.txt_diagnostico = tk.Text(ctrl_panel, height=13, bg="#181b20", fg="#e0e0e0", font=("Consolas", 9), relief=tk.FLAT, padx=8, pady=6)
        self.txt_diagnostico.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tab_graficas = ttk.Frame(notebook)
        notebook.add(tab_graficas, text="Gráficas Comparativas")
        self.fig, self.axes = plt.subplots(2, 2, figsize=(10, 6.8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab_graficas)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        NavigationToolbar2Tk(self.canvas, tab_graficas).update()

        tab_sim_real = ttk.Frame(notebook)
        notebook.add(tab_sim_real, text="Simulado vs. Real (%)")
        self.fig_comp, self.axes_comp = plt.subplots(1, 2, figsize=(10, 4.8), dpi=100)
        self.canvas_comp = FigureCanvasTkAgg(self.fig_comp, master=tab_sim_real)
        self.canvas_comp.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        NavigationToolbar2Tk(self.canvas_comp, tab_sim_real).update()

        tab_tabla = ttk.Frame(notebook, padding=10)
        notebook.add(tab_tabla, text="Tabla Resumen Estadístico")
        self.tree = ttk.Treeview(tab_tabla, show="headings", height=10)
        self.tree.pack(fill=tk.BOTH, expand=True)

        tab_ohm = ttk.LabelFrame(notebook, text="Simulador Interactivo de Ley de Ohm y Potencia (Req. 1.1)", padding=20)
        notebook.add(tab_ohm, text="Calculadora Ley de Ohm")
        self._construir_calculadora_ohm(tab_ohm)

    def _construir_calculadora_ohm(self, parent):
        ttk.Label(parent, text="Ingresa exactamente DOS valores (deja vacío el que deseas calcular):").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 12))
        self.ent_v = ttk.Entry(parent, width=20)
        self.ent_i = ttk.Entry(parent, width=20)
        self.ent_r = ttk.Entry(parent, width=20)

        ttk.Label(parent, text="Voltaje V (Voltios):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_v.grid(row=1, column=1, pady=4, padx=8)
        ttk.Label(parent, text="Corriente I (Amperios):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.ent_i.grid(row=2, column=1, pady=4, padx=8)
        ttk.Label(parent, text="Resistencia R (Ohmios):").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.ent_r.grid(row=3, column=1, pady=4, padx=8)

        ttk.Button(parent, text="Calcular Variable y Potencia", command=self._calcular_ohm_ui).grid(row=4, column=0, columnspan=2, pady=12)
        self.lbl_res_ohm = ttk.Label(parent, text="Resultado: —", font=("Consolas", 10, "bold"), foreground="#4fc3f7")
        self.lbl_res_ohm.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=6)

    def _calcular_ohm_ui(self):
        try:
            v = float(self.ent_v.get().strip()) if self.ent_v.get().strip() else None
            i = float(self.ent_i.get().strip()) if self.ent_i.get().strip() else None
            r = float(self.ent_r.get().strip()) if self.ent_r.get().strip() else None

            if v is None:
                v = float(ley_ohm(corriente=i, resistencia=r))
            elif i is None:
                i = float(ley_ohm(voltaje=v, resistencia=r))
            elif r is None:
                r = float(ley_ohm(voltaje=v, corriente=i))
            else:
                raise ValueError("Deja exactamente un campo vacío para calcularlo.")

            p = float(calcular_potencia(v, i))
            self.lbl_res_ohm.config(text=f"V = {v:.4f} V | I = {i:.4f} A | R = {r:.4f} Ω | Potencia P = {p:.4f} W")
        except Exception as e:
            messagebox.showerror("Error de cálculo", str(e))

    def _on_slider(self, _=None):
        v_int = max(1, int(round(self.var_ventana.get())))
        sig = round(float(self.var_sigma.get()), 2)
        cai = round(float(self.var_caida.get()), 2)
        vco = round(float(self.var_vcorte.get()), 2)

        self.lbl_ventana.config(text=f"Ventana Media Móvil: {v_int} muestras")
        self.lbl_sigma.config(text=f"Umbral Ruido MAD (σ): {sig:.2f}")
        self.lbl_caida.config(text=f"Umbral Caída Tensión: {cai:.2f} %")
        self.lbl_vcorte.config(text=f"Voltaje Corte Batería: {vco:.2f} V")
        self.actualizar_analisis()

    def _leer_parametros_simulacion(self):
        v_sol = float(self.var_vsolar_sim.get())
        i_sol = float(self.var_isolar_sim.get())
        r_car = float(self.var_rcarga_sim.get())
        if r_car <= 0:
            raise ValueError("La resistencia de carga debe ser mayor que 0 Ω.")
        return v_sol, i_sol, r_car

    def regenerar_simulacion(self):
        try:
            v_sol, i_sol, r_car = self._leer_parametros_simulacion()
            semilla_nueva = int(np.random.default_rng().integers(1, 10000))
            self.datasets_raw["simulado_ohm"] = simular_datos_fotovoltaicos(
                n_muestras=400,
                v_solar_base=v_sol,
                i_solar_pico=i_sol,
                r_carga_ohm=r_car,
                semilla=semilla_nueva,
            )
            self.combo_dataset["values"] = list(self.datasets_raw.keys())
            self.actualizar_analisis()
        except Exception as e:
            messagebox.showerror("Parámetros de simulación", str(e))

    def cargar_json_externo(self):
        ruta = filedialog.askopenfilename(title="Seleccionar archivo JSON de telemetría", filetypes=[("Archivos JSON", "*.json")])
        if not ruta:
            return
        try:
            nombre = os.path.splitext(os.path.basename(ruta))[0]
            self.datasets_raw[nombre] = cargar_dataset(ruta)
            self.combo_dataset["values"] = list(self.datasets_raw.keys())
            self.var_dataset.set(nombre)
            self.actualizar_analisis()
        except Exception as e:
            messagebox.showerror("Error al cargar JSON", str(e))

    def actualizar_analisis(self):
        if not self.datasets_raw:
            return

        ventana = max(1, int(round(self.var_ventana.get())))
        sigma = float(self.var_sigma.get())
        caida = float(self.var_caida.get())
        vcorte = float(self.var_vcorte.get())

        try:
            _, _, r_car = self._leer_parametros_simulacion()
        except Exception:
            r_car = 250.0

        tablas = []
        self.procesados.clear()
        self.detalles.clear()

        for nombre, df_raw in self.datasets_raw.items():
            df = procesar_variables(df_raw)
            df = filtrar_ruido(df, ventana=ventana, sigma_umbral=sigma)
            df = calcular_eficiencia_convertidor(df)
            df = calcular_errores_teorico_real(df)
            df, res_desc = modelar_descarga_bateria(df, v_corte=vcorte)
            df, res_perd = detectar_perdidas_tension(df, umbral_caida_pct=caida)

            self.procesados[nombre] = df
            self.detalles[nombre] = {"descarga": res_desc, "perdidas": res_perd}
            tablas.append(generar_tabla_resumen(nombre, df, res_desc, res_perd))

        df_real = self.datasets_raw.get("telemetries")
        if df_real is None:
            df_real = next(iter(self.datasets_raw.values()))

        df_sim = self.datasets_raw.get("simulado_ohm")
        if df_sim is None:
            df_sim = next(iter(self.datasets_raw.values()))

        self.comparacion_actual = comparar_simulado_vs_real(df_real, df_sim, r_carga_ohm=r_car)

        self.df_resumen_actual = pd.concat(tablas, ignore_index=True)
        self._actualizar_tabla_ui()
        self._actualizar_graficas_ui()
        self._actualizar_grafica_comparacion_ui()
        self._actualizar_diagnostico_ui()

    def _actualizar_diagnostico_ui(self):
        activo = self.var_dataset.get()
        if activo not in self.procesados:
            return
        df = self.procesados[activo]
        desc = self.detalles[activo]["descarga"]
        perd = self.detalles[activo]["perdidas"]
        comp = self.comparacion_actual or {}

        aut_txt = f"{desc['autonomia_estimada_h']:.2f} h" if desc["autonomia_estimada_h"] is not None else "No proyecta descarga"
        texto = (
            f"Dataset: {activo}\n"
            f"Muestras: {len(df)}\n"
            f"-----------------------------\n"
            f"V_carga media: {np.mean(df['load_voltage_limpia']):.4f} V\n"
            f"V_carga std:   {np.std(df['load_voltage_limpia'], ddof=1):.4f} V\n"
            f"E_solar total: {df['energia_solar_wh'].iloc[-1]:.5f} Wh\n"
            f"E_carga total: {df['energia_carga_wh'].iloc[-1]:.5f} Wh\n"
            f"Efic. media:   {np.nanmean(df['eficiencia_pct']):.2f} %\n"
            f"-----------------------------\n"
            f"Autonomía:     {aut_txt}\n"
            f"Caídas bruscas:{perd['total_eventos_caida_brusca']}\n"
            f"-----------------------------\n"
            f"Sim vs Real:   {comp.get('pct_sim_global', 0.0):.1f} %\n"
            f"  - Voltaje:   {comp.get('pct_sim_voltaje', 0.0):.1f} %\n"
            f"  - Potencia:  {comp.get('pct_sim_potencia', 0.0):.1f} %\n"
            f"  - Energía:   {comp.get('pct_sim_energia', 0.0):.1f} %\n"
        )
        self.txt_diagnostico.delete("1.0", tk.END)
        self.txt_diagnostico.insert(tk.END, texto)

    def _actualizar_tabla_ui(self):
        self.tree.delete(*self.tree.get_children())
        cols = list(self.df_resumen_actual.columns)
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=115, anchor=tk.CENTER)
        for _, row in self.df_resumen_actual.iterrows():
            self.tree.insert("", tk.END, values=list(row))

    def _actualizar_graficas_ui(self):
        activo = self.var_dataset.get()
        if activo not in self.procesados:
            return
        df = self.procesados[activo]

        for ax in self.axes.flat:
            ax.clear()

        self.axes[0, 0].plot(df["tiempo_h"], df["load_power"], alpha=0.45, label="Cruda (W)")
        self.axes[0, 0].plot(df["tiempo_h"], df["potencia_carga_calc_w_limpia"], linewidth=1.6, label="Filtrada (W)")
        self.axes[0, 0].set_title(f"Potencia en Carga ({activo})")
        self.axes[0, 0].legend(fontsize=8)
        self.axes[0, 0].grid(True, alpha=0.3)

        self.axes[0, 1].plot(df["tiempo_h"], df["load_voltage"], alpha=0.45, label="Medido (V)")
        self.axes[0, 1].plot(df["tiempo_h"], df["load_voltage_limpia"], linewidth=1.5, label="Filtrado (V)")
        self.axes[0, 1].plot(df["tiempo_h"], df["voltaje_regresion_v"], "--", linewidth=1.5, label="Regresión (V)")
        self.axes[0, 1].set_title(f"Voltaje y Regresión ({activo})")
        self.axes[0, 1].legend(fontsize=8)
        self.axes[0, 1].grid(True, alpha=0.3)

        self.axes[1, 0].plot(df["tiempo_h"], df["energia_solar_wh"], label="Energía Solar (Wh)")
        self.axes[1, 0].plot(df["tiempo_h"], df["energia_carga_wh"], label="Energía Carga (Wh)")
        self.axes[1, 0].set_title("Energía Acumulada (Trapecios)")
        self.axes[1, 0].legend(fontsize=8)
        self.axes[1, 0].grid(True, alpha=0.3)

        for nombre, d_item in self.procesados.items():
            ef_valida = d_item["eficiencia_pct"].dropna()
            if not ef_valida.empty:
                self.axes[1, 1].hist(ef_valida, bins=25, alpha=0.6, label=f"{nombre} (%)")
        self.axes[1, 1].set_title("Distribución de Eficiencia (0–100%)")
        self.axes[1, 1].legend(fontsize=8)
        self.axes[1, 1].grid(True, alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()

    def _actualizar_grafica_comparacion_ui(self):
        comp = self.comparacion_actual
        if not comp:
            return
        for ax in self.axes_comp.flat:
            ax.clear()

        self.axes_comp[0].plot(comp["progreso_pct"], comp["v_real"], label="Real (V)")
        self.axes_comp[0].plot(comp["progreso_pct"], comp["v_sim"], "--", label="Simulado (V)")
        self.axes_comp[0].set_title(f"Voltaje Carga — Similitud: {comp['pct_sim_voltaje']:.1f}%")
        self.axes_comp[0].set_xlabel("Progreso (%)")
        self.axes_comp[0].set_ylabel("Voltaje (V)")
        self.axes_comp[0].legend(fontsize=8)
        self.axes_comp[0].grid(True, alpha=0.3)

        self.axes_comp[1].plot(comp["progreso_pct"], comp["p_real_ohm"], label="Real P=V²/R (W)")
        self.axes_comp[1].plot(comp["progreso_pct"], comp["p_sim_ohm"], "--", label="Simulado P=V²/R (W)")
        self.axes_comp[1].set_title(f"Potencia (Ley de Ohm) — Similitud: {comp['pct_sim_potencia']:.1f}%")
        self.axes_comp[1].set_xlabel("Progreso (%)")
        self.axes_comp[1].set_ylabel("Potencia (W)")
        self.axes_comp[1].legend(fontsize=8)
        self.axes_comp[1].grid(True, alpha=0.3)

        self.fig_comp.suptitle(
            f"Simulado vs. Real | Global: {comp['pct_sim_global']:.1f}% (Energía: {comp['pct_sim_energia']:.1f}%)",
            fontsize=11,
            fontweight="bold",
        )
        self.fig_comp.tight_layout(rect=[0, 0.03, 1, 0.93])
        self.canvas_comp.draw()

    def exportar_csv(self):
        if self.df_resumen_actual.empty:
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="resumen_estadistico_electro1.csv", filetypes=[("CSV", "*.csv")])
        if ruta:
            self.df_resumen_actual.to_csv(ruta, index=False)
            messagebox.showinfo("Exportado", f"Tabla guardada en:\n{ruta}")

    def exportar_png(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".png", initialfile="comparativa_electro1.png", filetypes=[("Imagen PNG", "*.png")])
        if ruta:
            self.fig.savefig(ruta, dpi=150)
            messagebox.showinfo("Exportado", f"Gráfica guardada en:\n{ruta}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionElectro1(root)
    root.mainloop()