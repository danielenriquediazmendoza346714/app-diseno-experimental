"""Funciones reutilizables para el análisis de un DCA de un factor."""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import BinaryIO

import pandas as pd
from scipy.stats import studentized_range
from statsmodels.formula.api import ols
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def cargar_datos(archivo: str | Path | BinaryIO) -> pd.DataFrame:
    """Carga datos desde un archivo CSV o Excel.

    Args:
        archivo: Ruta o archivo binario con extensión `.csv` o `.xlsx`.

    Returns:
        Un DataFrame con los datos del archivo.

    Raises:
        ValueError: Si la extensión no corresponde a CSV o Excel `.xlsx`.
    """
    # La extensión permite seleccionar un lector compatible con cada formato.
    nombre_archivo = getattr(archivo, "name", archivo)
    extension = Path(str(nombre_archivo)).suffix.lower()

    if extension == ".csv":
        # El motor de Python infiere el separador entre coma y punto y coma.
        return pd.read_csv(archivo, sep=None, engine="python")
    if extension == ".xlsx":
        # Excel se lee directamente para conservar correctamente tipos y celdas.
        return pd.read_excel(archivo)

    raise ValueError("Formato no compatible. Use un archivo CSV o Excel (.xlsx).")


def validar_dca(df: pd.DataFrame, col_trat: str, col_resp: str) -> list[str]:
    """Valida los datos mínimos requeridos para un DCA de un factor.

    Args:
        df: Datos del experimento.
        col_trat: Nombre de la columna con los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.

    Returns:
        Lista de errores en español; queda vacía si los datos son válidos.
    """
    errores: list[str] = []
    columnas_faltantes = [
        columna for columna in (col_trat, col_resp) if columna not in df.columns
    ]
    if columnas_faltantes:
        errores.append(
            "Faltan las columnas requeridas: " + ", ".join(columnas_faltantes) + "."
        )
        return errores

    if col_trat == col_resp:
        errores.append("La columna de tratamiento y la de respuesta deben ser distintas.")
        return errores

    # Se revisan solo las variables del modelo porque son las que intervienen en el análisis.
    if df[[col_trat, col_resp]].isna().any().any():
        errores.append("Hay datos faltantes en las columnas de tratamiento o respuesta.")

    # La respuesta debe ser cuantitativa para calcular medias y variación experimental.
    if not pd.api.types.is_numeric_dtype(df[col_resp]):
        errores.append(f"La respuesta '{col_resp}' debe contener datos numéricos.")

    # El efecto se compara entre niveles distintos; por eso se requiere k >= 2 tratamientos.
    cantidad_tratamientos = df[col_trat].nunique(dropna=True)
    if cantidad_tratamientos < 2:
        errores.append("El DCA debe incluir al menos dos tratamientos.")

    # Cada tratamiento necesita n_i >= 2 observaciones para estimar su variación.
    replicas = df[col_trat].value_counts(dropna=True)
    if not replicas.empty and (replicas < 2).any():
        errores.append("Cada tratamiento debe tener al menos dos réplicas.")

    return errores


def _exigir_datos_validos(df: pd.DataFrame, col_trat: str, col_resp: str) -> None:
    """Interrumpe el análisis cuando la validación del DCA encuentra errores.

    Args:
        df: Datos del experimento.
        col_trat: Nombre de la columna con los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.

    Raises:
        ValueError: Si uno o más requisitos del DCA no se cumplen.
    """
    errores = validar_dca(df, col_trat, col_resp)
    if errores:
        raise ValueError(" ".join(errores))


def ajustar_dca(
    df: pd.DataFrame, col_trat: str, col_resp: str
) -> RegressionResultsWrapper:
    """Ajusta el modelo lineal de un DCA de un factor.

    Args:
        df: Datos validados del experimento.
        col_trat: Nombre de la columna con los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.

    Returns:
        Modelo OLS ajustado.

    Raises:
        ValueError: Si los datos no cumplen los requisitos del DCA.
    """
    _exigir_datos_validos(df, col_trat, col_resp)

    # Q() protege nombres de columnas con espacios, tildes o símbolos en la fórmula.
    nombre_respuesta = json.dumps(col_resp, ensure_ascii=False)
    nombre_tratamiento = json.dumps(col_trat, ensure_ascii=False)
    formula = f"Q({nombre_respuesta}) ~ C(Q({nombre_tratamiento}))"

    # Modelo: Y_ij = mu + tau_i + epsilon_ij; en Patsy se expresa como Q(resp) ~ C(Q(trat)).
    return ols(formula, data=df).fit()


def tabla_anova(modelo: RegressionResultsWrapper) -> pd.DataFrame:
    """Construye la tabla ANOVA tipo II con fuentes y columnas en español.

    Args:
        modelo: Modelo OLS ajustado para un DCA de un factor.

    Returns:
        Tabla con las filas Tratamientos, Error y Total.
    """
    # La ANOVA tipo II separa la variación explicada por tratamientos del error.
    tabla_original = anova_lm(modelo, typ=2)
    fila_tratamientos = next(fila for fila in tabla_original.index if fila != "Residual")
    fila_error = tabla_original.loc["Residual"]
    fila_trat = tabla_original.loc[fila_tratamientos]

    # El cuadrado medio se calcula como CM = SC / gl para tratamientos y para el error.
    gl_trat = int(fila_trat["df"])
    sc_trat = float(fila_trat["sum_sq"])
    cm_trat = sc_trat / gl_trat if gl_trat else float("nan")
    gl_error = int(fila_error["df"])
    sc_error = float(fila_error["sum_sq"])
    cm_error = sc_error / gl_error if gl_error else float("nan")

    # El estadístico global sigue F = CM_tratamientos / CM_error.
    # Los totales son SC_total = SC_tratamientos + SC_error y gl_total = gl_tratamientos + gl_error.
    gl_total = gl_trat + gl_error
    sc_total = sc_trat + sc_error
    cm_total = sc_total / gl_total if gl_total else float("nan")

    return pd.DataFrame(
        [
            {
                "Fuente": "Tratamientos",
                "gl": gl_trat,
                "SC": sc_trat,
                "CM": cm_trat,
                "F": float(fila_trat["F"]),
                "p-valor": float(fila_trat["PR(>F)"]),
            },
            {
                "Fuente": "Error",
                "gl": gl_error,
                "SC": sc_error,
                "CM": cm_error,
                "F": float("nan"),
                "p-valor": float("nan"),
            },
            {
                "Fuente": "Total",
                "gl": gl_total,
                "SC": sc_total,
                "CM": cm_total,
                "F": float("nan"),
                "p-valor": float("nan"),
            },
        ],
        columns=["Fuente", "gl", "SC", "CM", "F", "p-valor"],
    )


def resumen_tratamientos(
    df: pd.DataFrame, col_trat: str, col_resp: str
) -> pd.DataFrame:
    """Resume tamaño de muestra y respuesta por tratamiento.

    Args:
        df: Datos del experimento.
        col_trat: Nombre de la columna con los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.

    Returns:
        DataFrame con n, total, media y desviación estándar por tratamiento.

    Raises:
        ValueError: Si los datos no cumplen los requisitos del DCA.
    """
    _exigir_datos_validos(df, col_trat, col_resp)

    # Para cada nivel: n = count(y), total = sum(y), media = total / n y
    # s = sqrt(sum((y - media)^2) / (n - 1)); s describe la variación entre réplicas.
    return (
        df.groupby(col_trat, as_index=False, sort=False, observed=True)[col_resp]
        .agg(
            n="count",
            total="sum",
            media="mean",
            **{"desviación estándar": "std"},
        )
    )


def coeficiente_variacion(
    modelo: RegressionResultsWrapper, df: pd.DataFrame, col_resp: str
) -> float:
    """Calcula el coeficiente de variación del DCA en porcentaje.

    Args:
        modelo: Modelo OLS ajustado para el DCA.
        df: Datos del experimento.
        col_resp: Nombre de la columna con la respuesta numérica.

    Returns:
        Coeficiente de variación calculado como porcentaje.

    Raises:
        ValueError: Si faltan datos o la media general es cero.
    """
    if col_resp not in df.columns or not pd.api.types.is_numeric_dtype(df[col_resp]):
        raise ValueError(f"La columna de respuesta '{col_resp}' debe existir y ser numérica.")
    if df[col_resp].isna().any():
        raise ValueError(f"La columna de respuesta '{col_resp}' contiene datos faltantes.")

    # CME se obtiene de la suma de cuadrados residual dividida por los grados de libertad del error.
    tabla_modelo = anova_lm(modelo, typ=2)
    fila_error = tabla_modelo.loc["Residual"]
    cme = float(fila_error["sum_sq"] / fila_error["df"])

    # El CV expresa el error experimental respecto a la media: CV = sqrt(CME) / media general * 100.
    media_general = float(df[col_resp].mean())
    if media_general == 0:
        raise ValueError("No se puede calcular el CV porque la media general es cero.")
    return float((cme**0.5 / media_general) * 100)


def tukey(
    df: pd.DataFrame,
    col_trat: str,
    col_resp: str,
    alfa: float = 0.05,
) -> tuple[pd.DataFrame, float]:
    """Realiza Tukey y calcula una diferencia mínima significativa.

    Args:
        df: Datos del experimento.
        col_trat: Nombre de la columna con los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.
        alfa: Nivel de significancia entre cero y uno.

    Returns:
        Tupla con comparaciones de Tukey en español y la DMS.

    Raises:
        ValueError: Si alfa no es válido o los datos no cumplen los requisitos del DCA.
    """
    _exigir_datos_validos(df, col_trat, col_resp)
    if not 0 < alfa < 1:
        raise ValueError("El nivel alfa debe estar entre 0 y 1.")

    # Tukey compara todas las parejas mediante el rango studentizado y controla el error familiar alfa.
    resultado = pairwise_tukeyhsd(
        endog=df[col_resp], groups=df[col_trat], alpha=alfa
    )
    datos_resumen = resultado.summary().data
    comparaciones = pd.DataFrame(datos_resumen[1:], columns=datos_resumen[0])
    comparaciones = comparaciones.rename(
        columns={
            "group1": "Tratamiento 1",
            "group2": "Tratamiento 2",
            "meandiff": "Diferencia de medias",
            "p-adj": "p-valor ajustado",
            "lower": "Límite inferior",
            "upper": "Límite superior",
            "reject": "Diferencia significativa",
        }
    )
    for columna in (
        "Diferencia de medias",
        "p-valor ajustado",
        "Límite inferior",
        "Límite superior",
    ):
        comparaciones[columna] = pd.to_numeric(comparaciones[columna])
    comparaciones["Diferencia significativa"] = comparaciones[
        "Diferencia significativa"
    ].map({True: True, False: False, "True": True, "False": False})

    conteos = df.groupby(col_trat, observed=True).size()
    cantidad_tratamientos = len(conteos)
    gl_error = len(df) - cantidad_tratamientos
    tabla_modelo = anova_lm(ols(
        f"Q({json.dumps(col_resp, ensure_ascii=False)}) ~ "
        f"C(Q({json.dumps(col_trat, ensure_ascii=False)}))",
        data=df,
    ).fit(), typ=2)
    cme = float(tabla_modelo.loc["Residual", "sum_sq"] / gl_error)

    # Con réplicas iguales r es el número común; con tamaños distintos se usa la media armónica.
    balanceado = bool((conteos == conteos.iloc[0]).all())
    if balanceado:
        replicas_efectivas = float(conteos.iloc[0])
    else:
        replicas_efectivas = float(cantidad_tratamientos / (1 / conteos).sum())
        warnings.warn(
            "El diseño no está balanceado; la DMS calculada con la media armónica "
            "de réplicas es aproximada.",
            UserWarning,
            stacklevel=2,
        )

    # El cuantil studentizado y el error estándar dan DMS = q(1 - alfa; k; glE) * sqrt(CME / r).
    cuantil = float(
        studentized_range.ppf(1 - alfa, cantidad_tratamientos, gl_error)
    )
    dms = cuantil * (cme / replicas_efectivas) ** 0.5
    return comparaciones, float(dms)


def interpretar_dca(tabla: pd.DataFrame, alfa: float = 0.05) -> str:
    """Interpreta la prueba global de tratamientos de la tabla ANOVA.

    Args:
        tabla: Tabla ANOVA con una fila llamada Tratamientos y columna p-valor.
        alfa: Nivel de significancia entre cero y uno.

    Returns:
        Explicación sencilla de la decisión sobre la hipótesis nula.

    Raises:
        ValueError: Si alfa no es válido o falta el resultado de tratamientos.
    """
    if not 0 < alfa < 1:
        raise ValueError("El nivel alfa debe estar entre 0 y 1.")
    if "Fuente" not in tabla.columns or "p-valor" not in tabla.columns:
        raise ValueError("La tabla debe incluir las columnas 'Fuente' y 'p-valor'.")

    fila_tratamientos = tabla.loc[tabla["Fuente"] == "Tratamientos", "p-valor"]
    if fila_tratamientos.empty or pd.isna(fila_tratamientos.iloc[0]):
        raise ValueError("La tabla no contiene un p-valor válido para Tratamientos.")

    # H0: mu_1 = ... = mu_k; se rechaza si p <= alfa, lo que indica evidencia de medias distintas.
    p_valor = float(fila_tratamientos.iloc[0])
    if p_valor <= alfa:
        return (
            f"Se rechaza H0 al nivel de significancia {alfa:g}: hay evidencia de que "
            "no todos los promedios de los tratamientos son iguales. Para decidir "
            "cuáles tratamientos difieren, revise las comparaciones de medias y los supuestos."
        )
    return (
        f"No se rechaza H0 al nivel de significancia {alfa:g}: no hay evidencia "
        "suficiente para afirmar que los promedios de los tratamientos difieren. "
        "Esto no demuestra que sean iguales; considere también los supuestos y el contexto del ensayo."
    )
