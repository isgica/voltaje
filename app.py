import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# 1. Page Configuration
st.set_page_config(page_title="Dashboard Calidad de Energía", layout="wide")

# 2. FILE UPLOADER IN THE SIDEBAR
st.sidebar.header("📁 Cargar Datos")
uploaded_file = st.sidebar.file_uploader(
    "Carga tu archivo de registro (Excel o CSV)", 
    type=["csv", "xlsx", "xls"]
)

# 3. MODIFIED DATA LOADING FUNCTION
@st.cache_data
def load_uploaded_data(file_wrapper):
    try:
        # Check the file extension to use the correct pandas reader
        if file_wrapper.name.endswith('.csv'):
            # You might need to tweak 'sep' (e.g., sep=';') depending on your CSV format
            data = pd.read_csv(file_wrapper)
        else:
            data = pd.read_excel(file_wrapper)

        if 'Fecha' in data.columns and 'Hora' in data.columns:
            # 1. Combinar en una cadena de texto limpia
            fecha_hora_str = data['Fecha'].astype(str) + ' ' + data['Hora'].astype(str)
            
            # 2. LIMPIEZA: Eliminar la palabra 'ms' y cualquier número pegado a ella al final (ej: "0ms")
            # Usamos una expresión regular para quitar " [número]ms" al final de la cadena
            fecha_hora_str = fecha_hora_str.str.replace(r'\s+\d+ms$', '', regex=True)
            
            # 3. Convertir ahora sí a Datetime de forma segura
            data['FechaHora'] = pd.to_datetime(fecha_hora_str, errors='coerce')
            
            # Opcional: Avisar si hubo filas imposibles de parsear
            if data['FechaHora'].isna().any():
                st.sidebar.warning("⚠️ Algunas filas no pudieron convertirse a fecha y se omitieron.")
            
        return data
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo: {e}")
        return None

# --- Main App Logic ---
if uploaded_file is not None:
    # Load user data
    df = load_uploaded_data(uploaded_file)
    
    if df is not None:
        # Calculate the Transformer Nominal Current safely
        I_NOM_TRAFO = 1000 * 1000 / (480 * np.sqrt(3))

        st.title("⚡ Análisis de Calidad de Energía")
        tab1, tab2 = st.tabs(["🖨️ Reporte para Impresión (Matplotlib)", "📊 Cuadro de Mando Interactivo"])


        # --- TAB 1: MATPLOTLIB STATIC & PRINT VERSION ---
        with tab1:
            st.subheader("Vista Previa del Reporte Estático")
            
            fig, axes = plt.subplots(4, 2, figsize=(18, 24))
            fig.suptitle('ANÁLISIS COMPLETO - TRANSFORMADOR 1000 kVA | CLÍNICA PRIVADA\nFluke 1735', 
                         fontsize=16, fontweight='bold', y=0.995)

            # 1. TENSIONES EN EL TIEMPO
            ax1 = axes[0, 0]
            ax1.plot(df['FechaHora'], df['Tensión L1 Med'], label='L1', color='red', alpha=0.7, linewidth=0.8)
            ax1.plot(df['FechaHora'], df['Tensión L2 Med'], label='L2', color='green', alpha=0.7, linewidth=0.8)
            ax1.plot(df['FechaHora'], df['Tensión L3 Med'], label='L3', color='blue', alpha=0.7, linewidth=0.8)
            ax1.axhline(y=277, color='black', linestyle='--', linewidth=1, label='Nominal 277V')
            ax1.set_title('TENSIONES FASE-NEUTRO (277V nominal)', fontweight='bold')
            ax1.set_ylabel('Voltaje (V)')
            ax1.legend(loc='upper right', fontsize=8)
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(240, 310)

            # 2. CORRIENTES EN EL TIEMPO
            ax2 = axes[0, 1]
            ax2.plot(df['FechaHora'], df['Corriente L1 Med'], label='L1', color='red', alpha=0.7, linewidth=0.8)
            ax2.plot(df['FechaHora'], df['Corriente L2 Med'], label='L2', color='green', alpha=0.7, linewidth=0.8)
            ax2.plot(df['FechaHora'], df['Corriente L3 Med'], label='L3', color='blue', alpha=0.7, linewidth=0.8)
            ax2.plot(df['FechaHora'], df['Corriente N Med'], label='Neutro', color='purple', alpha=0.7, linewidth=0.8)
            ax2.axhline(y=I_NOM_TRAFO, color='black', linestyle='--', linewidth=1, label=f'I nominal trafo: {I_NOM_TRAFO:.0f}A')
            ax2.set_title('CORRIENTES POR FASE', fontweight='bold')
            ax2.set_ylabel('Corriente (A)')
            ax2.legend(loc='upper right', fontsize=8)
            ax2.grid(True, alpha=0.3)

            # 3. THD-V
            ax3 = axes[1, 0]
            ax3.plot(df['FechaHora'], df['THD V L1 Med'], label='L1', color='red', alpha=0.7, linewidth=0.8)
            ax3.plot(df['FechaHora'], df['THD V L2 Med'], label='L2', color='green', alpha=0.7, linewidth=0.8)
            ax3.plot(df['FechaHora'], df['THD V L3 Med'], label='L3', color='blue', alpha=0.7, linewidth=0.8)
            ax3.axhline(y=5, color='orange', linestyle='--', linewidth=2, label='Límite IEEE 519 (5%)')
            ax3.set_title('THD DE TENSIÓN (%)', fontweight='bold')
            ax3.set_ylabel('THD-V (%)')
            ax3.legend(loc='upper right', fontsize=8)
            ax3.grid(True, alpha=0.3)
            ax3.set_ylim(0, 20)

            # 4. THD-I
            ax4 = axes[1, 1]
            ax4.plot(df['FechaHora'], df['THD A L1 Med'], label='L1', color='red', alpha=0.7, linewidth=0.8)
            ax4.plot(df['FechaHora'], df['THD A L2 Med'], label='L2', color='green', alpha=0.7, linewidth=0.8)
            ax4.plot(df['FechaHora'], df['THD A L3 Med'], label='L3', color='blue', alpha=0.7, linewidth=0.8)
            ax4.plot(df['FechaHora'], df['THD A N Med'], label='Neutro', color='purple', alpha=0.7, linewidth=0.8)
            ax4.set_title('THD DE CORRIENTE (%)', fontweight='bold')
            ax4.set_ylabel('THD-I (%)')
            ax4.legend(loc='upper right', fontsize=8)
            ax4.grid(True, alpha=0.3)
            ax4.set_ylim(0, 50)

#            # 5. CARGA DEL TRANSFORMADOR
#            ax5 = axes[2, 0]
#            ax5.plot(df['FechaHora'], df['Carga_%'], color='darkblue', linewidth=0.8)
#            ax5.set_title('CARGA DEL TRANSFORMADOR (%)', fontweight='bold')
#            ax5.set_ylabel('Carga (%)')
#            ax5.grid(True, alpha=0.3)

            # 6. FACTOR DE POTENCIA
            ax6 = axes[2, 1]
            ax6.plot(df['FechaHora'], df['Factor de Potencia Total Med'], color='darkgreen', linewidth=0.8)
            ax6.set_title('FACTOR DE POTENCIA TOTAL', fontweight='bold')
            ax6.set_ylabel('FP')
            ax6.grid(True, alpha=0.3)
            ax6.set_ylim(0.7, 1.0)

#            # 7. DESBALANCE DE TENSIÓN
#            ax7 = axes[3, 0]
#            ax7.plot(df['FechaHora'], df['Desbalance_V_%'], color='darkred', linewidth=0.8)
#            ax7.set_title('DESBALANCE DE TENSIÓN (%)', fontweight='bold')
#            ax7.set_ylabel('Desbalance (%)')
#            ax7.grid(True, alpha=0.3)

            # 8. POTENCIA DISTORSIÓN
            ax8 = axes[3, 1]
            ax8.plot(df['FechaHora'], df['Potencia de distorsión Total Med']/1000, color='purple', linewidth=0.8)
            ax8.set_title('POTENCIA DE DISTORSIÓN (kW)', fontweight='bold')
            ax8.set_ylabel('Potencia distorsión (kW)')
            ax8.grid(True, alpha=0.3)

            for ax in axes.flat:
                plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

            plt.tight_layout()
            st.pyplot(fig)
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            st.download_button(
                label="📥 Descargar Imagen para Imprimir (PNG)",
                data=img_buffer,
                file_name="analisis_calidad_energia_reporte.png",
                mime="image/png"
            )

        # --- TAB 2: INTERACTIVE STREAMLIT CHARTS ---
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("1. Tensiones Fase-Neutro (277V Nominal)")
                st.line_chart(df, x='FechaHora', y=['Tensión L1 Med', 'Tensión L2 Med', 'Tensión L3 Med'], color=["#FF4B4B", "#00F4B4", "#004BFF"])
            with col2:
                st.subheader("2. Corrientes por Fase y Neutro")
                st.line_chart(df, x='FechaHora', y=['Corriente L1 Med', 'Corriente L2 Med', 'Corriente L3 Med', 'Corriente N Med'], color=["#FF4B4B", "#00F4B4", "#004BFF", "#A020F0"])
            
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("3. THD de Tensión (%)")
                st.line_chart(df, x='FechaHora', y=['THD V L1 Med', 'THD V L2 Med', 'THD V L3 Med'], color=["#FF4B4B", "#00F4B4", "#004BFF"])
            with col4:
                st.subheader("4. THD de Corriente (%)")
                st.line_chart(df, x='FechaHora', y=['THD A L1 Med', 'THD A L2 Med', 'THD A L3 Med', 'THD A N Med'], color=["#FF4B4B", "#00F4B4", "#004BFF", "#A020F0"])

            col5, col6 = st.columns(2)
#            with col5:
#                st.subheader("5. Carga del Transformador (%)")
#                st.line_chart(df, x='FechaHora', y='Carga_%', color="#00008B")
            with col6:
                st.subheader("6. Factor de Potencia Total")
                st.line_chart(df, x='FechaHora', y='Factor de Potencia Total Med', color="#006400")

            col7, col8 = st.columns(2)
#            with col7:
#                st.subheader("7. Desbalance de Tensión (%)")
#                st.line_chart(df, x='FechaHora', y='Desbalance_V_%', color="#8B0000")
            with col8:
                # Add safely inside layout processing
                if 'Potencia de distorsión Total Med' in df.columns:
                    df['Potencia_Distorsion_kW'] = df['Potencia de distorsión Total Med'] / 1000
                    st.subheader("8. Potencia de Distorsión (kW)")
                    st.line_chart(df, x='FechaHora', y='Potencia_Distorsion_kW', color="#800080")
else:
    # Fallback view shown before a user uploads anything
    st.title("⚡ Análisis de Calidad de Energía")
    st.warning("👈 Por favor, carga un archivo Excel (.xlsx/.xls) o CSV en el menú lateral para comenzar a procesar el gráfico.")
