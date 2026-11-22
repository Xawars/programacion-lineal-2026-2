# Sprint 1 - Propuesta (12 nov 2026)

Equipo: Sebastian Puerta y Victoria Giraldo.  
Proyecto: aplicación de programación lineal con GUI (enunciado oficial en `enunciado/`).

## 1. Integrantes

| Nombre           | Rol tentativo                                        |
| ---------------- | ---------------------------------------------------- |
| Sebastian Puerta | Motor del método (Gran M) + sensibilidad             |
| Victoria Giraldo | GUI (Streamlit) + gráfico 2D + validación de entrada |

Ambos debemos poder explicar cualquier línea en la sustentación.

## 2. Lenguaje y plataforma

- **Lenguaje:** Python 3
- **GUI:** Streamlit (app local en el navegador)
- **Por qué:**
  - Ya lo usamos en el curso / es el stack más corto para formularios + tablas + gráficas.
  - Plotly entra para el método gráfico (n = 2). Lo recomendó el profesor en el feedback del Sprint 1 (12 nov). Solo dibuja; no resuelve.
  - No hay que montar backend/frontend aparte.
  - En sustentación se corre con `streamlit run app.py`.

Librerías de optimización (PuLP, scipy.optimize, OR-Tools) **solo para verificar** resultados. La solución que muestra la app sale del método propio.

## 3. Método

- **Elegido: Gran M** (método de la gran M / Big-M).
- **Por qué:**
  - Cubre max y min.
  - Maneja restricciones ≤, ≥ y = con holguras, excesos y artificiales en un solo flujo.
  - Es el que ya vimos en clase con tablero; se presta al modo **paso a paso** (entra, sale, pivote, tablero).
  - Simplex revisado también sirve, pero Gran M es más directo para los casos con ≥ y = del enunciado.

Fallback de verificación (no califica como solver): PuLP o scipy, detrás de un botón “Comparar con librería”.

## 4. Qué hace la app (alcance Sprint 1 → final)

| Requisito del PDF | Cómo lo cubrimos |
| --- | --- |
| Entrada Max/Min, n, m, A, b, C, tipo de restricción | Formulario Streamlit + validación (tamaños, signos, tipos) |
| Resolver directo | Corre Gran M y muestra Xi, Z, holguras/excesos |
| Resolver paso a paso | Muestra cada tablero: variables básicas, pivote, Z |
| Gráfico si n = 2 | Región factible, vértices, isoutilidad |
| Sensibilidad | Precios sombra, costos reducidos, rangos de C y de b |
| Casos especiales | Infactible, no acotado, óptimos múltiples, degenerado (mensaje claro) |

## 5. Boceto de interfaz

### Pantalla A - Entrada

```
┌─────────────────────────────────────────────────────────┐
│  Optimización PL. Gran M                                │
├─────────────────────────────────────────────────────────┤
│  Objetivo:  (•) Maximizar   ( ) Minimizar               │
│  n variables: [ 2 ]     m restricciones: [ 3 ]          │
│                                                         │
│  Coeficientes C:  [ 3 ] [ 5 ]                           │
│                                                         │
│  Restricciones:                                         │
│  #1  [ 1 ]x1 + [ 0 ]x2   [≤ ▾]   b = [ 4 ]              │
│  #2  [ 0 ]x1 + [ 2 ]x2   [≤ ▾]   b = [12 ]              │
│  #3  [ 3 ]x1 + [ 2 ]x2   [≤ ▾]   b = [18 ]              │
│                                                         │
│  [ Validar ]  [ Resolver ]  [ Paso a paso ]             │
└─────────────────────────────────────────────────────────┘
```

### Pantalla B - Resultados

```
┌──────────────────────┬──────────────────────────────────┐
│  Solución            │  Caso especial (si aplica)       │
│  x1 = …              │  (infactible / no acotado / …)   │
│  x2 = …              │                                  │
│  Z  = …              │  Holguras / excesos              │
│                      │  s1 = …   s2 = …                 │
└──────────────────────┴──────────────────────────────────┘
```

### Pantalla C - Paso a paso

```
┌─────────────────────────────────────────────────────────┐
│  Iteración 0 / 1 / 2 …   [< Anterior]  [Siguiente >]    │
│                                                         │
│  Tablero (tabla)                                        │
│  Entra: xj     Sale: si     Pivote: a_rs                │
│  Z parcial: …                                           │
└─────────────────────────────────────────────────────────┘
```

### Pantalla D - Gráfico (solo si n = 2)

```
┌─────────────────────────────────────────────────────────┐
│  Región factible sombreada                              │
│  Vértices etiquetados con Z                             │
│  Isoutilidad en el óptimo                               │
│  Si n > 2: mensaje “gráfico no aplica”                  │
└─────────────────────────────────────────────────────────┘
```

### Pantalla E - Sensibilidad

```
┌─────────────────────────────────────────────────────────┐
│  Precios sombra (por restricción)                       │
│  Costos reducidos (vars no básicas)                     │
│  Rango de C_j que mantiene optimalidad                  │
│  Rango de b_i que mantiene factibilidad                 │
└─────────────────────────────────────────────────────────┘
```

Flujo: **Entrada → Validar → (Resolver | Paso a paso) → Resultados + Gráfico + Sensibilidad**.

## 6. Plan corto hasta el Sprint 2 (26 nov)

1. Validación de entrada + estructura del modelo.
2. Gran M que resuelva los problemas 1 y 3 del PDF.
3. Vista de resultados + primer paso a paso (al menos tableros).
4. Gráfico 2D para el problema 1.
5. Sensibilidad básica (precios sombra) si alcanza; si no, en Sprint 3.

## 7. Repo

- URL: _pendiente (crear al empezar a codear)_
- Entrega final también: README, manual ≤ 5 pág, video ≤ 5 min (según PDF).

## 8. Notas para la socialización del 12 nov

Decir en una frase cada cosa:

1. “Vamos a hacer la app en **Python con Streamlit**.”
2. “El método propio es **Gran M**; librerías solo para verificar.”
3. “La interfaz tiene entrada, solución directa, paso a paso, gráfico en 2 variables y sensibilidad.”
