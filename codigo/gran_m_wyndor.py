"""
Gran M, primer caso: Wyndor.

Maximizar Z = 3 x1 + 5 x2
    x1          <= 4
         2 x2   <= 12
    3 x1 + 2 x2 <= 18
    x1, x2 >= 0

Óptimo conocido: x1 = 2, x2 = 6, Z = 36.

Wyndor solo tiene <=. En ese caso no hace falta variable artificial
ni la M: basta una holgura por restricción. La M entra cuando haya
una >= o una =.
"""

# Columnas del tablero: x1, x2, s1, s2, s3 y el lado derecho.
# La fila Z guarda -3 y -5. El que entra es el número más negativo,
# porque estamos maximizando.
NOMBRES = ["x1", "x2", "s1", "s2", "s3", "b"]
basicas = ["s1", "s2", "s3"]
tablero = [
    [1, 0, 1, 0, 0, 4],
    [0, 2, 0, 1, 0, 12],
    [3, 2, 0, 0, 1, 18],
    [-3, -5, 0, 0, 0, 0],
]


def mostrar(paso):
    print(f"\n--- {paso} ---")
    print("básica  " + "  ".join(f"{nombre:>6}" for nombre in NOMBRES))
    for i, fila in enumerate(tablero[:-1]):
        nums = "  ".join(f"{valor:6.2f}" for valor in fila)
        print(f"{basicas[i]:<6}  {nums}")
    nums = "  ".join(f"{valor:6.2f}" for valor in tablero[-1])
    print(f"{'Z':<6}  {nums}")


def columna_que_entra():
    fila_z = tablero[-1][:-1]
    col = min(range(len(fila_z)), key=lambda j: fila_z[j])
    if fila_z[col] >= -1e-9:
        return None
    return col


def fila_que_sale(col):
    mejor = None
    for i, fila in enumerate(tablero[:-1]):
        if fila[col] <= 1e-9:
            continue
        razon = fila[-1] / fila[col]
        if mejor is None or razon < mejor[0]:
            mejor = (razon, i)
    return None if mejor is None else mejor[1]


def pivotear(fila, col):
    pivote = tablero[fila][col]
    tablero[fila] = [valor / pivote for valor in tablero[fila]]
    for i, otra in enumerate(tablero):
        if i == fila:
            continue
        factor = otra[col]
        tablero[i] = [valor - factor * tablero[fila][j] for j, valor in enumerate(otra)]


def resolver():
    mostrar("inicio")
    paso = 0
    while True:
        col = columna_que_entra()
        if col is None:
            break
        fila = fila_que_sale(col)
        if fila is None:
            raise SystemExit("el problema no está acotado")
        print(f"\nentra {NOMBRES[col]}, sale {basicas[fila]}")
        basicas[fila] = NOMBRES[col]
        pivotear(fila, col)
        paso += 1
        mostrar(f"paso {paso}")

    valores = {nombre: 0.0 for nombre in NOMBRES if nombre != "b"}
    for i, basica in enumerate(basicas):
        valores[basica] = tablero[i][-1]
    return valores["x1"], valores["x2"], tablero[-1][-1]


if __name__ == "__main__":
    x1, x2, z = resolver()
    print(f"\nSolución: x1 = {x1:.2f}, x2 = {x2:.2f}, Z = {z:.2f}")
    print("Esperado: x1 = 2, x2 = 6, Z = 36")
    assert abs(x1 - 2) < 1e-6 and abs(x2 - 6) < 1e-6 and abs(z - 36) < 1e-6
