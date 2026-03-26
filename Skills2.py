import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. IDENTIFICACIÓN Y SEGURIDAD
sheet_id = "1d6wWm4k2nFK48OSa8P9-LZ_SnrE6TrzR4eYQtKqpiYo"

# Test
# DICCIONARIO DE LLAVES (Usted define quién ve qué)
# La 'llave' es lo que el estudiante escribe, la 'pestaña' es el nombre real en el Excel
llaves_acceso = {
    "Clau2026": "Trillizas",
    "NourandGimeno2026": "TAF",
    "Valentin2026": "Mecanica_Fluidos",
    "Simon2026": "Matematicas_II",
    "Saiyajines2026": "Gym_Training"

}
# Configuración de página de rigor
st.set_page_config(page_title="Sistema de Mentoría - Alexander Barraza", layout="wide")

# 2. INTERFAZ DE VALIDACIÓN
st.sidebar.title("🔐 Validación de Mentoría")
password = st.sidebar.text_input("Ingrese su código de acceso:", type="password")

if password in llaves_acceso:
    st.toast("Reporte actualizado correctamente", icon="✅")
    pestaña_autorizada = llaves_acceso[password]
    # Esta ruta es infalible si el archivo es público
    url_export = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    try:
        # 1. CARGA DE DATOS PROTEGIDA
        xls = pd.ExcelFile(url_export)
        # Solo extraemos la pestaña que le compete a esa clave
        df = pd.read_excel(xls, sheet_name=pestaña_autorizada)
        df = df.dropna(how='all', axis=1)

        st.title(f"📈 Reporte: {pestaña_autorizada.replace('_', ' ')}")

        # 2. SELECCIÓN DINÁMICA DE ESTUDIANTE
        columnas_estudiantes = [col for col in df.columns if col not in ['Categoria','ME']]
        estudiante = st.selectbox("Seleccione el Perfil para visualizar:", columnas_estudiantes)

        # 3. GENERACIÓN DE LA GRÁFICA (Su lógica de Matplotlib)
        categorias = df['Categoria'].tolist()
        valores = df[estudiante].tolist()
        values_me = df['ME'].tolist()
    
       # 4. Cerrar el polígono
        valores += valores[:1]
        values_me += values_me[:1]
        angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
        angulos += angulos[:1]
        
        # 5. GENERACIÓN VISUAL (Gráfica de Rigor)
        col1, col2 ,col3 = st.columns([2, 1.1 , 0.9])
        # ... (código previo de ángulos y valores)
        
        with col1:
         with st.spinner('Calculando métricas de rendimiento...'):
            # Aquí va todo su código de: 
            # fig, ax = plt.subplots...
            # col1.pyplot(fig)
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            # Definir los radios para las zonas (asumiendo escala de 0 a 5)
            # Zona Roja (0-2), Amarilla (2-4), Verde (4-5), 
            ax.bar(0, 2, width=2*np.pi, color='red', alpha=0.2, zorder=0)
            ax.bar(0, 4, width=2*np.pi, color='yellow', alpha=0.2, zorder=0, bottom=2)
            ax.bar(0, 5, width=2*np.pi, color='green', alpha=0.2, zorder=0, bottom=4)
            # 1. Dibujar el fondo de comparación (Opcional: un círculo gris al 100%)
            # ax.fill(angulos, [5]*len(angulos), color='gray', alpha=0.1) 

           # 2. Dibujar el polígono del estudiante
            ax.plot(angulos, values_me, color='#ff4500', linewidth=3, label='Meta Esperada (ME)', linestyle='--')
            ax.plot(angulos, valores, color='#0047AB', linewidth=4, label=f'Progreso Actual: {estudiante}')
            ax.fill(angulos, valores, color='#0047AB', alpha=0.2, zorder=2)

            # 3. FIJAR LA ESCALA (Esto evita que el dibujo parezca "máximo" siempre)
            # Si su nota máxima es 5, deje 5. Si es 10, cambie a 10.
            # Esto dibuja los círculos internos en 1, 2, 3, 4 y 5
            ax.set_ylim(0, 5) 
            ax.set_yticks([1, 2, 3, 4, 5]) 
            # MOSTRAR MARCAS DE PORCENTAJE / ESCALA
            # Esto le pone el número a cada círculo para que sea legible
            ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], color="gray", size=8)

            # 4. Estética de los ejes
            ax.set_xticks(angulos[:-1])
            ax.set_xticklabels(categorias, fontsize=9, fontweight='bold')
    
            # Color de la malla para que no distraiga
            ax.grid(True, linestyle='--', alpha=0.6)
            # 5. ACTIVACIÓN DE LEYENDAS (Lo que faltaba)
            # Ubicamos la leyenda fuera del gráfico para no obstruir la vista
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

            st.pyplot(fig)
    
    

        with col2:
            st.write(f"### Detalle de Competencias: {estudiante}")
            
            # 6. TABLA COLOREADA (Pandas Styling)
            df_tabla = df[['Categoria', estudiante]].set_index('Categoria')
            
            def semaforo_celda(val):
                if not isinstance(val, (int, float)): return ''
                if val >= 4.0: color = '#d4edda' # Verde
                elif val >= 3.0: color = '#fff3cd' # Amarillo
                else: color = '#f8d7da' # Rojo
                return f'background-color: {color}'

            st.dataframe(df_tabla.style.applymap(semaforo_celda), use_container_width=True)

# LÓGICA DE STICKERS MOTIVACIONALES
# CÁLCULO DE PROMEDIO PARA RECOMPENSA
      

        with col3: # Lo ponemos en la columna de la tabla para que no estorbe al radar
            st.write("---") # Una línea divisoria profesional
            promedio = np.mean(valores)
         # --- LÓGICA DE SEGMENTACIÓN ---
            # Definimos quiénes pertenecen a qué grupo
            colegio = ["Gaby", "Isa", "Dani"]
            universidad = ["Nour", "Gimeno", "Valentin", "Simon"]
            entrenamiento = ["Alejandro", "Zahir", "Farid"] # Ajuste según sus nombres en el Excel
            
            # URL Base de su GitHub
            base_url = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/"
           
            # 1. DEFINICIÓN DE VARIABLES VISUALES
            # Ajustamos el tamaño a 200px para que se vea imponente
            estilo_base = "width: 200px; height: auto; display: block; margin: auto; padding: 20px; border-radius: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);"
# Selección de imagen por Categoría y Desempeño
            if estudiante in colegio:

                if promedio >= 4.0:
                    # EXCELENCIA: Fondo Verde, Sticker 3aa
                    color_bg = "#12d43f" # Verde intenso 
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MascotaGabiA.png"

                    #st.markdown("<h1 style='text-align: center;'>☀️</h1>", unsafe_allow_html=True)
                    st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.success("🎉 ¡Nivel Leyenda Alcanzado! ¡Continúa así!")
                    st.toast("¡Sigue así! ¡Vas muy bien!", icon="☀️")
                    st.balloons() # Efecto de celebración para el máximo puntaje
                
                elif promedio >= 3.1:
                    # PROGRESO: Fondo Amarillo, Sticker 3bb
                    color_bg = "#e9c656" # Amarillo dorado
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MascotaGabiB.png"
                
                    st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.info("👍 Buen progreso. Hay que ajustar detalles...")
                    st.toast("¡Vas por muy buen camino!", icon="⭐")
               
                else:
                    # DESAFÍO: Fondo Rojo, Sticker 3cc
                    color_bg = "#015acf" # Azul oscuro suave
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MascotaGabiC.png"

                    #st.markdown("<h1 style='text-align: center;'>🌧️</h1>", unsafe_allow_html=True)
                    st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.warning("¡Es momento de apretar tuercas! ⚙️⚙️")
                    st.toast("¡A ponernos las pilas!", icon="🔋")
                    st.snow() # <--- Efecto de nieve cayendo
            
            elif estudiante in universidad:

                # Aquí debe subir imágenes más sobrias (ej: un logo de átomo, un búho o un sello)
                if promedio >= 4.2: 
                    color_bg = "#cf8c0e" # Dorado intenso
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/TrofeoA.png"
                    
                    st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.success("Bien hecho 🎓📚")
                    st.toast("¡Vamos bien!", icon="🏆")
             
                elif promedio >= 3.5:
                    color_bg = "#97c5fa" # Azul cielo claro
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/TrofeoB.png"
                    
                    st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.info("Buen progreso. ¡Hay que ajustar detalles...! 📜🖋️")
                    st.toast(" Vamos mejorando", icon="👍")

                else:
                    
                    color_bg = "#e8f4f8" # Azul académico sobrio
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/TrofeoC.png"
                    
                    st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.warning("Hay que acelerar... 🔍📚")
                    st.toast("¡A ponernos las pilas!", icon="🔋")

            elif estudiante in entrenamiento:

                # Imágenes de calistenia/gimnasia (ej: una barra o una silueta de parada de manos)
                if promedio >= 4.2:
                    color_bg = "#cf5015" # Naranja intenso
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Gym_BaseA1.png"
                    
                    st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.success("Excelente ... 🤸‍♂️🥋")
                    st.toast("¡Bien hecho!", icon="🥇")
                    
                elif promedio >= 3.5: 
                    color_bg = "#aee646" # Verde lima
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Gym_BaseB1.png"
                    
                    st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.info("Vamos mejorando... 💪🧱")
                    st.toast("Buen progreso. ¡Hay que ajustar detalles...!",icon="🥈")

                else: 
                    
                    color_bg = "#7de4b4" # Verde Biche
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Gym_BaseC1.png"
                    
                    st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.warning("Ya vamos dando... 🧘‍♀️⏳")
                    st.toast("Medallita",icon="🥉")

            else:
                color_bg = "#ffffff"
                url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MagusOne.png"
                st.markdown(f'<div style="background-color: {color_bg}; {estilo_base}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                st.info("Reporte de Actividad")
            

    except Exception as e:
        st.error(f"Falla técnica en la lectura de la pestaña '{pestaña_autorizada}': {e}")
        st.info("Verifique que el formato del Excel mantenga la columna 'Categoria'.")

else:
    if password:
        st.sidebar.error("Credencial inválida.")
    st.info("Sistema de Gestión de Mentoría. Ingrese su clave para acceder a sus reportes de avance.")