import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(
    page_title="Dashboard Calidad de Energía", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- MOCK DATA GENERATION (Replace with your actual 'df' loading logic) ---
@st.cache_data
def load_data():
    dates = pd.date_range(start="2026-05-06", end="2026-05-14", freq="15min")
    n = len(dates)
    
    # Mathematical setup for constants
    v_nom = 277
    i_nom_trafo = 1000 * 1000 / (480 * np.sqrt(3))  # ~1204A
    
    data = {
        'FechaHora': dates,
        'Tensión L1 Med': np.random.normal(v_nom, 2, n),
        'Tensión L2 Med': np.random.normal(v_nom, 1.5, n),
        'Tensión L3 Med': np.random.normal(v_nom, 2.5, n),
        'Corriente L1 Med': np.random.uniform(400, 850, n),
        'Corriente L2 Med': np.random.uniform(420, 830, n),
        'Corriente L3 Med': np.random.uniform(410, 870, n),
        'Corriente N Med': np.random.uniform(15, 60, n),
        'THD V L1 Med': np.random.uniform(1, 4.5, n),
        'THD V L2 Med': np.random.uniform(1.2, 4.2, n),
        'THD V L3 Med': np.random.uniform(1.1, 5.5, n),
        'THD A L1 Med': np.random.uniform(12, 22, n),
        'THD A L2 Med': np.random.uniform(14, 24, n),
        'THD A L3 Med': np.random.uniform(13, 26, n),
        'THD A N Med': np.random.uniform(20, 38, n),
        'Carga_%': np.random.uniform(35, 75, n),
        'Factor de Potencia Total Med': np.random.uniform(0.84, 0.96, n),
        'Desbalance_V_%': np.random.uniform(0.4, 2.8, n),
        'Potencia de distorsión Total Med': np.random.uniform(4000, 18000, n)
    }
    return pd.DataFrame(data), i_nom_trafo

df, I_NOM_TRAFO = load_data()
# --------------------------------------------------------------------------

# 2. Header Information
st.title("⚡ ANÁLISIS COMPLETO - TRANSFORMADOR 1000 kVA")
st.caption("🏥 CLÍNICA PRIVADA | Fluke 1735 | Rejistro de 7.7 días (06-14 Mayo 2026)")
st.markdown("---")

# 3. Native Grid Layout (2 columns layout replacing your 4x2 subplot grid)

# --- ROW 1 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Tensiones Fase-Neutro (277V Nominal)")
    st.line_chart(
        df, 
        x='FechaHora', 
        y=['Tensión L1 Med', 'Tensión L2 Med', 'Tensión L3 Med'], 
        color=["#FF4B4B", "#00F4B4", "#004BFF"] # Red, Green, Blue
    )
    st.info("💡 Límites de tolerancia de tensión de diseño: -10% (249V) a +10% (305V)")

with col2:
    st.subheader("2. Corrientes por Fase y Neutro")
    st.line_chart(
        df, 
        x='FechaHora', 
        y=['Corriente L1 Med', 'Corriente L2 Med', 'Corriente L3 Med', 'Corriente N Med'],
        color=["#FF4B4B", "#00F4B4", "#004BFF", "#A020F0"] # Red, Green, Blue, Purple
    )
    st.caption(f"Límite de Corriente Nominal del Transformador: **{I_NOM_TRAFO:.0f} A** por fase.")

st.markdown("---")

# --- ROW 2 ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("3. THD de Tensión (%)")
    st.line_chart(
        df, 
        x='FechaHora', 
        y=['THD V L1 Med', 'THD V L2 Med', 'THD V L3 Med'],
        color=["#FF4B4B", "#00F4B4", "#004BFF"]
    )
    st.warning("⚠️ Límite recomendado por IEEE 519 es de **5%** para THD-V.")

with col4:
    st.subheader("4. THD de Corriente (%)")
    st.line_chart(
        df, 
        x='FechaHora', 
        y=['THD A L1 Med', 'THD A L2 Med', 'THD A L3 Med', 'THD A N Med'],
        color=["#FF4B4B", "#00F4B4", "#004BFF", "#A020F0"]
    )
    st.warning("⚠️ Límite objetivo IEEE: **20%** | Nivel crítico: **35%**")

st.markdown("---")

# --- ROW 3 ---
col5, col6 = st.columns(2)

with col5:
    st.subheader("5. Carga del Transformador (%)")
    st.line_chart(df, x='FechaHora', y='Carga_%', color="#00008B")
    st.caption("Límite recomendado de operación segura continua: **80%**")

with col6:
    st.subheader("6. Factor de Potencia Total")
    st.line_chart(df, x='FechaHora', y='Factor de Potencia Total Med', color="#006400")
    st.caption("Objetivo de eficiencia energética: **0.95** | Mínimo normativo regulatorio: **0.85**")

st.markdown("---")

# --- ROW 4 ---
col7, col8 = st.columns(2)

with col7:
    st.subheader("7. Desbalance de Tensión (%)")
    st.line_chart(df, x='FechaHora', y='Desbalance_V_%', color="#8B0000")
    st.caption("Límite estipulado por IEEE: **3%**")

with col8:
    # Convert W to kW inside the UI loop cleanly
    df['Potencia_Distorsion_kW'] = df['Potencia de distorsión Total Med'] / 1000
    st.subheader("8. Potencia de Distorsión (kW)")
    st.line_chart(df, x='FechaHora', y='Potencia_Distorsion_kW', color="#800080")
    st.caption("Representación neta de las pérdidas eléctricas debidas a la distorsión armónica.")
