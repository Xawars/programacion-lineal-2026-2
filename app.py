"""Pantalla del Sprint 2. El número lo calcula codigo/gran_m.py."""

import streamlit as st
from codigo.grafico import figura
from codigo.gran_m import PRESETS, Problema, fraccion, resolver, texto_valor

st.set_page_config(page_title="Gran M", layout="wide")


def aplicar(preset):
    st.session_state.sentido_ui = "Maximizar" if preset["sentido"] == "max" else "Minimizar"
    st.session_state.n_vars = len(preset["c"])
    st.session_state.n_rest = len(preset["restricciones"])
    st.session_state.pista = preset["para_que"]
    for j, coef in enumerate(preset["c"]):
        st.session_state[f"c_{j}"] = str(coef)
    for i, (coefs, rel, b) in enumerate(preset["restricciones"]):
        for j, coef in enumerate(coefs):
            st.session_state[f"a_{i}_{j}"] = str(coef)
        for j in range(len(coefs), 8):
            st.session_state[f"a_{i}_{j}"] = "0"
        st.session_state[f"rel_{i}"] = rel
        st.session_state[f"b_{i}"] = str(b)
    st.session_state.resultado = None
    st.session_state.problema = None
    st.session_state.errores = []


def leer_numero(texto, etiqueta, errores):
    texto = (texto or "").strip()
    if texto == "":
        errores.append(f"{etiqueta} está vacío.")
        return None
    try:
        return fraccion(texto)
    except (ValueError, ZeroDivisionError):
        errores.append(f"{etiqueta} no es un número: «{texto}».")
        return None


def leer_problema():
    errores = []
    n = int(st.session_state.n_vars)
    m = int(st.session_state.n_rest)
    sentido = "max" if st.session_state.sentido_ui == "Maximizar" else "min"
    c = []
    for j in range(n):
        c.append(leer_numero(st.session_state.get(f"c_{j}", ""), f"C de x{j + 1}", errores))
    restricciones = []
    for i in range(m):
        coefs = []
        for j in range(n):
            coefs.append(
                leer_numero(st.session_state.get(f"a_{i}_{j}", ""), f"R{i + 1}, coeficiente de x{j + 1}", errores)
            )
        b = leer_numero(st.session_state.get(f"b_{i}", ""), f"lado derecho de R{i + 1}", errores)
        rel = st.session_state.get(f"rel_{i}", "<=")
        if coefs and b is not None and all(coef is not None for coef in coefs):
            restricciones.append((coefs, rel, b))
    if errores:
        return None, errores
    try:
        return Problema(sentido, c, restricciones), []
    except ValueError as exc:
        return None, [str(exc)]


def resolver_en_pantalla(modo):
    problema, errores = leer_problema()
    st.session_state.errores = errores
    st.session_state.modo = modo
    if errores:
        st.session_state.resultado = None
        st.session_state.problema = None
        return
    try:
        st.session_state.resultado = resolver(problema)
        st.session_state.problema = problema
        st.session_state.paso_idx = 0
    except ValueError as exc:
        st.session_state.errores = [str(exc)]
        st.session_state.resultado = None
        st.session_state.problema = None


def mostrar_solucion(resultado):
    if resultado.estado == "optimo":
        st.success(resultado.mensaje)
    elif resultado.estado == "infactible":
        st.error(resultado.mensaje)
    elif resultado.estado == "no_acotado":
        st.warning(resultado.mensaje)
    else:
        st.error(resultado.mensaje)

    if resultado.z is not None:
        etiqueta = "Z máxima" if resultado.sentido == "max" else "Z mínima"
        columnas = st.columns(len(resultado.grupos["x"]) + 1)
        for i, nombre in enumerate(resultado.grupos["x"]):
            columnas[i].metric(nombre, texto_valor(resultado.valores[nombre]))
        columnas[-1].metric(etiqueta, texto_valor(resultado.z))

    holguras = resultado.grupos["holgura"] + resultado.grupos["exceso"]
    if holguras:
        st.markdown("**Holguras y excesos**")
        cols = st.columns(min(4, len(holguras)))
        for i, nombre in enumerate(holguras):
            tipo = "holgura" if nombre.startswith("s") else "exceso"
            cols[i % len(cols)].metric(f"{nombre} ({tipo})", texto_valor(resultado.valores[nombre]))

    if resultado.grupos["artificial"]:
        vivas = [nombre for nombre in resultado.grupos["artificial"] if resultado.valores[nombre] != 0]
        if vivas:
            st.markdown("**Artificiales que no salieron**")
            st.write(", ".join(f"{nombre} = {texto_valor(resultado.valores[nombre])}" for nombre in vivas))
        elif resultado.estado == "optimo":
            st.caption("Las artificiales quedaron en 0. El problema sí era factible.")

    mostrar_sensibilidad(resultado)


def _de_a(piso, techo):
    izquierda = "sin límite" if piso is None else texto_valor(piso)
    derecha = "sin límite" if techo is None else texto_valor(techo)
    return f"{izquierda} a {derecha}"


def mostrar_sensibilidad(resultado):
    if resultado.sensibilidad is None:
        return
    st.markdown("**Sensibilidad**")
    st.caption("Sale del tablero final. Mientras el coeficiente se quede en el rango, la base no cambia.")
    st.markdown("**Precios sombra y rango de cada lado derecho**")
    st.dataframe(
        [
            {
                "restricción": f"R{item['restriccion']}",
                "precio sombra": texto_valor(item["precio"]),
                "b puede ir de": _de_a(item["piso"], item["techo"]),
                "lectura": item["frase"],
            }
            for item in resultado.sensibilidad["precios"]
        ],
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("**Costos reducidos y rango de cada coeficiente de Z**")
    st.dataframe(
        [
            {
                "variable": item["variable"],
                "costo reducido": texto_valor(item["costo"]),
                "coeficiente puede ir de": _de_a(item["piso"], item["techo"]),
                "lectura": item["frase"],
            }
            for item in resultado.sensibilidad["costos"]
        ],
        hide_index=True,
        use_container_width=True,
    )
    if resultado.alerta_multiple:
        st.caption("Hay otro óptimo. Por eso un costo reducido vale 0 y ese coeficiente no puede subir.")
    if resultado.alerta_degenerada:
        st.caption("Hay degeneración. Por eso un lado derecho queda justo en un extremo de su rango.")


def mostrar_paso(resultado):
    total = len(resultado.pasos) - 1
    indice = st.slider("Iteración", 0, total, key="paso_idx")
    paso = resultado.pasos[indice]
    st.markdown(f"**{paso.titulo}**")
    if indice == 0:
        st.markdown("**Forma estándar**")
        for linea in resultado.forma:
            st.write(linea)
        for nota in resultado.notas_forma:
            st.caption(nota)
    filas = []
    for i, fila in enumerate(paso.tablero[:-1]):
        filas.append({"básica": paso.basicas[i], **dict(zip(paso.nombres, fila))})
    filas.append({"básica": "Z", **dict(zip(paso.nombres, paso.tablero[-1]))})
    st.dataframe(filas, hide_index=True, use_container_width=True)
    if paso.entra and paso.sale:
        st.info(f"Entra {paso.entra}. Sale {paso.sale}. Pivote {paso.pivote}.")
        for linea in paso.razones:
            st.write(linea)
    elif paso.entra:
        st.warning(f"Entra {paso.entra}, pero ninguna fila tiene coeficiente positivo. No está acotado.")
        for linea in paso.razones:
            st.write(linea)
    if paso.nota:
        st.caption(paso.nota)


def mostrar_grafico(problema, resultado):
    if len(problema.c) != 2:
        st.info(
            f"Este problema tiene {len(problema.c)} variables. "
            "El método gráfico solo aplica con dos. El número de arriba sale del Gran M."
        )
        return
    fig, region = figura(problema, resultado)
    st.plotly_chart(fig, use_container_width=True)
    if region["vacia"]:
        st.warning("No hay puntos factibles para dibujar.")
    elif not region["acotada"]:
        st.warning("La región se sale del recuadro: el problema no está acotado en el plano.")
    elif region["segmento"]:
        st.caption("Con una igualdad, la región factible es un segmento, no un área.")


if "n_vars" not in st.session_state:
    aplicar(PRESETS[0])

st.markdown("## Programación lineal. Método de la Gran M")
st.caption("Sebastian Puerta y Victoria Giraldo, Optimización 2026-2, Sprint 2")

ejemplos = [preset["nombre"] for preset in PRESETS]
carga, boton = st.columns([3, 1])
with carga:
    elegido = st.selectbox("Ejemplo", ejemplos, index=0)
with boton:
    st.write("")
    st.write("")
    if st.button("Cargar ejemplo", type="primary"):
        preset = next(item for item in PRESETS if item["nombre"] == elegido)
        aplicar(preset)
        st.rerun()

if st.session_state.get("pista"):
    st.caption(st.session_state.pista)

st.radio("Objetivo", ["Maximizar", "Minimizar"], horizontal=True, key="sentido_ui")
c1, c2 = st.columns(2)
c1.number_input("Variables", min_value=1, max_value=8, step=1, key="n_vars")
c2.number_input("Restricciones", min_value=1, max_value=12, step=1, key="n_rest")

n = int(st.session_state.n_vars)
m = int(st.session_state.n_rest)

st.markdown("**Coeficientes de Z**")
cols_c = st.columns(n)
for j in range(n):
    clave = f"c_{j}"
    st.session_state.setdefault(clave, "0")
    cols_c[j].text_input(f"x{j + 1}", key=clave)

st.markdown("**Restricciones**")
for i in range(m):
    st.session_state.setdefault(f"rel_{i}", "<=")
    st.session_state.setdefault(f"b_{i}", "0")
    columnas = st.columns(n + 2)
    for j in range(n):
        clave = f"a_{i}_{j}"
        st.session_state.setdefault(clave, "0")
        columnas[j].text_input(f"R{i + 1} x{j + 1}", key=clave)
    columnas[n].selectbox(
        "Signo",
        ["<=", ">=", "="],
        key=f"rel_{i}",
        format_func=lambda s: {"<=": "≤", ">=": "≥", "=": "="}[s],
    )
    columnas[n + 1].text_input("b", key=f"b_{i}")

b1, b2 = st.columns(2)
if b1.button("Solución directa", type="primary"):
    resolver_en_pantalla("directo")
if b2.button("Paso a paso"):
    resolver_en_pantalla("pasos")

for error in st.session_state.get("errores") or []:
    st.error(error)

resultado = st.session_state.get("resultado")
problema = st.session_state.get("problema")
if resultado is not None and problema is not None:
    st.divider()
    if st.session_state.get("modo") == "pasos":
        mostrar_paso(resultado)
        st.divider()
        mostrar_solucion(resultado)
    else:
        mostrar_solucion(resultado)
    st.divider()
    mostrar_grafico(problema, resultado)
    st.caption("Plotly solo dibuja. El valor de Z sale del Gran M, no de la gráfica.")
