import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Calculadora de Uso de Suelo",
    page_icon="🏗️",
    layout="wide",
)

st.title("Calculadora de Revisión de Uso de Suelo")
st.caption("Densidad · Ocupación del suelo · Densidad urbana")

st.divider()

# ============================================================
# 1. DATOS DEL PROYECTO
# ============================================================

st.subheader("1. Datos del proyecto")

col1, col2 = st.columns(2)

with col1:
    area_terreno = st.number_input(
        "Área del terreno (m²)",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.2f",
    )

    habitaciones = st.number_input(
        "Cantidad total de habitaciones",
        min_value=0,
        value=35,
        step=1,
    )

with col2:
    metodo_area = st.radio(
        "Método para introducir el área construida",
        options=[
            "Calcular con largo y ancho",
            "Introducir área directamente",
        ],
    )

if metodo_area == "Calcular con largo y ancho":
    col_ancho, col_largo = st.columns(2)

    with col_ancho:
        ancho = st.number_input(
            "Ancho construido (m)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
        )

    with col_largo:
        largo = st.number_input(
            "Largo construido (m)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
        )

    area_construida = ancho * largo

else:
    area_construida = st.number_input(
        "Área construida (m²)",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.2f",
    )

st.metric(
    "Área construida utilizada",
    f"{area_construida:,.2f} m²",
)

st.divider()

# ============================================================
# 2. PARÁMETROS NORMATIVOS
# ============================================================

st.subheader("2. Parámetros normativos")

col1, col2, col3 = st.columns(3)

with col1:
    densidad_permitida = st.number_input(
        "Densidad permitida (hab/ha)",
        min_value=0.0,
        value=75.0,
        step=1.0,
    )

with col2:
    ocupacion_permitida = st.number_input(
        "Ocupación permitida (%)",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=1.0,
    )

with col3:
    densidad_urbana_permitida = st.number_input(
        "Densidad urbana permitida (hab/ha)",
        min_value=0.0,
        value=400.0,
        step=1.0,
    )


# ============================================================
# 3. CÁLCULO DE DENSIDAD
# ============================================================

if area_terreno > 0:

    area_ha = area_terreno / 10000

    densidad = habitaciones / area_ha

else:

    area_ha = 0
    densidad = 0


densidad_excede = densidad > densidad_permitida


# ============================================================
# 4. DENSIDAD URBANA
# ============================================================

habitantes_total = None
densidad_urbana = None
densidad_urbana_excede = None


if densidad_excede:

    st.divider()

    st.subheader("3. Densidad urbana")

    st.warning(
        "La densidad de habitaciones supera el límite permitido. "
        "Debe calcularse la densidad urbana."
    )

    st.write(
        "Introduzca las diferentes tipologías de unidades del proyecto:"
    )


    if "tipologias" not in st.session_state:

        st.session_state.tipologias = [
            {
                "nombre": "Apartamento de 03 habitaciones",
                "unidades": 0,
                "habitantes": 4,
            }
        ]


    filas = []


    for i, item in enumerate(st.session_state.tipologias):

        col1, col2, col3, col4 = st.columns([3, 1.2, 1.5, 0.5])


        with col1:

            nombre = st.text_input(
                "Tipología" if i == 0 else "",
                value=item["nombre"],
                key=f"nombre_{i}",
            )


        with col2:

            unidades = st.number_input(
                "Unidades" if i == 0 else "",
                min_value=0,
                value=int(item["unidades"]),
                step=1,
                key=f"unidades_{i}",
            )


        with col3:

            habitantes_por_unidad = st.number_input(
                "Hab./unidad" if i == 0 else "",
                min_value=0,
                value=int(item["habitantes"]),
                step=1,
                key=f"habitantes_{i}",
            )


        with col4:

            eliminar = st.button(
                "✕",
                key=f"eliminar_{i}",
            )


        if eliminar:

            st.session_state.tipologias.pop(i)

            st.rerun()


        filas.append(
            {
                "Tipología": nombre,
                "Unidades": unidades,
                "Hab./unidad": habitantes_por_unidad,
                "Habitantes": unidades * habitantes_por_unidad,
            }
        )


    if st.button("＋ Agregar tipología"):

        st.session_state.tipologias.append(
            {
                "nombre": "Nueva tipología",
                "unidades": 0,
                "habitantes": 0,
            }
        )

        st.rerun()


    tabla_tipologias = pd.DataFrame(filas)


    st.dataframe(
        tabla_tipologias,
        use_container_width=True,
        hide_index=True,
    )


    habitantes_total = tabla_tipologias["Habitantes"].sum()


    densidad_urbana = habitantes_total / area_ha


    densidad_urbana_excede = (
        densidad_urbana > densidad_urbana_permitida
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Total de habitantes",
            f"{habitantes_total:,.0f}",
        )


    with col2:

        st.metric(
            "Densidad urbana",
            f"{densidad_urbana:,.2f} hab/ha",
        )


else:

    st.info(
        "La densidad urbana no aplica porque todavía no "
        "se ha introducido un área de terreno válida."
    )


# ============================================================
# 5. OCUPACIÓN DEL SUELO
# ============================================================

st.divider()

st.subheader("4. Ocupación del suelo")


area_construida = ancho * largo


if area_terreno > 0:

    ocupacion = (
        area_construida / area_terreno
    ) * 100

else:

    ocupacion = 0


ocupacion_excede = ocupacion > ocupacion_permitida


# ============================================================
# 6. RESULTADOS
# ============================================================

st.divider()

st.subheader("5. Resultado de la evaluación")


estado_densidad = (
    "EXCEDE"
    if densidad_excede
    else "ADECUADA"
)


estado_ocupacion = (
    "EXCEDE"
    if ocupacion_excede
    else "ADECUADA"
)


if densidad_urbana is None:

    estado_urbana = "NO APLICA"

    resultado_urbana = "No aplica"

else:

    estado_urbana = (
        "EXCEDE"
        if densidad_urbana_excede
        else "ADECUADA"
    )

    resultado_urbana = (
        f"{densidad_urbana:,.2f} hab/ha"
    )


resultados = pd.DataFrame(
    [
        [
            "Área del terreno",
            f"{area_terreno:,.2f} m²",
            "—",
            "—",
        ],

        [
            "Área del terreno",
            f"{area_ha:,.6f} ha",
            "—",
            "—",
        ],

        [
            "Densidad",
            f"{densidad:,.2f} hab/ha",
            f"{densidad_permitida:,.2f} hab/ha",
            estado_densidad,
        ],

        [
            "Área construida",
            f"{area_construida:,.2f} m²",
            "—",
            "—",
        ],

        [
            "Ocupación",
            f"{ocupacion:,.2f} %",
            f"{ocupacion_permitida:,.2f} %",
            estado_ocupacion,
        ],

        [
            "Densidad urbana",
            resultado_urbana,
            f"{densidad_urbana_permitida:,.2f} hab/ha",
            estado_urbana,
        ],
    ],

    columns=[
        "Verificación",
        "Resultado",
        "Permitido",
        "Estado",
    ],
)


st.dataframe(
    resultados,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# 7. RESPUESTA
# ============================================================

st.subheader("6. Respuesta")


if (
    not densidad_excede
    and not ocupacion_excede
):

    decision = (
        "PROCEDE A CARTA DE NO OBJECIÓN "
        "DEFINITIVA DE USO DE SUELO"
    )

    detalle = (
        "La densidad y la ocupación del suelo "
        "se encuentran dentro de los límites permitidos."
    )

    tipo = "success"


elif (
    densidad_excede
    and densidad_urbana_excede
):

    decision = (
        "PROCEDE A CARTA Y REVISIÓN "
        "DEL COMITÉ TÉCNICO"
    )

    detalle = (
        "La densidad de habitaciones supera el límite "
        "y la densidad urbana también supera el límite permitido."
    )

    tipo = "warning"


elif ocupacion_excede:

    decision = (
        "POSPONER / REMITIR A COMITÉ "
        "SEGÚN EL PROCEDIMIENTO APLICABLE"
    )

    detalle = (
        "La ocupación del suelo supera "
        "el porcentaje permitido."
    )

    tipo = "warning"


else:

    decision = (
        "CONTINUAR A REVISIÓN "
        "SEGÚN PROCEDIMIENTO"
    )

    detalle = (
        "La densidad de habitaciones supera el límite, "
        "pero la densidad urbana está dentro del límite permitido."
    )

    tipo = "info"


if tipo == "success":

    st.success(f"**{decision}**")

elif tipo == "warning":

    st.warning(f"**{decision}**")

else:

    st.info(f"**{decision}**")


st.write(detalle)


st.caption(
    "La matriz de decisiones puede ajustarse "
    "cuando se confirme el procedimiento institucional definitivo."
)
