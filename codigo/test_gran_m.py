"""Comprueba los 7 problemas del enunciado, Wyndor y el ejemplo de clase."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fractions import Fraction

from grafico import analizar_region
from gran_m import Problema, cargar_preset, resolver, texto_valor


def casi(valor, esperado):
    return abs(float(valor) - esperado) < 1e-6


def revisar(nombre, esperados, z, estado="optimo"):
    r = cargar_preset(nombre)
    res = resolver(r)
    assert res.estado == estado, (nombre, res.estado, res.mensaje)
    if z is not None:
        assert casi(res.z, z), (nombre, texto_valor(res.z), z)
    for var, esperado in esperados.items():
        assert casi(res.valores[var], esperado), (nombre, var, texto_valor(res.valores[var]), esperado)
    print(f"\n== {nombre}: {res.mensaje}")
    for paso in res.pasos:
        movimiento = ""
        if paso.entra and paso.sale:
            movimiento = f" | entra {paso.entra}, sale {paso.sale}, pivote {paso.pivote}"
        elif paso.entra and not paso.sale:
            movimiento = f" | entra {paso.entra}, nadie sale"
        print(f"  {paso.titulo}{movimiento}")
    return res


def test_todos():
    revisar("Wyndor", {"x1": 2, "x2": 6}, 36)
    revisar("Problema 1", {"x1": 42, "x2": 16}, 3380)
    revisar("Problema 2", {"x1": 0.4, "x2": 1.8}, 3.4)
    revisar("Problema 3", {"x1": 0, "x2": 100, "x3": 230}, 1350)
    revisar("Problema 4", {}, None, "infactible")
    revisar("Problema 5", {}, None, "no_acotado")
    res6 = revisar("Problema 6", {}, 10)
    assert res6.alerta_multiple, res6.mensaje
    res7 = revisar("Problema 7", {"x1": 0, "x2": 2}, 18)
    assert res7.alerta_degenerada, res7.mensaje
    revisar("Ejemplo de clase", {"x1": 7.5, "x2": 4.5}, 5.25)

    region = analizar_region(cargar_preset("Problema 1").restricciones)
    assert region["acotada"]
    pares = {(round(x, 4), round(y, 4)) for x, y in region["vertices"]}
    assert pares == {(0, 0), (50, 0), (42, 16), (0, 30)}, pares

    region5 = analizar_region(cargar_preset("Problema 5").restricciones)
    assert not region5["acotada"]

    region2 = analizar_region(cargar_preset("Problema 2").restricciones)
    assert region2["acotada"]
    assert len(region2["vertices"]) == 2, region2["vertices"]
    print("\nGráfico: problema 1 tiene los 4 vértices. Problema 5 no está acotado. Problema 2 es un segmento.")


def _con_cambio(problema, i_b=None, delta_b=0, i_c=None, delta_c=0):
    restricciones = [
        (coefs, rel, b + (delta_b if k == i_b else 0))
        for k, (coefs, rel, b) in enumerate(problema.restricciones)
    ]
    coeficientes = [coef + (delta_c if k == i_c else 0) for k, coef in enumerate(problema.c)]
    return Problema(problema.sentido, coeficientes, restricciones)


def _pasos_interiores(actual, piso, techo):
    bajo = None if piso is None else piso - actual
    alto = None if techo is None else techo - actual
    pasos = []
    if alto is None or alto > 0:
        paso = Fraction(1, 5) if alto is None else min(Fraction(1, 5), alto / 2)
        if paso > 0:
            pasos.append(paso)
    if bajo is None or bajo < 0:
        paso = Fraction(-1, 5) if bajo is None else max(Fraction(-1, 5), bajo / 2)
        if paso < 0:
            pasos.append(paso)
    return pasos


def test_sensibilidad():
    wyndor = resolver(cargar_preset("Wyndor"))
    precios = [item["precio"] for item in wyndor.sensibilidad["precios"]]
    assert precios == [0, Fraction(3, 2), 1], precios

    for nombre in (
        "Wyndor",
        "Problema 1",
        "Problema 2",
        "Problema 3",
        "Problema 6",
        "Problema 7",
        "Ejemplo de clase",
    ):
        problema = cargar_preset(nombre)
        base = resolver(problema)
        assert base.sensibilidad is not None, nombre
        for i, item in enumerate(base.sensibilidad["precios"]):
            for delta in _pasos_interiores(problema.restricciones[i][2], item["piso"], item["techo"]):
                nuevo = resolver(_con_cambio(problema, i_b=i, delta_b=delta))
                assert nuevo.estado == "optimo", (nombre, i, delta, nuevo.estado)
                assert nuevo.z - base.z == item["precio"] * delta, (nombre, "b", i, delta)
        for j, item in enumerate(base.sensibilidad["costos"]):
            for delta in _pasos_interiores(problema.c[j], item["piso"], item["techo"]):
                nuevo = resolver(_con_cambio(problema, i_c=j, delta_c=delta))
                assert nuevo.estado == "optimo", (nombre, item["variable"], delta)
                assert nuevo.z == base.z + delta * base.valores[f"x{j + 1}"], (nombre, item["variable"], delta)
                for k in range(len(problema.c)):
                    assert nuevo.valores[f"x{k + 1}"] == base.valores[f"x{k + 1}"], (nombre, item["variable"], delta)

    multiple = resolver(cargar_preset("Problema 6"))
    x1 = next(item for item in multiple.sensibilidad["costos"] if item["variable"] == "x1")
    assert x1["costo"] == 0
    assert x1["techo"] == 2

    assert resolver(cargar_preset("Problema 4")).sensibilidad is None
    assert resolver(cargar_preset("Problema 5")).sensibilidad is None
    print("\nSensibilidad: Wyndor da 0, 3/2 y 1. Los rangos coinciden al volver a resolver.")


if __name__ == "__main__":
    test_todos()
    test_sensibilidad()
    print("\nTodo coincidió.")
