"""Gráfico de dos variables. Solo dibuja. El número lo calcula gran_m.py."""

from __future__ import annotations

TOL = 1e-7


def _cumple(x, y, restricciones):
    if x < -TOL or y < -TOL:
        return False
    for coefs, rel, b in restricciones:
        valor = coefs[0] * x + coefs[1] * y
        if rel == "<=" and valor > b + TOL:
            return False
        if rel == ">=" and valor < b - TOL:
            return False
        if rel == "=" and abs(valor - b) > 1e-6:
            return False
    return True


def _cruce(linea_a, linea_b):
    a1, b1, c1 = linea_a
    a2, b2, c2 = linea_b
    det = a1 * b2 - a2 * b1
    if abs(det) < 1e-12:
        return None
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return (x, y)


def _lineas(restricciones):
    lineas = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    for coefs, _, b in restricciones:
        lineas.append((float(coefs[0]), float(coefs[1]), float(b)))
    return lineas


def _vertices(restricciones):
    lineas = _lineas(restricciones)
    vistos = []
    for i in range(len(lineas)):
        for j in range(i + 1, len(lineas)):
            punto = _cruce(lineas[i], lineas[j])
            if punto is None or not _cumple(punto[0], punto[1], restricciones):
                continue
            if any(abs(punto[0] - p[0]) < 1e-6 and abs(punto[1] - p[1]) < 1e-6 for p in vistos):
                continue
            vistos.append(punto)
    return vistos


def _choca_con_caja(restricciones, lado):
    extra = list(restricciones) + [([1.0, 0.0], "<=", lado), ([0.0, 1.0], "<=", lado)]
    for punto in _vertices(extra):
        if (abs(punto[0] - lado) < 1e-5 or abs(punto[1] - lado) < 1e-5) and _cumple(
            punto[0], punto[1], restricciones
        ):
            return True
    return False


def _hull(puntos):
    unicos = sorted({(round(p[0], 8), round(p[1], 8)) for p in puntos})
    if len(unicos) <= 2:
        return unicos

    def cruz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    abajo = []
    for p in unicos:
        while len(abajo) >= 2 and cruz(abajo[-2], abajo[-1], p) <= 0:
            abajo.pop()
        abajo.append(p)
    arriba = []
    for p in reversed(unicos):
        while len(arriba) >= 2 and cruz(arriba[-2], arriba[-1], p) <= 0:
            arriba.pop()
        arriba.append(p)
    return abajo[:-1] + arriba[:-1]


def _area(poli):
    if len(poli) < 3:
        return 0.0
    total = 0.0
    for i, (x1, y1) in enumerate(poli):
        x2, y2 = poli[(i + 1) % len(poli)]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2


def _recortar(poli, a, b, d):
    if not poli:
        return []
    salida = []
    n = len(poli)
    for i in range(n):
        p = poli[i]
        q = poli[(i + 1) % n]
        pin = a * p[0] + b * p[1] <= d + 1e-8
        qin = a * q[0] + b * q[1] <= d + 1e-8
        if pin and qin:
            salida.append(q)
        elif pin and not qin:
            salida.append(_punto_corte(p, q, a, b, d))
        elif (not pin) and qin:
            salida.append(_punto_corte(p, q, a, b, d))
            salida.append(q)
    return salida


def _punto_corte(p, q, a, b, d):
    ap = a * p[0] + b * p[1]
    aq = a * q[0] + b * q[1]
    t = 0.0 if abs(aq - ap) < 1e-15 else (d - ap) / (aq - ap)
    return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))


def _sombrear_caja(restricciones, lado):
    poli = [(0.0, 0.0), (lado, 0.0), (lado, lado), (0.0, lado)]
    semiplanos = [(-1.0, 0.0, 0.0), (0.0, -1.0, 0.0)]
    for coefs, rel, b in restricciones:
        a, c = float(coefs[0]), float(coefs[1])
        rhs = float(b)
        if rel == "<=":
            semiplanos.append((a, c, rhs))
        elif rel == ">=":
            semiplanos.append((-a, -c, -rhs))
        else:
            semiplanos.append((a, c, rhs))
            semiplanos.append((-a, -c, -rhs))
    for a, c, rhs in semiplanos:
        poli = _recortar(poli, a, c, rhs)
    return poli


def analizar_region(restricciones):
    """Vértices factibles y si la región se sale de una caja grande."""
    if any(len(coefs) != 2 for coefs, _, _ in restricciones):
        raise ValueError("el gráfico pide dos variables")
    como_float = [([float(c) for c in coefs], rel, float(b)) for coefs, rel, b in restricciones]
    vertices = _vertices(como_float)
    mayor = 1.0
    for x, y in vertices:
        mayor = max(mayor, abs(x), abs(y))
    for _, _, b in como_float:
        mayor = max(mayor, abs(b))
    lado = mayor + 15
    acotada = not _choca_con_caja(como_float, lado)
    if acotada:
        poli = _hull(vertices)
        segmento = poli if _area(poli) <= 1e-6 and len(poli) >= 2 else None
        if segmento:
            poli_relleno = []
        else:
            poli_relleno = poli
    else:
        vista = max(8.0, mayor)
        poli_relleno = _sombrear_caja(como_float, vista)
        segmento = None
    return {
        "vertices": vertices,
        "poligono": poli_relleno,
        "segmento": segmento,
        "acotada": acotada,
        "vacia": not vertices and not poli_relleno,
    }


def _z_de(punto, c):
    return c[0] * punto[0] + c[1] * punto[1]


def figura(problema, resultado):
    import plotly.graph_objects as go

    if len(problema.c) != 2:
        return None
    region = analizar_region(problema.restricciones)
    c = [float(coef) for coef in problema.c]
    fig = go.Figure()
    extra = list(region["poligono"])
    todos = region["vertices"] + extra
    tope = max([1.0] + [max(abs(x), abs(y)) for x, y in todos]) * 1.25 + 1

    def segmento_recta(a, b, rhs):
        puntos = []
        candidatos = []
        if abs(b) > 1e-12:
            candidatos.append((0.0, rhs / b))
            candidatos.append((tope, (rhs - a * tope) / b))
        if abs(a) > 1e-12:
            candidatos.append((rhs / a, 0.0))
            candidatos.append(((rhs - b * tope) / a, tope))
        for x, y in candidatos:
            if -1e-6 <= x <= tope + 1e-6 and -1e-6 <= y <= tope + 1e-6:
                puntos.append((x, y))
        limpios = []
        for p in puntos:
            if not any(abs(p[0] - q[0]) < 1e-6 and abs(p[1] - q[1]) < 1e-6 for q in limpios):
                limpios.append(p)
        return limpios[:2]

    for i, (coefs, rel, b) in enumerate(problema.restricciones, start=1):
        extremos = segmento_recta(float(coefs[0]), float(coefs[1]), float(b))
        if len(extremos) < 2:
            continue
        partes = []
        for j, coef in enumerate(coefs):
            if coef == 0:
                continue
            partes.append(f"{coef} x{j + 1}")
        signo = {"<=": "≤", ">=": "≥", "=": "="}[rel]
        fig.add_trace(
            go.Scatter(
                x=[extremos[0][0], extremos[1][0]],
                y=[extremos[0][1], extremos[1][1]],
                mode="lines",
                name=f"R{i}: {' + '.join(partes)} {signo} {b}",
                line={"width": 2},
            )
        )

    if len(region["poligono"]) >= 3:
        px = [p[0] for p in region["poligono"]] + [region["poligono"][0][0]]
        py = [p[1] for p in region["poligono"]] + [region["poligono"][0][1]]
        fig.add_trace(
            go.Scatter(
                x=px,
                y=py,
                fill="toself",
                mode="lines",
                name="Región factible",
                fillcolor="rgba(31, 119, 80, 0.25)",
                line={"color": "rgba(31, 119, 80, 0.9)", "width": 1},
            )
        )
    if region["segmento"] and len(region["segmento"]) >= 2:
        fig.add_trace(
            go.Scatter(
                x=[p[0] for p in region["segmento"]],
                y=[p[1] for p in region["segmento"]],
                mode="lines",
                name="Región factible",
                line={"color": "rgb(31, 119, 80)", "width": 6},
            )
        )

    z_opt = None if resultado.z is None else float(resultado.z)
    optimos = []
    otros = []
    for punto in region["vertices"]:
        z_punto = _z_de(punto, c)
        if z_opt is not None and abs(z_punto - z_opt) < 1e-4:
            optimos.append((punto, z_punto))
        else:
            otros.append((punto, z_punto))

    if otros:
        fig.add_trace(
            go.Scatter(
                x=[p[0] for p, _ in otros],
                y=[p[1] for p, _ in otros],
                mode="markers+text",
                name="Vértices",
                text=[f"({p[0]:.4g}, {p[1]:.4g})<br>Z={z:.4g}" for p, z in otros],
                textposition="top center",
                marker={"size": 9, "color": "#1f4e79"},
            )
        )
    if optimos:
        fig.add_trace(
            go.Scatter(
                x=[p[0] for p, _ in optimos],
                y=[p[1] for p, _ in optimos],
                mode="markers+text",
                name="Óptimo",
                text=[f"óptimo ({p[0]:.4g}, {p[1]:.4g})<br>Z={z:.4g}" for p, z in optimos],
                textposition="bottom center",
                marker={"size": 14, "color": "#b45309", "symbol": "star"},
            )
        )
        if z_opt is not None and (abs(c[0]) > 1e-12 or abs(c[1]) > 1e-12):
            extremos = segmento_recta(c[0], c[1], z_opt)
            if len(extremos) == 2:
                fig.add_trace(
                    go.Scatter(
                        x=[extremos[0][0], extremos[1][0]],
                        y=[extremos[0][1], extremos[1][1]],
                        mode="lines",
                        name="Isoutilidad en el óptimo",
                        line={"color": "#b45309", "width": 2, "dash": "dash"},
                    )
                )

    titulo = "Región factible"
    if not region["acotada"]:
        titulo = "La región no está acotada"
    if region["vacia"]:
        titulo = "No hay región factible"
    fig.update_layout(
        title=titulo,
        template="plotly_white",
        legend={"orientation": "h", "y": -0.2},
        xaxis={"range": [-1, tope], "title": "x1"},
        yaxis={"range": [-1, tope], "title": "x2", "scaleanchor": "x", "scaleratio": 1},
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
    )
    return fig, region
