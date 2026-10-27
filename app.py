import streamlit as st

AUTOR = "Escribe aquí tu nombre"

st.set_page_config(
    page_title="App de Diseño Experimental",
    page_icon="🌱",
    layout="wide",
)

st.title("App de Diseño Experimental")
st.subheader("Ingeniería Agrícola – Universidad de Sucre")
st.write(
    "El diseño experimental permite planear ensayos de campo de forma ordenada, "
    "comparar tratamientos y distinguir sus efectos de la variabilidad natural. "
    "Así, las decisiones sobre cultivos, manejo y producción se apoyan en evidencia "
    "obtenida con métodos claros y verificables."
)

st.header("Módulos")
st.table(
    [
        {
            "Módulo": "DCA",
            "Nombre completo": "Diseño Completamente al Azar",
            "Cuándo se usa": "Cuando las unidades experimentales son homogéneas y los tratamientos se asignan al azar.",
            "Ejemplo agrícola": "Comparar cuatro dosis de fertilizante en parcelas uniformes de yuca.",
            "Estado": "Disponible",
        },
        {
            "Módulo": "DBCA",
            "Nombre completo": "Diseño de Bloques Completos al Azar",
            "Cuándo se usa": "Cuando existe una fuente conocida de variación que puede agruparse en bloques.",
            "Ejemplo agrícola": "Comparar variedades de maíz agrupando parcelas por gradiente de fertilidad.",
            "Estado": "En construcción",
        },
        {
            "Módulo": "DCL",
            "Nombre completo": "Diseño de Cuadrado Latino",
            "Cuándo se usa": "Cuando se necesita controlar dos fuentes de variación mediante filas y columnas.",
            "Ejemplo agrícola": "Comparar tratamientos en un lote con gradientes de humedad y fertilidad.",
            "Estado": "En construcción",
        },
        {
            "Módulo": "DPD",
            "Nombre completo": "Diseño de Parcelas Divididas",
            "Cuándo se usa": "Cuando dos factores se aplican con distinta facilidad o precisión experimental.",
            "Ejemplo agrícola": "Evaluar riego en parcelas principales y variedades en subparcelas.",
            "Estado": "En construcción",
        },
        {
            "Módulo": "Factoriales",
            "Nombre completo": "Diseños Factoriales",
            "Cuándo se usa": "Cuando se estudian simultáneamente varios factores y sus interacciones.",
            "Ejemplo agrícola": "Evaluar dosis de nitrógeno y densidades de siembra en arroz.",
            "Estado": "En construcción",
        },
        {
            "Módulo": "RSM",
            "Nombre completo": "Metodología de Superficie de Respuesta",
            "Cuándo se usa": "Cuando se busca modelar y optimizar una respuesta según factores cuantitativos.",
            "Ejemplo agrícola": "Optimizar temperatura y tiempo de secado para reducir la humedad de yuca.",
            "Estado": "En construcción",
        },
    ]
)

st.header("Instrucciones de uso")
st.markdown(
    "1. Elige un módulo en el menú lateral.\n"
    "2. Carga los datos del ensayo.\n"
    "3. Revisa los resultados y su interpretación.\n"
    "4. Verifica los cálculos a mano y contrasta tus conclusiones."
)

st.warning(
    "Esta app apoya el aprendizaje. El estudiante interpreta los resultados, "
    "verifica supuestos y compara con su cálculo manual."
)

with st.sidebar:
    st.header("Información del curso")
    st.write(f"Autor: {AUTOR}")
    st.write("Curso: Diseño Experimental")
    st.write("Semestre: 2026-2")
