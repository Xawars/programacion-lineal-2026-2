"""Gran M para un problema lineal pequeño.

Maximizar o minimizar. Restricciones <=, >= o =. El lado derecho puede ser negativo.
La M y las artificiales solo aparecen si hay una >= o una =.
Los números del tablero son a + b*M, con fracciones exactas, para no perder la M
entre un float gigante.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction


class Num:
    """Número del tablero: parte normal + coeficiente de M."""

    def __init__(self, a=0, b=0):
        self.a = Fraction(a)
        self.b = Fraction(b)

    def es_cero(self):
        return self.a == 0 and self.b == 0

    def es_negativo(self):
        return self.b < 0 or (self.b == 0 and self.a < 0)

    def es_positivo(self):
        return self.b > 0 or (self.b == 0 and self.a > 0)

    def __add__(self, otro):
        return Num(self.a + otro.a, self.b + otro.b)

    def __sub__(self, otro):
        return Num(self.a - otro.a, self.b - otro.b)

    def __neg__(self):
        return Num(-self.a, -self.b)

    def __mul__(self, otro):
        if isinstance(otro, Num):
            if self.b != 0 and otro.b != 0:
                raise ValueError("en el tablero no se multiplica M por M")
            return Num(self.a * otro.a, self.a * otro.b + self.b * otro.a)
        factor = Fraction(otro)
        return Num(self.a * factor, self.b * factor)

    def __truediv__(self, otro):
        if isinstance(otro, Num):
            if otro.b != 0 or otro.a == 0:
                raise ValueError("solo se divide entre un número distinto de cero, sin M")
            return Num(self.a / otro.a, self.b / otro.a)
        return Num(self.a / Fraction(otro), self.b / Fraction(otro))

    def menor_que(self, otro):
        if self.b != otro.b:
            return self.b < otro.b
        return self.a < otro.a

    def igual(self, otro):
        return self.a == otro.a and self.b == otro.b


def fraccion(valor) -> Fraction:
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, str):
        return Fraction(valor)
    return Fraction(valor).limit_denominator(10**9)


def texto_num(n: Num) -> str:
    def pieza(x: Fraction) -> str:
        if x.denominator == 1:
            return str(x.numerator)
        return f"{x.numerator}/{x.denominator}"

    if n.b == 0:
        return pieza(n.a)
    if n.b == 1:
        parte_m = "M"
    elif n.b == -1:
        parte_m = "-M"
    else:
        parte_m = f"{pieza(n.b)}M"
    if n.a == 0:
        return parte_m
    if n.b > 0:
        return f"{pieza(n.a)}+{parte_m}"
    return f"{pieza(n.a)}{parte_m}"


def texto_valor(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    decimal = f"{float(x):.4f}".rstrip("0").rstrip(".")
    return f"{x.numerator}/{x.denominator} ({decimal})"


@dataclass
class Problema:
    sentido: str
    c: list[Fraction]
    restricciones: list[tuple[list[Fraction], str, Fraction]]

    def __post_init__(self):
        if self.sentido not in ("max", "min"):
            raise ValueError("el sentido tiene que ser max o min")
        self.c = [fraccion(x) for x in self.c]
        limpias = []
        for coefs, rel, b in self.restricciones:
            if rel not in ("<=", ">=", "="):
                raise ValueError(f"relación no válida: {rel}")
            coefs = [fraccion(x) for x in coefs]
            if len(coefs) != len(self.c):
                raise ValueError("una restricción no tiene tantas columnas como variables")
            limpias.append((coefs, rel, fraccion(b)))
        self.restricciones = limpias


@dataclass
class Paso:
    titulo: str
    basicas: list[str]
    nombres: list[str]
    tablero: list[list[str]]
    entra: str | None = None
    sale: str | None = None
    pivote: str | None = None
    razones: list[str] = field(default_factory=list)
    nota: str = ""


@dataclass
class Resultado:
    estado: str
    mensaje: str
    sentido: str
    valores: dict[str, Fraction]
    z: Fraction | None
    grupos: dict[str, list[str]]
    pasos: list[Paso]
    forma: list[str]
    notas_forma: list[str]
    alerta_multiple: str | None = None
    alerta_degenerada: str | None = None
    variables_multiples: list[str] = field(default_factory=list)
    sensibilidad: dict | None = None


def _ecuacion(terminos):
    partes = []
    for k, (coef, nombre) in enumerate(terminos):
        if coef == 1 or coef == -1:
            cuerpo = nombre
        else:
            cuerpo = f"{texto_valor(abs(coef))} {nombre}"
        if k == 0:
            partes.append(f"- {cuerpo}" if coef < 0 else cuerpo)
        else:
            partes.append(f"+ {cuerpo}" if coef > 0 else f"- {cuerpo}")
    return " ".join(partes) if partes else "0"


def _copiar(tablero):
    return [[Num(celda.a, celda.b) for celda in fila] for fila in tablero]


def _texto_tablero(tablero):
    return [[texto_num(celda) for celda in fila] for fila in tablero]


def construir(problema: Problema):
    """Pasa el problema a igualdades y arma el tablero inicial, ya con la M limpiada."""
    n = len(problema.c)
    c_max = problema.c if problema.sentido == "max" else [-c for c in problema.c]
    notas = []
    if problema.sentido == "min":
        notas.append(
            "El problema pide minimizar. Minimizar Z es maximizar -Z. "
            "Al final se cambia el signo de la Z del tablero."
        )

    normas = []
    volteada = []
    for i, (coefs, rel, b) in enumerate(problema.restricciones, start=1):
        dio_vuelta = False
        if b < 0:
            coefs = [-x for x in coefs]
            b = -b
            rel = {"<=": ">=", ">=": "<=", "=": "="}[rel]
            dio_vuelta = True
            notas.append(
                f"Restricción {i}: el lado derecho era negativo. "
                f"Se multiplicó toda la fila por -1 y el signo quedó {rel}."
            )
        if all(c == 0 for c in coefs):
            raise ValueError(f"la restricción {i} no usa ninguna variable")
        normas.append((coefs, rel, b))
        volteada.append(dio_vuelta)

    meta = []
    for i, (_, rel, _) in enumerate(normas):
        if rel == "<=":
            meta.append((i, "holgura", f"s{i + 1}"))
        elif rel == ">=":
            meta.append((i, "exceso", f"e{i + 1}"))
            meta.append((i, "artificial", f"a{i + 1}"))
        else:
            meta.append((i, "artificial", f"a{i + 1}"))

    nombres = [f"x{j + 1}" for j in range(n)] + [nombre for _, _, nombre in meta]
    m = len(normas)
    n_cols = len(nombres)
    tablero = []
    for coefs, _, b in normas:
        fila = [Num(0) for _ in range(n_cols + 1)]
        for j, coef in enumerate(coefs):
            fila[j] = Num(coef)
        fila[-1] = Num(b)
        tablero.append(fila)

    basicas = [""] * m
    col_inicial = [None] * m
    grupos = {
        "x": [f"x{j + 1}" for j in range(n)],
        "holgura": [],
        "exceso": [],
        "artificial": [],
    }
    for col, (i, kind, nombre) in enumerate(meta, start=n):
        tablero[i][col] = Num(-1 if kind == "exceso" else 1)
        grupos[kind].append(nombre)
        if kind != "exceso":
            basicas[i] = nombre
            col_inicial[i] = col

    z = [Num(0) for _ in range(n_cols + 1)]
    for j, coef in enumerate(c_max):
        z[j] = Num(-coef)
    for col, (_, kind, _) in enumerate(meta, start=n):
        if kind == "artificial":
            z[col] = Num(0, 1)
    for col, (i, kind, _) in enumerate(meta, start=n):
        if kind == "artificial":
            z = [z[j] - tablero[i][j] * Num(0, 1) for j in range(n_cols + 1)]
    tablero.append(z)

    forma = []
    for i, (coefs, rel, b) in enumerate(normas):
        terminos = []
        for j, coef in enumerate(coefs):
            if coef != 0:
                terminos.append((coef, f"x{j + 1}"))
        for fila, kind, nombre in meta:
            if fila != i:
                continue
            terminos.append((-1 if kind == "exceso" else 1, nombre))
        forma.append(f"R{i + 1}: {_ecuacion(terminos)} = {texto_valor(b)}")

    objetivo = []
    for j, coef in enumerate(c_max):
        if coef != 0:
            objetivo.append((coef, f"x{j + 1}"))
    for _, kind, nombre in meta:
        if kind == "artificial":
            objetivo.append((-1, f"M {nombre}"))
    forma.append("Se maximiza " + _ecuacion(objetivo))
    if grupos["artificial"]:
        notas.append(
            "Cada igualdad o mayor-o-igual necesita una artificial para arrancar. "
            "La M es un castigo enorme: se le resta M veces cada artificial a la función "
            "que se maximiza, y antes del primer pivote se limpia la M de las columnas básicas."
        )
    else:
        notas.append(
            "Todas las restricciones quedaron como menor-o-igual. "
            "Bastan holguras. En este problema la M no aparece."
        )
    return tablero, basicas, nombres, grupos, forma, notas, col_inicial, volteada


def columna_que_entra(tablero):
    fila_z = tablero[-1][:-1]
    col = 0
    empate = False
    for j in range(1, len(fila_z)):
        if fila_z[j].igual(fila_z[col]):
            empate = True
            continue
        if fila_z[j].menor_que(fila_z[col]):
            col = j
            empate = False
    if not fila_z[col].es_negativo():
        return None, False
    return col, empate


def fila_que_sale(tablero, col):
    mejor = None
    empates = []
    for i, fila in enumerate(tablero[:-1]):
        if not fila[col].es_positivo():
            continue
        razon = fila[-1].a / fila[col].a
        if mejor is None or razon < mejor[0]:
            mejor = (razon, i)
            empates = [i]
        elif razon == mejor[0]:
            empates.append(i)
    if mejor is None:
        return None, []
    return mejor[1], empates


def pivotear(tablero, fila, col):
    pivote = tablero[fila][col]
    tablero[fila] = [celda / pivote for celda in tablero[fila]]
    for i, otra in enumerate(tablero):
        if i == fila:
            continue
        factor = otra[col]
        tablero[i] = [celda - factor * tablero[fila][j] for j, celda in enumerate(otra)]


def _limites(z, a):
    """z + delta * a >= 0. Devuelve el menor y el mayor delta que lo cumplen."""
    if a == 0:
        if z < 0:
            return Fraction(1), Fraction(0)
        return None, None
    limite = -z / a
    if a > 0:
        return limite, None
    return None, limite


def _apretar(bajo, alto, nuevo_bajo, nuevo_alto):
    if nuevo_bajo is not None and (bajo is None or nuevo_bajo > bajo):
        bajo = nuevo_bajo
    if nuevo_alto is not None and (alto is None or nuevo_alto < alto):
        alto = nuevo_alto
    return bajo, alto


def _a_coeficiente(actual, bajo, alto, invertir):
    if invertir:
        bajo, alto = (None if alto is None else -alto), (None if bajo is None else -bajo)
    return (
        None if bajo is None else actual + bajo,
        None if alto is None else actual + alto,
    )


def _rango_c(tablero, basicas, nombres, fila, col, z_propio):
    bajo, alto = None, None
    if fila is None:
        return _limites(z_propio, -1)
    for j, nombre in enumerate(nombres):
        if nombre in basicas:
            continue
        celda_z = tablero[-1][j]
        if celda_z.b != 0:
            continue
        bajo, alto = _apretar(bajo, alto, *_limites(celda_z.a, tablero[fila][j].a))
    return bajo, alto


def _rango_b(tablero, basicas, col):
    bajo, alto = None, None
    for i, _basica in enumerate(basicas):
        bajo, alto = _apretar(bajo, alto, *_limites(tablero[i][-1].a, tablero[i][col].a))
    return bajo, alto


def calcular_sensibilidad(problema, tablero, basicas, nombres, col_inicial, volteada):
    """Precios sombra, costos reducidos y rangos, leídos del tablero óptimo."""
    c_max = problema.c if problema.sentido == "max" else [-c for c in problema.c]
    coef_base = []
    for basica in basicas:
        if basica.startswith("x"):
            coef_base.append(c_max[int(basica[1:]) - 1])
        else:
            coef_base.append(Fraction(0))

    signo_z = 1 if problema.sentido == "max" else -1
    precios = []
    for i, col in enumerate(col_inicial):
        y = sum(coef_base[r] * tablero[r][col].a for r in range(len(basicas)))
        precio = signo_z * (-y if volteada[i] else y)
        if precio == 0:
            frase = "Si el lado derecho sube en 1, Z no cambia."
        elif precio > 0:
            frase = f"Si el lado derecho sube en 1, Z sube {texto_valor(precio)}."
        else:
            frase = f"Si el lado derecho sube en 1, Z baja {texto_valor(-precio)}."
        bajo, alto = _rango_b(tablero, basicas, col)
        piso, techo = _a_coeficiente(problema.restricciones[i][2], bajo, alto, volteada[i])
        precios.append({"restriccion": i + 1, "precio": precio, "frase": frase, "piso": piso, "techo": techo})

    costos = []
    en_base = {nombre: i for i, nombre in enumerate(basicas)}
    for j, nombre in enumerate(nombres):
        if not nombre.startswith("x"):
            continue
        indice = int(nombre[1:]) - 1
        if nombre in en_base:
            cambio = Fraction(0)
            frase = "Está en la base. Su costo reducido es 0."
            bajo, alto = _rango_c(tablero, basicas, nombres, en_base[nombre], j, Fraction(0))
        else:
            cambio = signo_z * (-tablero[-1][j].a)
            if cambio == 0:
                frase = "No está en la base, pero puede entrar sin cambiar Z."
            elif cambio < 0:
                frase = f"Si se obliga a subir 1, Z baja {texto_valor(-cambio)}."
            else:
                frase = f"Si se obliga a subir 1, Z sube {texto_valor(cambio)}."
            bajo, alto = _rango_c(tablero, basicas, nombres, None, j, tablero[-1][j].a)
        piso, techo = _a_coeficiente(problema.c[indice], bajo, alto, problema.sentido == "min")
        costos.append(
            {
                "variable": nombre,
                "costo": cambio,
                "frase": frase,
                "piso": piso,
                "techo": techo,
            }
        )
    return {"precios": precios, "costos": costos}


def _razon_texto(tablero, basicas, col, entra):
    lineas = []
    for i, fila in enumerate(tablero[:-1]):
        if not fila[col].es_positivo():
            lineas.append(f"{basicas[i]}: no limita. En la columna de {entra} el coeficiente no es positivo.")
            continue
        razon = fila[-1].a / fila[col].a
        lineas.append(
            f"{basicas[i]}: {texto_num(fila[-1])} / {texto_num(fila[col])} = {texto_valor(razon)}"
        )
    return lineas


def resolver(problema: Problema) -> Resultado:
    tablero, basicas, nombres, grupos, forma, notas, col_inicial, volteada = construir(problema)
    pasos = []
    degenerada = False
    notas_degenerada = []
    estado = "optimo"
    mensaje = ""
    tope = 40

    for k in range(tope + 1):
        col, empate_entra = columna_que_entra(tablero)
        nota = ""
        entra = sale = pivote = None
        razones = []
        if col is None:
            nota = "En la fila Z ya no hay negativos. El tablero está en el óptimo de lo que se está maximizando."
        else:
            entra = nombres[col]
            if empate_entra:
                nota = "Hay empate en quién entra. Se elige la columna de más a la izquierda."
            razones = _razon_texto(tablero, basicas, col, entra)
            fila, empates = fila_que_sale(tablero, col)
            if fila is None:
                estado = "no_acotado"
                mensaje = (
                    f"La variable {entra} quiere entrar, pero ningún renglón la limita. "
                    "La solución no está acotada: Z puede crecer sin fin."
                )
                nota = mensaje
            else:
                sale = basicas[fila]
                pivote = texto_num(tablero[fila][col])
                if len(empates) > 1:
                    degenerada = True
                    nombres_empate = ", ".join(basicas[i] for i in empates)
                    notas_degenerada.append(f"empate al salir entre {nombres_empate}")
                    extra = f" Empate en la razón mínima entre {nombres_empate}. Se elige {sale}. Hay degeneración."
                    nota = (nota + extra).strip()
        pasos.append(
            Paso(
                titulo="Tablero inicial" if k == 0 else f"Después del pivote {k}",
                basicas=list(basicas),
                nombres=nombres + ["b"],
                tablero=_texto_tablero(tablero),
                entra=entra,
                sale=sale,
                pivote=pivote,
                razones=razones,
                nota=nota,
            )
        )
        if col is None or estado == "no_acotado":
            break
        if k == tope:
            estado = "ciclo"
            mensaje = "El método no paró en el límite de iteraciones. Revisa si hay un ciclo."
            break
        basicas[fila] = entra
        pivotear(tablero, fila, col)

    valores = {nombre: Fraction(0) for nombre in nombres}
    for i, basica in enumerate(basicas):
        valores[basica] = tablero[i][-1].a

    z_tablero = tablero[-1][-1]
    artificial_viva = [
        nombre
        for nombre in grupos["artificial"]
        if valores[nombre] > 0
    ]
    if estado == "optimo" and (artificial_viva or z_tablero.b != 0):
        estado = "infactible"
        cuales = ", ".join(f"{nombre} = {texto_valor(valores[nombre])}" for nombre in artificial_viva)
        mensaje = (
            "No hay solución factible. Al terminar, todavía queda una artificial en la base"
            + (f" ({cuales})" if cuales else "")
            + ". Esa variable no existe en el problema real: solo servía para arrancar."
        )
        pasos[-1].nota = mensaje

    z = None
    alerta_multiple = None
    multiples = []
    if estado == "optimo":
        z = z_tablero.a if problema.sentido == "max" else -z_tablero.a
        basicas_en_cero = [b for b in basicas if valores[b] == 0]
        if basicas_en_cero:
            degenerada = True
            notas_degenerada.append(
                "básica en cero: " + ", ".join(basicas_en_cero)
            )
        no_basicas = [nombre for nombre in nombres if nombre not in basicas and nombre not in grupos["artificial"]]
        fila_z = tablero[-1]
        for j, nombre in enumerate(nombres):
            if nombre in no_basicas and fila_z[j].es_cero():
                multiples.append(nombre)
        if multiples:
            alerta_multiple = (
                "Hay más de una solución óptima. "
                + ", ".join(multiples)
                + " no está en la base y tiene 0 en la fila Z: puede entrar sin cambiar Z."
            )
        mensaje = f"Óptimo encontrado. Z = {texto_valor(z)}."
        if alerta_multiple:
            mensaje += " " + alerta_multiple

    alerta_degenerada = None
    if degenerada and estado == "optimo":
        alerta_degenerada = "El problema es degenerado (" + "; ".join(notas_degenerada) + ")."
        mensaje += " " + alerta_degenerada

    if estado == "no_acotado":
        z = None

    sensibilidad = None
    if estado == "optimo":
        sensibilidad = calcular_sensibilidad(problema, tablero, basicas, nombres, col_inicial, volteada)

    return Resultado(
        estado=estado,
        mensaje=mensaje,
        sentido=problema.sentido,
        valores=valores,
        z=z,
        grupos=grupos,
        pasos=pasos,
        forma=forma,
        notas_forma=notas,
        alerta_multiple=alerta_multiple,
        alerta_degenerada=alerta_degenerada,
        variables_multiples=multiples,
        sensibilidad=sensibilidad,
    )


def problema_de_listas(sentido, c, restricciones) -> Problema:
    return Problema(sentido, c, restricciones)


PRESETS = [
    {
        "nombre": "Problema 1",
        "sentido": "max",
        "c": ["50", "80"],
        "restricciones": [
            (["2", "1"], "<=", "100"),
            (["1", "3"], "<=", "90"),
            (["0", "1"], "<=", "40"),
        ],
        "para_que": "Forma estándar y gráfico. La tercera restricción sobra.",
    },
    {
        "nombre": "Problema 2",
        "sentido": "min",
        "c": ["4", "1"],
        "restricciones": [
            (["3", "1"], "=", "3"),
            (["4", "3"], ">=", "6"),
            (["-1", "-2"], ">=", "-4"),
        ],
        "para_que": "Minimización, igualdad, mayor-o-igual, lado derecho negativo y artificiales.",
    },
    {
        "nombre": "Problema 3",
        "sentido": "max",
        "c": ["3", "2", "5"],
        "restricciones": [
            (["1", "2", "1"], "<=", "430"),
            (["3", "0", "2"], "<=", "460"),
            (["1", "4", "0"], "<=", "420"),
        ],
        "para_que": "Tres variables. El gráfico no aplica.",
    },
    {
        "nombre": "Problema 4",
        "sentido": "max",
        "c": ["1", "1"],
        "restricciones": [
            (["1", "1"], "<=", "2"),
            (["1", "1"], ">=", "5"),
        ],
        "para_que": "Infactible.",
    },
    {
        "nombre": "Problema 5",
        "sentido": "max",
        "c": ["1", "1"],
        "restricciones": [
            (["1", "-1"], "<=", "1"),
            (["-1", "1"], "<=", "2"),
        ],
        "para_que": "No acotado.",
    },
    {
        "nombre": "Problema 6",
        "sentido": "max",
        "c": ["2", "4"],
        "restricciones": [
            (["1", "2"], "<=", "5"),
            (["1", "1"], "<=", "4"),
        ],
        "para_que": "Óptimos múltiples. Z = 10 en todo un segmento.",
    },
    {
        "nombre": "Problema 7",
        "sentido": "max",
        "c": ["3", "9"],
        "restricciones": [
            (["1", "4"], "<=", "8"),
            (["1", "2"], "<=", "4"),
        ],
        "para_que": "Degeneración: una básica queda en cero.",
    },
    {
        "nombre": "Wyndor",
        "sentido": "max",
        "c": ["3", "5"],
        "restricciones": [
            (["1", "0"], "<=", "4"),
            (["0", "2"], "<=", "12"),
            (["3", "2"], "<=", "18"),
        ],
        "para_que": "El ejemplo de las dos plantas. x1 = 2, x2 = 6, Z = 36.",
    },
    {
        "nombre": "Ejemplo de clase",
        "sentido": "min",
        "c": ["2/5", "1/2"],
        "restricciones": [
            (["3/10", "1/10"], "<=", "27/10"),
            (["1/2", "1/2"], "=", "6"),
            (["3/5", "2/5"], ">=", "6"),
        ],
        "para_que": "El de la clase del 20 oct: X1 = 7.5, X2 = 4.5, Z mín = 5.25.",
    },
]


def cargar_preset(nombre: str) -> Problema:
    for preset in PRESETS:
        if preset["nombre"] == nombre:
            return problema_de_listas(preset["sentido"], preset["c"], preset["restricciones"])
    raise KeyError(nombre)
