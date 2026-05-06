import streamlit as st
import pandas as pd
import plotly.express as px
import tco

# Configuración de página
st.set_page_config(page_title="TCO Autos: Gas vs Híbridos vs Eléctricos", layout="wide", page_icon="🚗")

st.title("Comparador de Costo Total de Propiedad (TCO) 🚗⚡")
st.markdown("""
Analiza y compara el costo real a largo plazo entre vehículos de Combustión (Gasolina), 
Híbridos (HEV), Híbridos Enchufables (PHEV) y Eléctricos (BEV). El cálculo incluye 
amortización del crédito, comisiones y costos de energía mensuales.
""")

# --- SIDEBAR: Parámetros Globales ---
st.sidebar.header("🌍 Parámetros Globales")
km_anual = st.sidebar.number_input("Kilometraje Anual (km)", min_value=1000, max_value=100000, value=15000, step=1000)
precio_gas = st.sidebar.number_input("Precio Gasolina (MXN/L)", min_value=1.0, value=24.0, step=0.5)
precio_kwh = st.sidebar.number_input("Precio Electricidad (MXN/kWh)", min_value=0.1, value=3.5, step=0.1)
meses_proyeccion = st.sidebar.slider("Meses de proyección", min_value=12, max_value=240, value=120, step=12)

# Parámetros financieros por defecto en sidebar
st.sidebar.markdown("---")
st.sidebar.header("💰 Finanzas (Valores por defecto)")
tasa_default = st.sidebar.number_input("Tasa Anual Default (%)", min_value=0.0, max_value=50.0, value=12.0)
plazo_default = st.sidebar.selectbox("Plazo Default (meses)", [12, 24, 36, 48, 60, 72], index=4)
comision_default = st.sidebar.number_input("Comisión Apertura (%)", min_value=0.0, max_value=10.0, value=3.0)

# --- MAIN: Parámetros por Vehículo ---
st.header("Configuración por Vehículo")
cols = st.columns(4)

vehiculos = ["Gasolina (ICE)", "Híbrido (HEV)", "Enchufable (PHEV)", "Eléctrico (BEV)"]
tipos = ["GAS", "HEV", "PHEV", "BEV"]
datos_vehiculos = {}

# Valores por defecto realistas para México 2024-2025
defaults = {
    "GAS": {"precio": 350000, "eng": 70000, "cons_l": 8.5, "cons_kwh": 0.0},
    "HEV": {"precio": 450000, "eng": 90000, "cons_l": 4.5, "cons_kwh": 0.0},
    "PHEV": {"precio": 650000, "eng": 130000, "cons_l": 5.0, "cons_kwh": 18.0},
    "BEV": {"precio": 750000, "eng": 150000, "cons_l": 0.0, "cons_kwh": 16.0}
}

for i, (col, nombre, tipo) in enumerate(zip(cols, vehiculos, tipos)):
    with col:
        st.subheader(nombre)
        marca_modelo = st.text_input("Marca/Modelo", f"Auto {tipo}", key=f"modelo_{tipo}")
        precio = st.number_input("Precio (MXN)", min_value=10000, value=defaults[tipo]["precio"], step=10000, key=f"precio_{tipo}")
        enganche = st.number_input("Enganche (MXN)", min_value=0, value=defaults[tipo]["eng"], step=5000, key=f"eng_{tipo}")
        
        with st.expander("Consumo y Eficiencia", expanded=True):
            cons_l = 0.0
            cons_kwh = 0.0
            pct_ev = 0.0
            
            if tipo in ["GAS", "HEV", "PHEV"]:
                cons_l = st.number_input("Consumo (L/100km)", value=defaults[tipo]["cons_l"], step=0.1, key=f"cl_{tipo}")
            if tipo in ["PHEV", "BEV"]:
                cons_kwh = st.number_input("Consumo (kWh/100km)", value=defaults[tipo]["cons_kwh"], step=0.5, key=f"ckwh_{tipo}")
            if tipo == "PHEV":
                pct_ev = st.slider("% Uso Eléctrico", min_value=0, max_value=100, value=60, help="Porcentaje del kilometraje anual en modo eléctrico.", key=f"pct_{tipo}")

        with st.expander("Crédito (Avanzado)", expanded=False):
            plazo = st.number_input("Plazo (meses)", value=plazo_default, key=f"plazo_{tipo}")
            tasa = st.number_input("Tasa Anual (%)", value=tasa_default, key=f"tasa_{tipo}")
            comision = st.number_input("Comisión Apertura (%)", value=comision_default, key=f"com_{tipo}")

        datos_vehiculos[tipo] = {
            "nombre": marca_modelo,
            "precio": precio,
            "enganche": enganche,
            "plazo": plazo,
            "tasa": tasa,
            "comision": comision,
            "cons_l": cons_l,
            "cons_kwh": cons_kwh,
            "pct_ev": pct_ev
        }

# --- PROCESAMIENTO Y CÁLCULOS ---
resultados = {}
series_tiempo = {}

for tipo, config in datos_vehiculos.items():
    costo_energia_mes = tco.calcular_costo_energia_mensual(
        km_anual=km_anual,
        tipo=tipo,
        precio_gasolina=precio_gas,
        precio_electricidad=precio_kwh,
        consumo_l_100km=config["cons_l"],
        consumo_kwh_100km=config["cons_kwh"],
        pct_km_ev_phev=config["pct_ev"]
    )
    
    proyeccion = tco.proyeccion_costo_acumulado(
        precio=config["precio"],
        enganche=config["enganche"],
        plazo_meses=config["plazo"],
        tasa_anual=config["tasa"],
        comision_apertura_pct=config["comision"],
        costo_energia_mensual=costo_energia_mes,
        meses_proyeccion=meses_proyeccion
    )
    
    resultados[tipo] = proyeccion
    series_tiempo[config["nombre"]] = proyeccion["serie_acumulada"]

# --- RESULTADOS Y VISUALIZACIÓN ---
st.markdown("---")
st.header("📊 Resultados del Análisis")

# 1. Resumen por tarjetas (Metrics)
cols_res = st.columns(4)
for i, (tipo, config) in enumerate(datos_vehiculos.items()):
    res = resultados[tipo]
    with cols_res[i]:
        st.info(f"**{config['nombre']}**")
        st.metric("Mensualidad (Crédito)", f"${res['pago_mensual']:,.2f}")
        st.metric("Total Pagado Auto (Capital+Int)", f"${res['total_pagado_auto']:,.2f}")
        st.metric("Costo Energía Anual", f"${res['costo_energia_anual']:,.2f}")

# 2. Gráfica de Costo Acumulado
st.subheader("Costo Acumulado en el Tiempo (TCO)")
df_series = pd.DataFrame(series_tiempo)
df_series.index.name = "Meses"
df_series.reset_index(inplace=True)

# Convertir de formato ancho a largo para Plotly
df_melted = df_series.melt(id_vars=["Meses"], var_name="Vehículo", value_name="Costo Acumulado (MXN)")

fig = px.line(
    df_melted, 
    x="Meses", 
    y="Costo Acumulado (MXN)", 
    color="Vehículo",
    title="Crecimiento del Costo Total de Propiedad a través de los meses",
    markers=False,
    color_discrete_sequence=px.colors.qualitative.G10
)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# 3. Análisis de Break-Even (Punto de equilibrio)
st.subheader("🎯 Análisis de Recuperación de Inversión (Break-Even vs Gasolina)")
serie_gas_nombre = datos_vehiculos["GAS"]["nombre"]
serie_gas = df_series[serie_gas_nombre].tolist()

for tipo in ["HEV", "PHEV", "BEV"]:
    nombre_comparado = datos_vehiculos[tipo]["nombre"]
    serie_comp = df_series[nombre_comparado].tolist()
    
    mes_break_even = tco.encontrar_break_even(serie_gas, serie_comp)
    
    if mes_break_even == 0:
        st.success(f"✅ El **{nombre_comparado}** es más barato que el de Gasolina desde el **Día 1**.")
    elif mes_break_even > 0:
        anios = mes_break_even // 12
        meses = mes_break_even % 12
        st.success(f"✅ El **{nombre_comparado}** recupera su sobrecosto inicial en el **Mes {mes_break_even}** ({anios} años y {meses} meses).")
    else:
        st.warning(f"⚠️ El **{nombre_comparado}** no logra recuperar la diferencia de costo de adquisición en el periodo de {meses_proyeccion} meses frente al de Gasolina.")

st.caption("Nota: El cálculo asume precios de energía constantes a lo largo del tiempo y no considera gastos de mantenimiento, seguros o depreciación de reventa, los cuales también afectan el TCO real.")
