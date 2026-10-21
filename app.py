import streamlit as st
import sqlite3
import difflib
import pandas as pd

# Configuración visual de la página
st.set_page_config(page_title="RiskScreen - Compliance", page_icon="🛡️", layout="centered")

def inicializar_bd():
    conn = sqlite3.connect('riskscreen_local.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS listas_restrictivas (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, fuente TEXT, categoria TEXT)')
    c.execute('SELECT COUNT(*) FROM listas_restrictivas')
    if c.fetchone()[0] == 0:
        ejemplos = [
            ('JUAN CARLOS RODRIGUEZ', 'OFAC', 'Riesgo Alto - Sancionado'),
            ('JOSE GREGORIO MARTINEZ', 'ONU', 'Riesgo Alto - Terrorismo'),
            ('MARIA ALEJANDRA PEREZ', 'PEP Venezuela', 'Persona Expuesta Políticamente'),
            ('CARLOS EDUARDO GOMEZ', 'Lista Interna', 'Riesgo Moderado - Fraude Prev')
        ]
        c.executemany('INSERT INTO listas_restrictivas (nombre, fuente, categoria) VALUES (?, ?, ?)', ejemplos)
    conn.commit()
    conn.close()

# Inicializamos la base de datos
inicializar_bd()

st.title("🛡️ Sistema RiskScreen")
st.markdown("### Módulo de Inspección Local y Gestión de Listas")

# Creamos pestañas para organizar la aplicación
pestana1, pestana2 = st.tabs(["🔍 Consulta de Screening", "⚙️ Administrar Base de Datos"])

# --- PESTAÑA 1: SCREENING ---
with pestana1:
    st.write("Ingrese el nombre completo de la persona u organización para realizar el filtro en las listas restrictivas.")
    nombre_buscado = st.text_input("Nombre a consultar:", placeholder="Ej. Juan Carlos...")

    if st.button("Ejecutar Screening", type="primary"):
        if not nombre_buscado.strip():
            st.warning("Por favor, ingrese un nombre válido para realizar la búsqueda.")
        else:
            conn = sqlite3.connect('riskscreen_local.db')
            c = conn.cursor()
            c.execute('SELECT nombre, fuente, categoria FROM listas_restrictivas')
            registros = c.fetchall()
            conn.close()

            nombres_en_bd = [reg[0] for reg in registros]
            coincidencias = difflib.get_close_matches(nombre_buscado.upper(), nombres_en_bd, n=1, cutoff=0.6)

            st.divider()
            st.markdown(f"#### Resultados para: `{nombre_buscado.upper()}`")

            if not coincidencias:
                st.success("🟢 **SEMÁFORO VERDE: RIESGO BAJO / SIN COINCIDENCIAS**\n\nEl nombre no registra alertas en las listas restrictivas. **Aprobado** para continuar con el trámite.")
            else:
                nombre_coincidente = coincidencias[0]
                for reg in registros:
                    if reg[0] == nombre_coincidente:
                        st.error("🔴 **SEMÁFORO ROJO: ALERTA DE COINCIDENCIA CRÍTICA**")
                        st.markdown(f"""
                        - **Nombre Registrado:** {nombre_coincidente}
                        - **Fuente Oficial:** `{reg[1]}`
                        - **Categoría de Riesgo:** `{reg[2]}`
                        """)
                        st.warning("⚠️ **ACCIÓN REQUERIDA:** Bloqueo preventivo de la operación. Enviar expediente al Oficial de Cumplimiento.")

# --- PESTAÑA 2: ADMINISTRAR BASE DE DATOS ---
with pestana2:
    st.subheader("📋 Registros Actuales en la Base de Datos")
    
    # Consultar y mostrar registros en forma de tabla interactiva
    conn = sqlite3.connect('riskscreen_local.db')
    c = conn.cursor()
    c.execute('SELECT id, nombre, fuente, categoria FROM listas_restrictivas')
    registros_bd = c.fetchall()
    conn.close()

    if registros_bd:
        df = pd.DataFrame(registros_bd, columns=["ID", "Nombre", "Fuente", "Categoría"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("La base de datos está vacía.")

    st.divider()
    st.subheader("➕ Agregar Nuevo Registro a las Listas")
    
    with st.form("form_agregar"):
        nuevo_nombre = st.text_input("Nombre completo de la persona/empresa:")
        nueva_fuente = st.text_input("Fuente (ej. OFAC, ONU, Lista Interna):")
        nueva_categoria = st.text_input("Categoría de riesgo:")
        boton_guardar = st.form_submit_button("Guardar en la Base de Datos")

if boton_guardar:
            if nuevo_nombre.strip() and nueva_fuente.strip() and nueva_categoria.strip():
                conn = sqlite3.connect('riskscreen_local.db')
                c = conn.cursor()
                c.execute('INSERT INTO listas_restrictivas (nombre, fuente, categoria) VALUES (?, ?, ?)', 
                          (nuevo_nombre.upper(), nueva_fuente.upper(), nueva_categoria))
                conn.commit()
                conn.close()
                st.success(f"¡El registro de '{nuevo_nombre.upper()}' se ha agregado con éxito!")
                st.rerun()
            else:
                st.error("Por favor, complete todos los campos para poder guardar.")
