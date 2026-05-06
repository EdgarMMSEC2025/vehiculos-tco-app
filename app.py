import streamlit as st
import pandas as pd
import plotly.express as px
import tco

# Configuración inicial de la página
st.set_page_config(page_title="TCO y Break-Even Autos", page_icon="🚗", layout="wide")

st.title("🚗 Calculadora TCO y Break-Even de Vehículos")
st.markdown("**Contexto:** Estimaciones y cálculos parametrizados para México (Actualizado a Mayo 2026).")

# --- BARRA LATERAL: PARÁMETROS GENERALES ---
st.sidebar.header("🌍 Parámetros Generales (Mayo 2026)")
km_anuales = st.sidebar.number_input("Kilometraje Anual", min_value=5000, max_value=100000, value=15000, step=1000)
precio_gas = st.sidebar.number_input("Precio Gasolina ($/litro)", min_value=15.0, max_value=40.0, value=25.50, step=0.5)
precio_elec = st.sidebar.number_input("Tarifa Eléctrica CFE ($/kWh)", min_value=1.0, max_value=10.0, value=3.50, step=0.1)
mantenimiento_base = st.sidebar.number_input("Mantenimiento Anual Auto Gasolina ($)", min_value=2000, max_value=50000, value=12000, step=1000)
meses_proyeccion = st.sidebar.slider("Meses a proyectar", 12, 120, 72)

# --- COLUMNAS PARA VEHÍCULOS ---
col1, col2 = st.columns(2)

# Columna 1: Vehículo de Combustión (Referencia)
with col1:
    st.header("⛽ Auto de Gasolina (Referencia)")
    precio_gasolina = st.number_input("Precio del Auto ($)", value=450000, step=10000, key="p_gas")
    enganche_gasolina = st.slider("Enganche (%)", 10, 80, 20, key="eng_gas")
    plazo_gasolina = st.selectbox("Plazo de Crédito (meses)", [12, 24, 36, 48, 60, 72], index=4, key="plazo_gas")
    tasa_gasolina = st.number_input("Tasa de Interés Anual (%)", value=14.5, step=0.5, key="tasa_gas")
    rend_gasolina = st.number_input("Rendimiento (km/l)", value=12.0, step=0.5, key="rend_gas")

# Columna 2: Vehículo Alternativo (HEV, PHEV, BEV)
with col2:
    st.header("⚡ Auto Limpio/Eficiente")
    tipo_alt = st.selectbox("Tecnología", ["HEV (Híbrido)", "PHEV (Híbrido Enchufable)", "BEV (Eléctrico 100%)"])
    tipo_clave = tipo_alt.split(" ")[0] # Extrae HEV, PHEV o BEV
    
    precio_alt = st.number_input("Precio del Auto ($)", value=600000, step=10000, key="p_alt")
    enganche_alt = st.slider("Enganche (%)", 10, 80, 20, key="eng_alt")
    plazo_alt = st.selectbox("Plazo de Crédito (meses)", [12, 24, 36, 48, 60, 72], index=4, key="plazo_alt")
    tasa_alt = st.number_input("Tasa de Interés Anual (%)", value=12.0, step=0.5, key="tasa_alt")
    
    rend_gas_alt, rend_elec_alt, pct_elec = 0.0, 0.0, 0
    
    if tipo_clave in ['HEV', 'PHEV']:
        rend_gas_alt = st.number_input("Rendimiento Gasolina (km/l)", value=22.0, step=0.5, key="rend_gas_alt")
    if tipo_clave in ['PHEV', 'BEV']:
        rend_elec_alt = st.number_input("Rendimiento Eléctrico (km/kWh)", value=6.0, step=0.5, key="rend_elec_alt")
    if tipo_clave == 'PHEV':
        pct_elec = st.slider("% de uso en modo 100% eléctrico", 0, 100, 60)

# --- CÁLCULOS ---
# 1. Financiamiento
mensualidad_gas, monto_eng_gas = tco.calcular_mensualidad(precio_gasolina, enganche_gasolina, tasa_gasolina, plazo_gasolina)
mensualidad_alt, monto_eng_alt = tco.calcular_mensualidad(precio_alt, enganche_alt, tasa_alt, plazo_alt)

# 2. Operativos
energia_gas, mant_gas, tenencia_gas = tco.calcular_costos_operativos(
    'Gasolina', precio_gasolina, km_anuales, rend_gasolina, 0, precio_gas, 0, mantenimiento_base
)
energia_alt, mant_alt, tenencia_alt = tco.calcular_costos_operativos(
    tipo_clave, precio_alt, km_anuales, rend_gas_alt, rend_elec_alt, precio_gas, precio_elec, mantenimiento_base, pct_elec
)

# 3. Proyecciones
acumulado_gas = tco.proyectar_costos_acumulados(meses_proyeccion, monto_eng_gas, mensualidad_gas, energia_gas, mant_gas, tenencia_gas, plazo_gasolina)
acumulado_alt = tco.proyectar_costos_acumulados(meses_proyeccion, monto_eng_alt, mensualidad_alt, energia_alt, mant_alt, tenencia_alt, plazo_alt)

# --- RESULTADOS Y BREAK-EVEN ---
st.divider()
st.subheader("📊 Análisis de Costos Mensuales")

datos_mensuales = {
    "Concepto": ["Mensualidad Crédito", "Gasto Energía/Gasolina", "Mantenimiento Prorrateado", "Tenencia Prorrateada", "TOTAL MENSUAL"],
    "Auto Gasolina ($)": [mensualidad_gas, energia_gas, mant_gas, tenencia_gas, mensualidad_gas + energia_gas + mant_gas + tenencia_gas],
    f"Auto {tipo_clave} ($)": [mensualidad_alt, energia_alt, mant_alt, tenencia_alt, mensualidad_alt + energia_alt + mant_alt + tenencia_alt]
}
df_mensual = pd.DataFrame(datos_mensuales)
st.dataframe(df_mensual.style.format({df_mensual.columns[1]: "{:,.2f}", df_mensual.columns[2]: "{:,.2f}"}), use_container_width=True)

# Cálculo del Break-Even
mes_breakeven = None
for mes in range(meses_proyeccion):
    if acumulado_alt[mes] < acumulado_gas[mes]:
        mes_breakeven = mes + 1
        break

st.subheader("🎯 Análisis de Break-Even (Punto de Equilibrio)")
if mes_breakeven:
    st.success(f"¡El sobrecosto inicial de la tecnología {tipo_clave} se recupera en el **Mes {mes_breakeven}**!")
    st.write("A partir de este mes, los ahorros en gasolina, mantenimiento y tenencia superan la inversión extra del vehículo.")
else:
    st.warning(f"Con estos parámetros, la inversión no se recupera dentro de los {meses_proyeccion} meses proyectados.")

# Gráfica
df_grafica = pd.DataFrame({
    "Mes": range(1, meses_proyeccion + 1),
    "Gasolina": acumulado_gas,
    tipo_clave: acumulado_alt
})

fig = px.line(df_grafica, x="Mes", y=["Gasolina", tipo_clave], 
              title="Costo Total de Propiedad Acumulado (TCO)",
              labels={"value": "Costo Acumulado ($)", "variable": "Tecnología"})

if mes_breakeven:
    fig.add_vline(x=mes_breakeven, line_dash="dash", line_color="green", annotation_text=f"Break-Even: Mes {mes_breakeven}")

st.plotly_chart(fig, use_container_width=True)
