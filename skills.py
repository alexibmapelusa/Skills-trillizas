import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import gspread
from fpdf import FPDF
from datetime import datetime
from urllib.parse import quote

# ============================== CONFIGURACIÓN ==============================
# ⚠️ Los tres valores marcados con ⚠️ hay que ponerlos antes de subir el archivo.

sheet_id = "1d6wWm4k2nFK48OSa8P9-LZ_SnrE6TrzR4eYQtKqpiYo"   # libro de siempre (público por enlace)
SHEET_COLLEGE = "1DMulgmqCyjeSZVA521atqPu91R-49d-l04UJiLeclP0"         # ⚠️ ID del libro Resultados_Competencias_College

# La 'llave' es lo que el estudiante escribe, la 'pestaña' es el nombre real en el Excel
llaves_acceso = {
    "Clau2026": "Trillizas",
    "NourandGimeno2026": "TAF",
    "Valentin2026": "Mecanica_Fluidos",
    "Simon2026": "Matematicas_II",
    "Saiyajines2026": "Gym_Training",
    "College2026": "Diagnostico_College",
}

# clave -> nombre del estudiante en MAYÚSCULAS, igual que como llega del Form (el motor lo pasa a mayúsculas)
ESTUDIANTES_COLLEGE = {"College2026": "ALEXANDER MANCHESTER"}      # ⚠️ nombre real

# (título del botón, enlace PRELLENADO del Form con NOMBRE_AQUI en el campo del nombre)
DIAGNOSTICOS_COLLEGE = [
    ("📐 Diagnóstico 1 · Functions & Graphs", "https://docs.google.com/forms/d/e/1FAIpQLSdHkqBz2gI8IbcdqKL2h9eDHOmbgotVtCjsT8Hv3scRwvpRhw/viewform?usp=pp_url&entry.359099417=ALEXANDER+MANCHESTER"),   # ⚠️ enlace del Form
    ("📐 Diagnóstico 2 · Functions & Graphs", "https://docs.google.com/forms/d/e/1FAIpQLSdGVx0FiCD40TIsOHnqj9Tj10RdzH6E8rGP5hDvSab_PpNWBA/viewform?usp=pp_url&entry.956039767=ALEXANDER+MANCHESTER"),   # ⚠️ enlace del Form

]

st.set_page_config(page_title="Sistema de Mentoría - Alexander Barraza", layout="wide")


# ============================== UTILIDADES ==============================
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generar_reporte_maestro(nombre_estudiante, tipo_cliente, df_notas, df_glosario):
    pdf = FPDF()
    pdf.add_page()

    config_estetica = {
        "Colegio": {"bg": "#1a4d2e", "tit": "#d4af37", "tab": "#228b22", "font": "Arial"},
        "Entrenamiento": {"bg": "#2d1b4e", "tit": "#f1c40f", "tab": "#6c5ce7", "font": "Courier"},
        "Universidad": {"bg": "#0a192f", "tit": "#64ffda", "tab": "#172a45", "font": "Helvetica"},
        "College": {"bg": "#0a192f", "tit": "#64ffda", "tab": "#172a45", "font": "Helvetica"},
    }
    estilo = config_estetica.get(tipo_cliente, config_estetica["Colegio"])
    rgb_bg, rgb_tit, rgb_tab = hex_to_rgb(estilo["bg"]), hex_to_rgb(estilo["tit"]), hex_to_rgb(estilo["tab"])

    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
             "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_actual = meses[datetime.now().month - 1]
    año_actual = datetime.now().year

    pdf.set_fill_color(*rgb_bg)
    pdf.rect(0, 0, 210, 297, 'F')

    pdf.set_font(estilo["font"], 'B', 20)
    pdf.set_text_color(*rgb_tit)
    pdf.cell(0, 20, f'INFORME DE RENDIMIENTO - {mes_actual.upper()} {año_actual}', 0, 1, 'C')

    pdf.set_font(estilo["font"], 'B', 16)
    pdf.cell(0, 10, f'Estudiante: {nombre_estudiante.upper()}', 0, 1, 'C')
    pdf.ln(10)

    for index, row in df_notas.iterrows():
        materia = str(row['Categoria']).upper()
        nota_valor = int(row[nombre_estudiante])
        materia_search = str(row['Categoria']).strip().upper()

        filtro = df_glosario[
            (df_glosario['Categoria'].str.upper().str.contains(materia_search[:20], na=False, regex=False)) &
            (df_glosario['Tipo_Cliente'] == tipo_cliente) &
            (df_glosario['Nivel'].astype(str) == str(nota_valor))
        ]

        if not filtro.empty:
            estado = filtro['Estatus'].values[0]
            logro = filtro['Descripción_Logro'].values[0]
        else:
            print(f"DEBUG LOCAL -> No hallado: {materia_search[:20]} | Nivel: {nota_valor} | Cliente: {tipo_cliente}")
            estado = "N/A"
            logro = "Evaluación técnica en proceso."

        pdf.set_font(estilo["font"], 'B', 11)
        pdf.set_fill_color(*rgb_tab)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, f" {materia} - NIVEL {nota_valor} [{estado}]", 1, 1, 'L', True)

        pdf.set_font(estilo["font"], '', 10)
        pdf.set_text_color(245, 245, 220)
        pdf.multi_cell(0, 5, logro, 0, 'L')
        pdf.ln(3)

    # Firma y contacto
    pdf.set_y(-40)
    pdf.set_draw_color(*rgb_tit)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    magos = {
        "Colegio": "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/MagusOne.png",
        "Universidad": "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Magus_Howl.png",
        "College": "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Magus_Howl.png",
    }
    url_mago = magos.get(tipo_cliente, magos["Colegio"])
    try:
        pdf.image(url_mago, x=10, y=pdf.get_y(), w=15)
    except Exception:
        pass

    pdf.set_x(30)
    pdf.set_font(estilo["font"], 'B', 10)
    pdf.set_text_color(*rgb_tit)
    pdf.cell(0, 5, "ALEXANDER BARRAZA", 0, 1, 'L')

    pdf.set_x(30)
    pdf.set_font(estilo["font"], '', 8)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 4, "Físico Profesional | Mentoría Internacional", 0, 1, 'L')

    pdf.set_x(30)
    pdf.set_text_color(173, 216, 230)
    pdf.cell(0, 4, "Contacto WhatsApp: +57 3164880199", 0, 1, 'L')

    try:
        output_pdf = pdf.output(dest='S')
        if isinstance(output_pdf, str):
            return output_pdf.encode('latin-1', errors='replace')
        return bytes(output_pdf)
    except Exception:
        return b"Error en la generacion de bytes del PDF"


# ============================== COLLEGE ==============================
@st.cache_data(ttl=60)
def leer_libro_college(id_libro):
    """Lee el libro privado de College con la cuenta de servicio guardada en st.secrets."""
    gc = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    libro = gc.open_by_key(id_libro)
    df = pd.DataFrame(libro.worksheet("Diagnostico_College").get_all_records())
    df_gl = pd.DataFrame(libro.worksheet("Glosario_Competencias").get_all_records())
    return df, df_gl


def panel_diagnosticos(estudiante=None):
    st.subheader("📝 Diagnósticos / Diagnostics")
    cols = st.columns(len(DIAGNOSTICOS_COLLEGE))
    for col, (titulo, url) in zip(cols, DIAGNOSTICOS_COLLEGE):
        if estudiante:
            url = url.replace("NOMBRE_AQUI", quote(estudiante))
        col.link_button(titulo, url, use_container_width=True)


def mostrar_college(df, df_glosario, solo=None):
    meta = ["Estudiante", "Fecha_Respuesta", "Test", "Promedio"]
    categorias = [c for c in df.columns if c not in meta]
    fila_me = df[df["Estudiante"] == "ME"]
    values_me = [float(fila_me.iloc[0][c]) for c in categorias] if not fila_me.empty else [4.0] * len(categorias)
    df_est = df[df["Estudiante"] != "ME"]
    if solo:
        df_est = df_est[df_est["Estudiante"] == solo]

    # Paleta sobria de College (azul marino + turquesa)
    st.markdown('<style>.stApp{background-color:#0a192f !important; color:#e6f1ff !important;} h1,h2,h3{color:#64ffda !important; font-family:Helvetica, Arial, sans-serif;} label, .stMarkdown p{color:#e6f1ff !important;} div[role="alert"]{font-family:Helvetica, Arial, sans-serif; color:#e6f1ff !important; background-color:#172a45 !important; border:2px solid #64ffda !important;}</style>', unsafe_allow_html=True)

    st.title("📈 Reporte: Matemáticas College")
    panel_diagnosticos(solo)

    if df_est.empty:
        st.warning("Aún no hay registros para mostrar. Cuando se complete el diagnóstico, el reporte aparecerá aquí.")
        return

    estudiante = solo if solo else st.selectbox("Seleccione el Perfil para visualizar:", sorted(df_est["Estudiante"].unique()))
    regs = df_est[df_est["Estudiante"] == estudiante].reset_index(drop=True)
    etiquetas = [f"{r.Fecha_Respuesta} - {r.Test}" for r in regs.itertuples()]
    idx = st.selectbox("Registro:", range(len(regs)), index=len(regs) - 1, format_func=lambda i: etiquetas[i])
    fila = regs.iloc[idx]
    valores = [float(fila[c]) for c in categorias]
    promedio = float(np.mean(valores))
    valores_c, me_c = valores + valores[:1], values_me + values_me[:1]
    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += angulos[:1]

    col1, col2 = st.columns([2, 0.7])
    with col1:
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        fig.patch.set_alpha(0)
        ax.bar(0, 5, width=2 * np.pi, color='#fdf5e6', alpha=1.0, zorder=0)
        ax.bar(0, 2, width=2 * np.pi, color='red', alpha=0.2, zorder=0)
        ax.bar(0, 4, width=2 * np.pi, color='yellow', alpha=0.2, zorder=0, bottom=2)
        ax.bar(0, 5, width=2 * np.pi, color='green', alpha=0.2, zorder=0, bottom=4)
        ax.plot(angulos, me_c, color='#e6a029', linewidth=5, label='Meta Esperada (ME)', linestyle='dashdot')
        ax.plot(angulos, valores_c, color="#0047AB", linewidth=5, label=f'Progreso Actual: {estudiante}')
        ax.fill(angulos, valores_c, color='#0047AB', alpha=0.5, zorder=2)
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], color="black", size=9)
        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(categorias, fontsize=8, fontweight='bold', color='#e6f1ff')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='lower left', bbox_to_anchor=(-0.3, -0.1), fontsize=9, frameon=True)
        st.pyplot(fig, transparent=True)

    with col2:
        st.write("---")

        # ===== AVATAR: cambia según el PROMEDIO del registro (umbral, imagen, brillo, alto, mensaje) =====
        base = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/Howl_Castillo_Vagabundo_"
        niveles_img = [
            (4.2, "2A", "#7ea8fc", "150%", "Bien hecho 🎓📚"),
            (3.5, "2B", "#d6e629", "80%", "Buen progreso. ¡Hay que ajustar detalles...! 📜🖋️"),
            (3.0, "2C", "#e6a029", "80%", "Hay que acelerar un poco más... 🔍📚"),
            (0.0, "1C", "#d12f0f", "80%", "Hay que acelerar mucho... 🔍🔍📚📚"),
        ]
        _, suf, brillo, alto, msg = next(n for n in niveles_img if promedio >= n[0])
        estilo = "display: flex; justify-content: center; align-items: center; margin: -50px 0px 10px 40px; padding: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.3); overflow: hidden;"
        forma = "width: 200px; height: 200px; border-radius: 15px; margin: -70px 0px 10px 100px;"
        st.markdown(f"""<div style="background-color: #140744; {estilo} {forma}"><img src="{base}{suf}.png" style="height: {alto}; width: auto; filter: drop-shadow(0px 0px 10px {brillo}) drop-shadow(0px 0px 10px {brillo});"></div>""", unsafe_allow_html=True)
        st.info(msg)

        st.write(f"### Detalle de Competencias: {estudiante}")
        df_tabla = pd.DataFrame({"Categoria": categorias, estudiante: [int(v) for v in valores]})

        def semaforo(val):
            color = '#1f6f5c' if val >= 4 else '#8a6d1d' if val >= 3 else '#8c2f39'
            return f'font-family: Helvetica; color: #ffffff; background-color: {color};'

        def cat_estilo(val):
            return 'background-color: #172a45; color: #e6f1ff; font-family: Helvetica;'

        st.dataframe(df_tabla.style.map(cat_estilo, subset=['Categoria']).map(semaforo, subset=[estudiante]),
                     hide_index=True, use_container_width=True)

        try:
            pdf_bytes = generar_reporte_maestro(estudiante, "College", df_tabla, df_glosario)
            st.download_button(label=f"📥 Descargar Reporte de Nivel: {estudiante}", data=pdf_bytes,
                               file_name=f"Reporte_{estudiante}.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"No se pudo generar el PDF: {e}")

    with st.expander("📖 Descriptor de cada competencia según el glosario"):
        for cat, val in zip(categorias, valores):
            f = df_glosario[(df_glosario["Categoria"] == cat) & (df_glosario["Tipo_Cliente"] == "College")
                            & (df_glosario["Nivel"].astype(int) == int(val))]
            if not f.empty:
                st.markdown(f"**{cat}: nivel {int(val)} ({f['Estatus'].values[0]})** — {f['Descripción_Logro'].values[0]}")


# ============================== FLUJO ANTIGUO (Trillizas, TAF, Universidad, Entrenamiento) ==============================
def mostrar_reporte_clasico(df, df_glosario, pestaña_autorizada):
    st.title(f"📈 Reporte: {pestaña_autorizada.replace('_', ' ')}")

    columnas_estudiantes = [col for col in df.columns if col not in ['Categoria', 'ME']]
    estudiante = st.selectbox("Seleccione el Perfil para visualizar:", columnas_estudiantes)

    categorias = df['Categoria'].tolist()
    valores = df[estudiante].tolist()
    values_me = df['ME'].tolist()

    valores += valores[:1]
    values_me += values_me[:1]
    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += angulos[:1]

    col1, col2 = st.columns([2, 0.7])

    with col1:
        with st.spinner('Calculando métricas de rendimiento...'):
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            fig.patch.set_alpha(0)
            ax.bar(0, 5, width=2*np.pi, color='#fdf5e6', alpha=1.0, zorder=0)
            ax.bar(0, 2, width=2*np.pi, color='red', alpha=0.2, zorder=0)
            ax.bar(0, 4, width=2*np.pi, color='yellow', alpha=0.2, zorder=0, bottom=2)
            ax.bar(0, 5, width=2*np.pi, color='green', alpha=0.2, zorder=0, bottom=4)
            ax.plot(angulos, values_me, color='#e6a029', linewidth=5, label='Meta Esperada (ME)', linestyle='dashdot')
            ax.plot(angulos, valores, color="#0047AB", linewidth=5, label=f'Progreso Actual: {estudiante}', linestyle='-')
            ax.fill(angulos, valores, color='#0047AB', alpha=0.5, zorder=2)
            ax.set_ylim(0, 5)
            ax.set_yticks([1, 2, 3, 4, 5])
            ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], color="black", size=9)
            ax.set_xticks(angulos[:-1])
            ax.set_xticklabels(categorias, fontsize=9, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc='lower left', bbox_to_anchor=(-0.3, -0.1), fontsize=9, frameon=True)
            st.pyplot(fig, transparent=True)

    tipo_actual = "Otro"
    with col2:
        st.write("---")
        promedio = np.mean(valores)

        colegio = ["Gaby", "Isa", "Dani"]
        universidad = ["Nour", "Gimeno", "Valentin", "Simon"]
        entrenamiento = ["Alejandro", "Zahir", "Farid"]

        estilo_ajustado = "display: flex; justify-content: center; align-items: center; margin: -50px 0px 10px 40px; padding: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.3); overflow: hidden;"
        margin_ajuste = "margin: -70px 0px 10px 100px;"
        img_base = "https://raw.githubusercontent.com/alexibmapelusa/Skills-trillizas/main/images/"

        if estudiante in colegio:
            tipo_actual = "Colegio"
            forma_box = "width: 147px; height: 175px; border-radius: 50% / 50%;"
            st.markdown('<style>.stApp{background-color:#1a4d2e !important;} h1,h2,h3{color:#d4af37 !important;} div[role="alert"]{font-family:Georgia, serif; color:#228b22 !important; background-color:#fdf5e6 !important; border:2px solid #d4af37 !important;}</style>', unsafe_allow_html=True)

            if promedio >= 4.2:
                color_bg = "#000000"
                url_img = img_base + "MascotaGabi1A.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #1a4d2e) drop-shadow(0px 0px 10px #1a4d2e);"></div>""", unsafe_allow_html=True)
                st.info(" ☀️ ¡Nivel A: nivel leyenda alcanzado! ¡Continúa así!")
                st.link_button("🚀 ¡Practica 1 minuto en ThatQuiz!", "https://www.thatquiz.org/es/")
                st.toast("¡Sigue así! ¡Vas muy bien!", icon="🎉")
                st.balloons()

            elif promedio >= 3.7:
                color_bg = "#000000"
                url_img = img_base + "MascotaGabi1B.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #d6e629) drop-shadow(0px 0px 10px #d6e629);"></div>""", unsafe_allow_html=True)
                st.info("⭐⭐ Nivel B: Buen progreso. Hay que ajustar detalles...¡Practica 3 minutos diarios! 🚀")
                st.link_button("🚀 ¡Dale 3 minutos a ThatQuiz!", "https://www.thatquiz.org/es/")
                st.toast("¡Vas por muy buen camino!", icon="💪")

            elif promedio >= 3.0:
                color_bg = "#000000"
                url_img = img_base + "MascotaGabi1C.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #e6a029) drop-shadow(0px 0px 10px #e6a029);"></div>""", unsafe_allow_html=True)
                st.info("⭐ Nivel C: Vamos progresando pero hay que ajustar detalles...¡Practica 5 minutos diarios! 🚀")
                st.link_button("🚀 ¡Dale 2 minutos a phet.colorado.edu!", "https://phet.colorado.edu/sims/cheerpj/rotation/latest/rotation.html?simulation=rotation&locale=es")
                st.link_button("🚀 ¡Dale 3 minutos a ThatQuiz!", "https://www.thatquiz.org/es/")
                st.toast("¡Vamos mejorando!", icon="👍")

            else:
                color_bg = "#000000"
                url_img = img_base + "MascotaGabi1D.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #d12f0f) drop-shadow(0px 0px 10px #d12f0f);"></div>""", unsafe_allow_html=True)
                st.info("⚙️⚙️ Nivel D: ¡Es momento de apretar tuercas!¡Practica 7 minutos diarios! 🚀 ")
                st.link_button("🚀 ¡Dale 2 minutos a phet.colorado.edu!", "https://phet.colorado.edu/sims/cheerpj/rotation/latest/rotation.html?simulation=rotation&locale=es")
                st.link_button("🚀 ¡Dale 5 minutos a ThatQuiz!", "https://www.thatquiz.org/es/")
                st.toast("¡A ponernos las pilas!", icon="🔋")

        elif estudiante in entrenamiento:
            tipo_actual = "Entrenamiento"
            forma_box = "width: 200px; height: 200px; border-radius: 50%;"
            st.markdown('<style>.stApp{background-color:#2d1b4e !important;} h1,h2,h3{color:#f1c40f !important; font-family:"Courier New", monospace;} div[role="alert"]{font-family:"Courier New", monospace; color:#ffffff !important; background-color:#6c5ce7 !important; border:2px solid #f1c40f !important; box-shadow: 0px 0px 15px #f1c40f;}</style>', unsafe_allow_html=True)

            if promedio >= 4.1:
                color_bg = "#3210F0"
                url_img = img_base + "Gohan_DragonBall_1A.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 90%; width: auto;filter: drop-shadow(0px 0px 10px #b5f5f7) drop-shadow(0px 0px 10px #b5f5f7) contrast(1.2);"></div>""", unsafe_allow_html=True)
                st.info("🥇 Nivel A: ¡ Excelente ! 🤸‍♂️")
                st.toast("¡Bien hecho!", icon="🥋")

            elif promedio >= 3.2:
                color_bg = "#3210F0"
                url_img = img_base + "Krilin_DragonBall_1B.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 105%; width: auto;filter: drop-shadow(0px 0px 25px #b5f5f7) drop-shadow(0px 0px 25px #b5f5f7) contrast(1.2);"></div>""", unsafe_allow_html=True)
                st.info("🥈 Nivel B: Vamos mejorando... 💪")
                st.toast("Buen progreso. ¡Hay que ajustar detalles...!", icon="🧱")

            elif promedio >= 2.5:
                color_bg = "#C9FAFC"
                url_img = img_base + "Yajirobe_DragonBall_1C.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 105%; width: auto;filter: drop-shadow(0px 0px 5px #c6f7f7) drop-shadow(0px 0px 35px #c6f7f7) contrast(1.2);"></div>""", unsafe_allow_html=True)
                st.info("Nivel C: Medallita 🥉 porque ya vamos dando.. 🧘‍♀️")
                st.toast("Ya vamos dando...", icon="🍚")

            else:
                color_bg = "#C9FAFC"
                url_img = img_base + "Oolong_Dragon_Ball_1D.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 95%; width: auto;filter: drop-shadow(0px 0px 5px #c6f7f7) drop-shadow(0px 0px 35px #c6f7f7) contrast(1.2);"></div>""", unsafe_allow_html=True)
                st.info("Nivel D: Sin medallitas...solo pastillas 💊💊 a ver si mejoramos...")
                st.toast("Ya vamos dando ... lástima", icon="⏳")

        elif estudiante in universidad:
            tipo_actual = "Universidad"
            forma_box = "width: 200px; height: 200px; border-radius: 15px;"
            st.markdown('<style>.stApp{background-color:#1a4d2e !important;} h1,h2,h3{color:#d4af37 !important;} div[role="alert"]{font-family:Georgia, serif; color:#228b22 !important; background-color:#fdf5e6 !important; border:2px solid #d4af37 !important;}</style>', unsafe_allow_html=True)

            if promedio >= 4.2:
                color_bg = "#140744"
                url_img = img_base + "Howl_Castillo_Vagabundo_2A.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 150%; width: auto;filter: drop-shadow(0px 0px 10px #7ea8fc) drop-shadow(0px 0px 10px #7ea8fc);"></div>""", unsafe_allow_html=True)
                st.info("Bien hecho 🎓📚")
                st.toast("¡Vamos bien!", icon="🏆")

            elif promedio >= 3.5:
                color_bg = "#140744"
                url_img = img_base + "Howl_Castillo_Vagabundo_2B.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #d6e629) drop-shadow(0px 0px 10px #d6e629);"></div>""", unsafe_allow_html=True)
                st.info("Buen progreso. ¡Hay que ajustar detalles...! 📜🖋️")
                st.toast(" Vamos mejorando", icon="👍")

            elif promedio >= 3.0:
                color_bg = "#140744"
                url_img = img_base + "Howl_Castillo_Vagabundo_2C.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #e6a029) drop-shadow(0px 0px 10px #e6a029);"></div>""", unsafe_allow_html=True)
                st.info("Hay que acelerar un poco mas... 🔍📚")
                st.toast("¡A ponernos las pilas!", icon="🔋")

            else:
                color_bg = "#140744"
                url_img = img_base + "Howl_Castillo_Vagabundo_1C.png"
                st.markdown(f"""<div style="background-color: {color_bg}; {estilo_ajustado} {forma_box} {margin_ajuste} display: flex; justify-content: center; align-items: center;">
                    <img src="{url_img}" style="height: 80%; width: auto;filter: drop-shadow(0px 0px 10px #d12f0f) drop-shadow(0px 0px 10px #d12f0f);"></div>""", unsafe_allow_html=True)
                st.info("Hay que acelerar mucho... 🔍🔍📚📚")
                st.toast("¡Estamos graves!", icon="🔋")

        else:
            color_bg = "#ffffff"
            url_img = img_base + "MagusOne.png"
            st.markdown(f'<div style="background-color: {color_bg}; {estilo_ajustado}"><img src="{url_img}" style="width: 100%;"></div>', unsafe_allow_html=True)
            st.info("Reporte de Actividad")

        # Tabla coloreada
        st.write(f"### Detalle de Competencias: {estudiante}")
        df_tabla = df[['Categoria', estudiante]]

        def estilo_categoria(val):
            return 'background-color: #fdf5e6; color: #5a3e1b; font-family: Georgia;'

        def semaforo_celda(val):
            if not isinstance(val, (int, float)):
                return 'font-family: Georgia; color: #383d41; background-color: #edd19d;'
            if val >= 4.0:
                color = '#d4edda'
            elif val >= 3.0:
                color = '#fff3cd'
            else:
                color = "#f8d7da"
            return f'font-family: Georgia; color: #1a4d2e; background-color: {color};'

        styled_df = (df_tabla.style.map(estilo_categoria, subset=['Categoria'])
                     .map(semaforo_celda, subset=[estudiante])).hide(axis="index")
        st.dataframe(styled_df, use_container_width=True)

        try:
            pdf_bytes = generar_reporte_maestro(estudiante, tipo_actual, df_tabla, df_glosario)
            st.download_button(label=f"📥 Descargar Reporte de Nivel: {estudiante}", data=pdf_bytes,
                               file_name=f"Reporte_{estudiante}_Marzo.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Asegúrese de que el nombre coincide con la columna: {e}")

    if tipo_actual == "Colegio":
        try:
            NAME = "CLASES_FEB_MAR_2026.pdf"
            with open(NAME, "rb") as f:
                datos_pdf = f.read()
            st.download_button(label="📄" + NAME, data=datos_pdf, file_name=NAME, mime="application/pdf")
        except FileNotFoundError:
            st.warning("Suba el PDF al repositorio para habilitar la descarga.")


# ============================== INTERFAZ PRINCIPAL ==============================
st.sidebar.title("🔐 Validación de Mentoría")
password = st.sidebar.text_input("Ingrese su código de acceso:", type="password")

if password in llaves_acceso:
    st.toast("Reporte actualizado correctamente", icon="✅")
    pestaña_autorizada = llaves_acceso[password]

    # --- College: libro privado, leído con la cuenta de servicio ---
    if pestaña_autorizada == "Diagnostico_College":
        try:
            df_c, df_gl = leer_libro_college(SHEET_COLLEGE)
            mostrar_college(df_c, df_gl, ESTUDIANTES_COLLEGE.get(password))
        except Exception as e:
            st.error(f"No se pudo leer el libro de College: {e}")
        st.stop()

    # --- Resto de claves: libro público por enlace, como siempre ---
    url_export = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    try:
        xls = pd.ExcelFile(url_export)
        df = pd.read_excel(xls, sheet_name=pestaña_autorizada)
        df_glosario = pd.read_excel(xls, sheet_name="Glosario_Competencias")
        df = df.dropna(how='all', axis=1)
        mostrar_reporte_clasico(df, df_glosario, pestaña_autorizada)
    except Exception as e:
        st.error(f"Falla técnica en la lectura de la pestaña '{pestaña_autorizada}': {e}")
        st.info("Verifique que el formato del Excel mantenga la columna 'Categoria'.")

else:
    if password:
        st.sidebar.error("Credencial inválida.")
    st.info("Sistema de Gestión de Mentoría. Ingrese su clave para acceder a sus reportes de avance.")



# cd "f:\Disco Actual\6.Programacion\MiniJarviz"
# streamlit run skills.py
