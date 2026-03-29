import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from datetime import datetime

# Conversor colores 
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Generación de PDF con su lógica original
def generar_reporte_maestro(nombre_estudiante, tipo_cliente, df_notas, df_glosario):
    # 1. INICIALIZACIÓN
    pdf = FPDF()
    pdf.add_page()
    
    # Configuración de colores según su tabla
    config_estetica = {
        "Colegio": {"bg": "#1a4d2e", "tit": "#d4af37", "tab": "#228b22", "font": "Arial"},
        "Entrenamiento": {"bg": "#2d1b4e", "tit": "#f1c40f", "tab": "#6c5ce7", "font": "Courier"},
        "Universidad": {"bg": "#0a192f", "tit": "#64ffda", "tab": "#172a45", "font": "Helvetica"}
    }
    estilo = config_estetica.get(tipo_cliente, config_estetica["Colegio"])
    rgb_bg, rgb_tit, rgb_tab = hex_to_rgb(estilo["bg"]), hex_to_rgb(estilo["tit"]), hex_to_rgb(estilo["tab"])

    # 2. LÓGICA DE MES AUTOMÁTICO
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_actual = meses[datetime.now().month - 1]
    año_actual = datetime.now().year

    # 3. DIBUJO DE FONDO Y ENCABEZADO
    pdf.set_fill_color(*rgb_bg)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Título Principal
    pdf.set_font(estilo["font"], 'B', 20)
    pdf.set_text_color(*rgb_tit)
    pdf.cell(0, 20, f'INFORME DE RENDIMIENTO - {mes_actual.upper()} {año_actual}', 0, 1, 'C')
    
    # Nombre del Estudiante
    pdf.set_font(estilo["font"], 'B', 16)
    pdf.cell(0, 10, f'Estudiante: {nombre_estudiante.upper()}', 0, 1, 'C')
    pdf.ln(10)

    # 4. CUERPO DEL INFORME (Bucle Limpio)
    for index, row in df_notas.iterrows():
        # Tomamos los datos DIRECTO del DataFrame para evitar errores de variables previas
        materia = str(row['Categoria']).upper()
        nota_valor = int(row[nombre_estudiante])
        
        # Búsqueda en Glosario
        filtro = df_glosario[(df_glosario['Categoría'] == row['Categoria']) & 
                             (df_glosario['Tipo_Cliente'] == tipo_cliente) & 
                             (df_glosario['Nivel'] == nota_valor)]
        
        estado = filtro['Estatus'].values[0] if not filtro.empty else "N/A"
        logro = filtro['Descripción_Logro'].values[0] if not filtro.empty else "Evaluación técnica en proceso."

        # Celda de Título de Competencia (SIN FECHAS, SIN S/F)
        pdf.set_font(estilo["font"], 'B', 11)
        pdf.set_fill_color(*rgb_tab)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, f" {materia} - NIVEL {nota_valor} [{estado}]", 1, 1, 'L', True)
        
        # Descripción del Logro
        pdf.set_font(estilo["font"], '', 10)
        pdf.set_text_color(245, 245, 220)
        pdf.multi_cell(0, 5, logro, 0, 'L')
        pdf.ln(3)

        pdf.multi_cell(0, 5, logro, 0, 'L')
        pdf.ln(3)

    # --- NUEVO BLOQUE DE FIRMA Y CONTACTO ---
    pdf.set_y(-40) # Se ubica a 40mm del final de la página
    pdf.set_draw_color(*rgb_tit) 
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Línea divisoria
    pdf.ln(4)

    # A. IMAGEN DEL MAGUITO (Pequeña)
    url_mago = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MagusOne.png"
    try:
        pdf.image(url_mago, x=10, y=pdf.get_y(), w=15) # w=15 la hace bien pequeña
    except:
        pass

    # B. DATOS DEL MENTOR
    pdf.set_x(30) # Espacio para que no se encime con el mago
    pdf.set_font(estilo["font"], 'B', 10)
    pdf.set_text_color(*rgb_tit)
    pdf.cell(0, 5, "ALEXANDER BARRAZA", 0, 1, 'L')
    
    pdf.set_x(30)
    pdf.set_font(estilo["font"], '', 8)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 4, "Físico Profesional | Mentoría Internacional", 0, 1, 'L')
    
    pdf.set_x(30)
    pdf.set_text_color(173, 216, 230) # Azul claro sutil
    pdf.cell(0, 4, "Contacto WhatsApp: +57 3164880199", 0, 1, 'L') 

    # 5. SALIDA DE DATOS (CRÍTICO PARA QUE NO SALGA EN BLANCO)
    # Generamos los bytes y forzamos la codificación correcta para Streamlit
    try:
        output_pdf = pdf.output(dest='S')
        if isinstance(output_pdf, str):
            return output_pdf.encode('latin-1', errors='replace')
        return output_pdf
    except:
        return b"Error en la generacion de bytes del PDF"

# CSS Personalizado:
# 1. Usamos la imagen como un 'border-image' sutil.
# 2. Creamos una sombra dorada para dar profundidad.
#st.markdown("""<style>/* 1. Fondo limpio y profesional */.stApp { background-color: #f8f9fa; }/* 2. Títulos con el color de la identidad élfica */ 
           # h1, h2, h3 { color: #1a4d2e !important; font-family: 'Georgia', serif; }</style>""",unsafe_allow_html=True)
# 1. IDENTIFICACIÓN Y SEGURIDAD
sheet_id = "1d6wWm4k2nFK48OSa8P9-LZ_SnrE6TrzR4eYQtKqpiYo"

# Test1
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
        # CARGAR EL GLOSARIO (Nueva línea a añadir)
        df_glosario = pd.read_excel(xls, sheet_name="Glosario_Competencias")
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
        col1, col2  = st.columns([2,0.7])
        # ... (código previo de ángulos y valores)
        
        with col1:

         with st.spinner('Calculando métricas de rendimiento...'):
            # Aquí va todo su código de: 
            # fig, ax = plt.subplots...
            # col1.pyplot(fig)
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            fig.patch.set_alpha(0) 
            # ESTA ES LA CLAVE: Hacer transparente el fondo de la figura y del eje
            ax.bar(0, 5, width=2*np.pi, color='#fdf5e6', alpha=1.0, zorder=0)
            #ax.set_facecolor('none')
            # Definir los radios para las zonas (asumiendo escala de 0 a 5)
            # Zona Roja (0-2), Amarilla (2-4), Verde (4-5), 
            ax.bar(0, 2, width=2*np.pi, color='red', alpha=0.2, zorder=0)
            ax.bar(0, 4, width=2*np.pi, color='yellow', alpha=0.2, zorder=0, bottom=2)
            ax.bar(0, 5, width=2*np.pi, color='green', alpha=0.2, zorder=0, bottom=4)
            # 1. Dibujar el fondo de comparación (Opcional: un círculo gris al 100%)
            # ax.fill(angulos, [5]*len(angulos), color='gray', alpha=0.1) 

           # 2. Dibujar el polígono del estudiante
            ax.plot(angulos, values_me, color='#e6a029', linewidth=5, label=f'Meta Esperada (ME)', linestyle='dashdot')
            ax.plot(angulos, valores, color="#0047AB", linewidth=5, label=f'Progreso Actual: {estudiante}', linestyle='-')
            ax.fill(angulos, valores, color='#0047AB', alpha=0.5, zorder=2)

            # 3. FIJAR LA ESCALA (Esto evita que el dibujo parezca "máximo" siempre)
            # Si su nota máxima es 5, deje 5. Si es 10, cambie a 10.
            # Esto dibuja los círculos internos en 1, 2, 3, 4 y 5
            ax.set_ylim(0, 5) 
            ax.set_yticks([1, 2, 3, 4, 5]) 
            # MOSTRAR MARCAS DE PORCENTAJE / ESCALA
            # Esto le pone el número a cada círculo para que sea legible
            ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], color="black", size=9)

            # 4. Estética de los ejes
            ax.set_xticks(angulos[:-1])
            ax.set_xticklabels(categorias, fontsize=9, fontweight='bold')
    
            # Color de la malla para que no distraiga
            ax.grid(True, linestyle='--', alpha=0.6)
            # 5. ACTIVACIÓN DE LEYENDAS (Lo que faltaba)
            # Ubicamos la leyenda fuera del gráfico para no obstruir la vista
            #ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            ax.legend(loc='lower left', bbox_to_anchor=(-0.3, -0.1), fontsize=9, frameon=True)

            st.pyplot(fig, transparent=True)
            
        with col2: # Lo ponemos en la columna de la tabla para que no estorbe al radar
            st.write("---") # Una línea divisoria profesional
            # CÁLCULO DE PROMEDIO PARA RECOMPENSA 
            promedio = np.mean(valores)
            # --- LÓGICA DE SEGMENTACIÓN ---
            # Definimos quiénes pertenecen a qué grupo
            colegio = ["Gaby", "Isa", "Dani"]
            universidad = ["Nour", "Gimeno", "Valentin", "Simon"]
            entrenamiento = ["Alejandro", "Zahir", "Farid"] # Ajuste según sus nombres en el Excel
            
            # URL Base de su GitHub
            #base_url = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/"
           
            # 1. DEFINICIÓN DE VARIABLES VISUALES
            # Ajustamos el tamaño a 200px para que se vea imponente
            # ESTILO BASE LIMPIO (Solo lo estructural)
            #estilo_base = "display: flex; justify-content: center; align-items: center; margin: auto; padding: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.3); overflow: hidden;"
            estilo_ajustado = f"display: flex; justify-content: center; align-items: center; margin: -50px 0px 10px 40px; padding: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.3); overflow: hidden;"
            margin_ajuste = "margin: -70px 0px 10px 80px;" # Subir 60px y mover 50px a la derecha
            # Selección de imagen por Categoría y Desempeño
            if estudiante in colegio:
                tipo_actual = "Colegio"
                # FORMA: OVALADA (Ancho != Alto, Radio 50%)
                forma_box = "width: 147px; height: 175px; border-radius: 50% / 50%;"
                # CSS para el fondo general del reporte
                # Fusión en una sola línea de inyección
                st.markdown('<style>.stApp{background-color:#1a4d2e !important;} h1,h2,h3{color:#d4af37 !important;} div[role="alert"]{font-family:Georgia, serif; color:#228b22 !important; background-color:#fdf5e6 !important; border:2px solid #d4af37 !important;}</style>', unsafe_allow_html=True)
                
                # Niveles entrenamiento LÓGICA DE STICKERS MOTIVACIONALES 
                if promedio >= 4.2:
                    # EXCELENCIA: Fondo Verde, Sticker 3aa
                    color_bg = "#000000" # Negro
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MascotaGabi1A.png"
                    
                    st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                        <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #1a4d2e) drop-shadow(0px 0px 10px #1a4d2e); 
                        /* Doble filtro para dar grosor al contorno dorado */"></div>""",unsafe_allow_html=True)
                    st.info(" ☀️ ¡Nivel A: nivel leyenda alcanzado! ¡Continúa así!")
                    st.link_button("🚀 ¡Practica 1 minuto en ThatQuiz!", "https://www.thatquiz.org/es/")
                    st.toast("¡Sigue así! ¡Vas muy bien!", icon="🎉")
                    st.balloons() # Efecto de celebración para el máximo puntaje
                
                elif promedio >= 3.7:
                    # PROGRESO: Fondo Amarillo, Sticker 3bb
                    color_bg = "#000000" # Negro
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MascotaGabi1B.png"
                
                    st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                        <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #d6e629) drop-shadow(0px 0px 10px #d6e629); 
                        /* Doble filtro para dar grosor al contorno dorado */"></div>""",unsafe_allow_html=True)
                    st.info("⭐⭐ Nivel B: Buen progreso. Hay que ajustar detalles...¡Practica 3 minutos diarios! 🚀")
                    st.link_button("🚀 ¡Dale 3 minutos a ThatQuiz!", "https://www.thatquiz.org/es/")
                    st.toast("¡Vas por muy buen camino!", icon="💪")

                elif promedio >= 3.0:
                    # PROGRESO: Fondo Amarillo, Sticker 3bb
                    color_bg = "#000000" # Negro
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MascotaGabi1C.png"
                
                    st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                        <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #e6a029) drop-shadow(0px 0px 10px #e6a029); 
                        /* Doble filtro para dar grosor al contorno dorado */"></div>""",unsafe_allow_html=True)
                    st.info("⭐ Nivel C: Vamos progresando pero hay que ajustar detalles...¡Practica 5 minutos diarios! 🚀")
                    st.link_button("🚀 ¡Dale 2 minutos a phet.colorado.edu!", "https://phet.colorado.edu/sims/cheerpj/rotation/latest/rotation.html?simulation=rotation&locale=es")
                    st.link_button("🚀 ¡Dale 3 minutos a ThatQuiz!", "https://www.thatquiz.org/es/")
                    st.toast("¡Vamos mejorando!", icon="👍")
               
                else:
                    # DESAFÍO: Fondo Rojo, Sticker 3cc
                    color_bg = "#000000" # Negro
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MascotaGabi1D.png"

                    # El estilo inline con el filtro de silueta
                    st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                        <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #d12f0f) drop-shadow(0px 0px 10px #d12f0f; 
                        /* Doble filtro para dar grosor al contorno dorado */"></div>""",unsafe_allow_html=True)
                    st.info("⚙️⚙️ Nivel D: ¡Es momento de apretar tuercas!¡Practica 7 minutos diarios! 🚀 ")
                    st.link_button("🚀 ¡Dale 2 minutos a phet.colorado.edu!", "https://phet.colorado.edu/sims/cheerpj/rotation/latest/rotation.html?simulation=rotation&locale=es")
                    st.link_button("🚀 ¡Dale 5 minutos a ThatQuiz!", "https://www.thatquiz.org/es/")
                    st.toast("¡A ponernos las pilas!", icon="🔋")

            elif estudiante in entrenamiento:
                tipo_actual = "Entrenamiento"
                # FORMA: REDONDA PERFECTA (Ancho == Alto, Radio 50%)
                forma_box = "width: 200px; height: 200px; border-radius: 50%;"
                # CSS para el fondo general del reporte
                # Fusión en una sola línea de inyección
                st.markdown('<style>.stApp{background-color:#2d1b4e !important;} h1,h2,h3{color:#f1c40f !important; font-family:"Courier New", monospace;} div[role="alert"]{font-family:"Courier New", monospace; color:#ffffff !important; background-color:#6c5ce7 !important; border:2px solid #f1c40f !important; box-shadow: 0px 0px 15px #f1c40f;}</style>', unsafe_allow_html=True)
                
                # Niveles entrenamiento LÓGICA DE STICKERS MOTIVACIONALES CÁLCULO DE PROMEDIO PARA RECOMPENSA 
                if promedio >= 4.1:
                    color_bg = "#3210F0" # Cielo Intenso
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Gohan_DragonBall_1A.png"
                    st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} display: flex; justify-content: center; align-items: center;">
                        <img src="{url_img}" style="height: 90%; width: auto;filter: drop-shadow(0px 0px 10px #b5f5f7) drop-shadow(0px 0px 10px #b5f5f7) contrast(1.2);
                        /* Efecto de Aura de Energía para Entrenamiento */"></div>""",unsafe_allow_html=True)
                    st.info("🥇 Nivel A: ¡ Excelente ! 🤸‍♂️")
                    st.toast("¡Bien hecho!", icon="🥋")
                    
                elif promedio >= 3.2: 
                    color_bg = "#3210F0" # Cielo Intenso
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Krilin_DragonBall_1B.png"
                    st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} display: flex; justify-content: center; align-items: center;">
                        <img src="{url_img}" style="height: 105%; width: auto;filter: drop-shadow(0px 0px 25px #b5f5f7) drop-shadow(0px 0px 25px #b5f5f7) contrast(1.2);
                        /* Efecto de Aura de Energía para Entrenamiento */"></div>""",unsafe_allow_html=True)
                    st.info("🥈 Nivel B: Vamos mejorando... 💪")
                    st.toast("Buen progreso. ¡Hay que ajustar detalles...!",icon="🧱")

                elif promedio >= 2.5: 
                    color_bg = "#C9FAFC" # Cielo suave
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Yajirobe_DragonBall_1C.png"
                    st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} display: flex; justify-content: center; align-items: center;">
                        <img src="{url_img}" style="height: 105%; width: auto;filter: drop-shadow(0px 0px 5px #c6f7f7) drop-shadow(0px 0px 35px #c6f7f7) contrast(1.2);
                        /* Efecto de Aura de Energía para Entrenamiento */"></div>""",unsafe_allow_html=True)
                    st.info("Nivel C: Medallita 🥉 porque ya vamos dando.. 🧘‍♀️")
                    st.toast("Ya vamos dando...",icon="🍚") 
            
                else: 
                    color_bg = "#C9FAFC" # Cielo suave
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Oolong_Dragon_Ball_1D.png"
                    st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} display: flex; justify-content: center; align-items: center;">
                        <img src="{url_img}" style="height: 95%; width: auto;filter: drop-shadow(0px 0px 5px #c6f7f7) drop-shadow(0px 0px 35px #c6f7f7) contrast(1.2);
                        /* Efecto de Aura de Energía para Entrenamiento */"></div>""",unsafe_allow_html=True)
                    st.info("Nivel D: Sin medallitas...solo pastillas 💊💊 a ver si mejoramos...")
                    st.toast("Ya vamos dando ... lástima",icon="⏳")             
                       
            
            elif estudiante in universidad:
                tipo_actual = "Universidad"
                # FORMA:CUADRADO TÉCNICO
                forma_box = "width: 200px; height: 200px; border-radius: 15px;"
                # CSS para el fondo general del reporte
                # Fusión en una sola línea de inyección
                st.markdown('<style>.stApp{background-color:#1a4d2e !important;} h1,h2,h3{color:#d4af37 !important;} div[role="alert"]{font-family:Georgia, serif; color:#228b22 !important; background-color:#fdf5e6 !important; border:2px solid #d4af37 !important;}</style>', unsafe_allow_html=True)
                
                # Niveles entrenamiento LÓGICA DE STICKERS MOTIVACIONALES CÁLCULO DE PROMEDIO PARA RECOMPENSA 
                if promedio >= 4.2: 
                    color_bg = "#cf8c0e" # Dorado intenso
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/TrofeoA.png"
                    
                    st.markdown(f'<div style="background-color: {color_bg}; {forma_box}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.success("Bien hecho 🎓📚")
                    st.toast("¡Vamos bien!", icon="🏆")
             
                elif promedio >= 3.5:
                    color_bg = "#97c5fa" # Azul cielo claro
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/TrofeoB.png"
                    
                    st.markdown(f'<div style="background-color: {color_bg}; {forma_box}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.info("Buen progreso. ¡Hay que ajustar detalles...! 📜🖋️")
                    st.toast(" Vamos mejorando", icon="👍")

                else:
                    color_bg = "#e8f4f8" # Azul académico sobrio
                    url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/TrofeoC.png"
                    
                    st.markdown(f'<div style="background-color: {color_bg}; {forma_box}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                    st.warning("Hay que acelerar... 🔍📚")
                    st.toast("¡A ponernos las pilas!", icon="🔋")


            else:
                color_bg = "#ffffff"
                url_img = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MagusOne.png"
                st.markdown(f'<div style="background-color: {color_bg}; {estilo_ajustado}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
                st.info("Reporte de Actividad")
            
           

            # 6. TABLA COLOREADA (Pandas Styling)
            st.write(f"### Detalle de Competencias: {estudiante}")
            df_tabla = df[['Categoria', estudiante]]
            
            def estilo_categoria(val):
                return 'background-color: #fdf5e6; color: #5a3e1b; font-family: Georgia;'
            def semaforo_celda(val):
                #estilo_base = 'font-family: Georgia; color: #fdf5e6; background-color: transparent;'
                if not isinstance(val, (int, float)): 
                    return 'font-family: Georgia; color: #383d41; background-color: #edd19d;'  # Gris
                if val >= 4.0: 
                    color = '#d4edda' # Verde
                elif val >= 3.0: 
                    color = '#fff3cd' # Amarillo
                else: 
                    color = "#f8d7da" # Rojo
                return f'font-family: Georgia; color: #1a4d2e; background-color: {color};'
            
           


            
            # 2. El dataframe original con su semáforo básico
            styled_df = (df_tabla.style.applymap(estilo_categoria, subset=['Categoria']).applymap(semaforo_celda, subset=[estudiante]))
            st.dataframe(styled_df, styled_df.hide(axis="index"),use_container_width=True)
 
             # 2. En la parte donde renderiza la interfaz (donde ya tiene la variable 'estudiante_seleccionado')
            try:
                pdf_bytes = generar_reporte_maestro(estudiante, tipo_actual, df_tabla, df_glosario)
                st.download_button(label=f"📥 Descargar Reporte de Nivel: {estudiante}",data=pdf_bytes,file_name=f"Reporte_{estudiante}_Marzo.pdf",
                mime="application/pdf")
            except Exception as e:
                st.error(f"Asegúrese de que el nombre coincide con la columna: {e}")

            # 1. Lea el archivo (solo una vez)
            try:
                NAME = "CLASES_FEB_MAR_2026.pdf"
                with open(NAME, "rb") as f:
                    datos_pdf = f.read()

            # 2. Cree el botón de descarga
                st.download_button(
                    label="📄"+NAME,
                    data=datos_pdf,
                    file_name=NAME,
                    mime="application/pdf"
                    )
            except FileNotFoundError:
                st.warning("Suba el PDF al repositorio para habilitar la descarga.")        

    except Exception as e:
        st.error(f"Falla técnica en la lectura de la pestaña '{pestaña_autorizada}': {e}")
        st.info("Verifique que el formato del Excel mantenga la columna 'Categoria'.")

else:
    if password:
        st.sidebar.error("Credencial inválida.")
    st.info("Sistema de Gestión de Mentoría. Ingrese su clave para acceder a sus reportes de avance.")
