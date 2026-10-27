# Instrucciones para GitHub Copilot

## Contexto del proyecto

- Este repositorio contiene una aplicación de Diseño Experimental desarrollada en Python y Streamlit.
- El proyecto pertenece al curso de Diseño Experimental de Ingeniería Agrícola de la Universidad de Sucre.
- El público principal son estudiantes de Ingeniería Agrícola.

## Estructura del repositorio

- `app.py`: portada de la aplicación.
- `pages/`: un archivo por cada diseño experimental.
- `utils/`: funciones reutilizables; debe incluir `__init__.py`.
- `data/`: archivos CSV de ejemplo.
- `verificacion/`: scripts de R para verificar los análisis.
- Respeta esta estructura al agregar o cambiar funcionalidades.

## Idioma y documentación

- Escribe en español todo el código nuevo, los comentarios, los docstrings y los mensajes visibles de la interfaz.
- Añade un comentario en cada paso estadístico que explique qué se calcula y por qué, con una explicación adecuada para estudiantes de Ingeniería Agrícola.
- Incluye anotaciones de tipos (`type hints`) en las funciones.
- Documenta las funciones con docstrings en estilo Google, redactados en español.

## Dependencias permitidas

Utiliza únicamente estas librerías:

- `streamlit`
- `pandas`
- `numpy`
- `scipy`
- `statsmodels`
- `plotly`
- `openpyxl`

No agregues otras dependencias sin pedir permiso primero.

## Métodos estadísticos

- Ajusta los modelos ANOVA con `statsmodels.formula.api.ols`.
- Calcula las tablas ANOVA con `statsmodels.stats.anova.anova_lm`, usando `typ=2`.
- Realiza las comparaciones de Tukey con `statsmodels.stats.multicomp.pairwise_tukeyhsd`.
- No inventes ni codifiques resultados estadísticos de ejemplo como si fueran resultados reales: todos los números presentados deben provenir del cálculo correspondiente.

## Forma de trabajo del agente

- Antes de modificar archivos, revisa el código y las convenciones existentes en el área relacionada con la solicitud.
- Mantén los cambios acotados al objetivo solicitado y reutiliza las funciones y patrones existentes cuando corresponda.
- En los análisis, comprueba que las variables y los datos usados correspondan al diseño experimental y explica cualquier supuesto relevante para interpretar los resultados.
- Al terminar, resume los cambios y las verificaciones realizadas; indica claramente cualquier parte que no haya sido posible comprobar.

## Verificación

- Antes de terminar una tarea, ejecuta el código pertinente y corrige los errores que aparezcan.
- Si no es posible ejecutar una parte, explica claramente qué impidió verificarla.
