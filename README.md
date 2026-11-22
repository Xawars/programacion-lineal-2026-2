# Aplicación de programación lineal

Resuelve programas lineales con el método de la Gran M. La interfaz está hecha en Streamlit y el resultado lo calcula el código del repositorio. Si el problema tiene dos variables, Plotly dibuja la región. El gráfico no calcula el óptimo.

Sebastian Puerta y Victoria Giraldo. Optimización, 2026-2.

## Requisitos

Python 3.12. Las librerías están en `requirements.txt`.

## Instalación

Desde esta carpeta:

```bash
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

Se abre en el navegador. Se puede cargar uno de los ejemplos o escribir el problema: maximizar o minimizar, el número de variables, las restricciones y el lado derecho. Los coeficientes aceptan enteros y fracciones, como `2/5`.

Hay dos modos. La solución directa muestra las variables, Z, las holguras y los excesos. El paso a paso muestra la forma estándar, la variable que entra, la que sale, el pivote y el tablero de cada iteración.

Con dos variables aparece la región factible, los vértices y la recta de la función objetivo. Con tres o más, la pantalla avisa que el gráfico no aplica.

Si hay un óptimo, debajo quedan los precios sombra, los costos reducidos y el rango de cada coeficiente de Z y de cada lado derecho.

## Pruebas

```bash
python codigo/test_gran_m.py
```

Comprueba los problemas del enunciado.
