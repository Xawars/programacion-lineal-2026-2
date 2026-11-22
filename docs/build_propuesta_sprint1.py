"""Genera Propuesta_Sprint1_PL.pptx (solo Sprint 1)."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).parent
NAVY = RGBColor(0x14, 0x21, 0x3D)
TEAL = RGBColor(0x2A, 0x9D, 0x8F)
INK = RGBColor(0x22, 0x30, 0x3C)
GRAY = RGBColor(0x6B, 0x77, 0x85)
LIGHT = RGBColor(0xF5, 0xF7, 0xFA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xE1, 0xE6, 0xEC)
CARD = WHITE
FONT = "Segoe UI"
FONT_B = "Segoe UI Semibold"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = 13.333, 7.5


def fondo(s, color):
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = color


def caja(s, x, y, w, h, color, borde=None, forma=MSO_SHAPE.ROUNDED_RECTANGLE, radio=0.08):
    sh = s.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    if borde:
        sh.line.color.rgb = borde
        sh.line.width = Pt(1)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    if forma == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radio
    return sh


def texto(s, x, y, w, h, parrafos, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, p in enumerate(parrafos):
        if isinstance(p, str):
            p = (p, 18, INK, False)
        t, size, color, bold = p[:4]
        font = p[4] if len(p) > 4 else (FONT_B if bold else FONT)
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        para.space_after = Pt(size * 0.35)
        run = para.add_run()
        run.text = t
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.name = font
    return tb


def titulo(s, kicker, t, n):
    fondo(s, LIGHT)
    caja(s, 0, 0, 0.18, SH, TEAL, forma=MSO_SHAPE.RECTANGLE)
    texto(s, 0.7, 0.4, 11, 0.35, [(kicker.upper(), 12, TEAL, True)])
    texto(s, 0.7, 0.7, 12, 0.7, [(t, 30, NAVY, True)])
    texto(s, 12.3, 7.05, 0.8, 0.3, [(str(n), 11, GRAY, False)], align=PP_ALIGN.RIGHT)


def tarjeta(s, x, y, w, h, encabezado, cuerpo, acento=TEAL):
    caja(s, x, y, w, h, CARD, borde=LINE)
    caja(s, x, y, w, 0.08, acento, forma=MSO_SHAPE.RECTANGLE)
    texto(s, x + 0.25, y + 0.25, w - 0.5, 0.4, [(encabezado, 16, acento, True)])
    texto(s, x + 0.25, y + 0.7, w - 0.5, h - 0.9, [(c, 15, INK, False) for c in cuerpo])


# 1 Portada
s = prs.slides.add_slide(BLANK)
fondo(s, NAVY)
texto(s, 0.9, 1.7, 11, 0.4, [("OPTIMIZACIÓN, 2026-2", 14, TEAL, True)])
texto(s, 0.9, 2.2, 11, 1.6, [
    ("Propuesta Sprint 1", 44, WHITE, True),
    ("Aplicación de programación lineal", 24, RGBColor(0xAE, 0xB8, 0xC6), False),
])
texto(s, 0.9, 4.5, 11, 1.4, [
    ("Integrantes: Jhoan Sebastian Puerta Uribe, Carol Victoria", 17, WHITE, False),
    ("Universidad de Antioquia, Facultad de Ingeniería", 14, RGBColor(0xAE, 0xB8, 0xC6), False),)
    ("Fecha de socialización: 12 de noviembre de 2026", 14, RGBColor(0xAE, 0xB8, 0xC6), False),
])

# 2 Decisiones
s = prs.slides.add_slide(BLANK)
titulo(s, "Decisiones del equipo", "Lenguaje, plataforma y método", 2)
tarjeta(s, 0.7, 1.8, 3.9, 4.4, "Lenguaje", [
    "Python 3",
    "",
    "Lenguaje libre según el enunciado. Facilita validación, tablas y gráficas en el mismo entorno.",
], NAVY)
tarjeta(s, 4.8, 1.8, 3.9, 4.4, "Interfaz gráfica", [
    "Streamlit",
    "",
    "Aplicación local en el navegador. Formularios, tablas y Plotly para el gráfico, sin separar backend y frontend.",
], TEAL)
tarjeta(s, 8.9, 1.8, 3.7, 4.4, "Método propio", [
    "Gran M (Big-M)",
    "",
    "Cubre Max/Min y restricciones ≤, ≥ y =. Se adapta al modo paso a paso con tablero.",
], RGBColor(0xE7, 0x6F, 0x51))

# 3 Justificación breve
s = prs.slides.add_slide(BLANK)
titulo(s, "Justificación", "Por qué estas decisiones", 3)
puntos = [
    ("Método Gran M", "Permite un solo flujo para todos los tipos de restricción del enunciado, con holguras, excesos y artificiales."),
    ("Librerías externas", "PuLP o scipy solo para verificar. La solución que muestra la app sale del método implementado por el equipo."),
    ("Streamlit", "Cumple la GUI obligatoria, acelera el boceto funcional y se ejecuta en sustentación con un comando."),
]
for i, (h, b) in enumerate(puntos):
    y = 1.85 + i * 1.55
    caja(s, 0.7, y, 11.9, 1.35, CARD, borde=LINE)
    caja(s, 0.7, y, 0.12, 1.35, [NAVY, TEAL, RGBColor(0xE7, 0x6F, 0x51)][i], forma=MSO_SHAPE.RECTANGLE)
    texto(s, 1.15, y + 0.25, 11, 0.4, [(h, 20, NAVY, True)])
    texto(s, 1.15, y + 0.7, 11, 0.5, [(b, 16, INK, False)])

# 4 Boceto
s = prs.slides.add_slide(BLANK)
titulo(s, "Boceto de interfaz", "Pantallas previstas", 4)
pantallas = [
    ("1. Entrada", "Max/Min, n, m, coeficientes C, matriz A, vector b y tipo de cada restricción. Botones Validar, Resolver y Paso a paso."),
    ("2. Resultados", "Valor de cada Xi, Z, holguras o excesos, y mensaje si el caso es especial (infactible, no acotado, etc.)."),
    ("3. Paso a paso", "Cada iteración del tablero: variable que entra, variable que sale, pivote y Z parcial."),
    ("4. Gráfico", "Solo si n = 2: región factible, vértices con Z e isoutilidad. Si n > 2, se indica que no aplica."),
    ("5. Sensibilidad", "Precios sombra, costos reducidos y rangos de C y de b."),
]
for i, (h, b) in enumerate(pantallas):
    y = 1.7 + i * 1.0
    caja(s, 0.7, y, 11.9, 0.88, CARD, borde=LINE)
    texto(s, 0.95, y + 0.12, 2.4, 0.6, [(h, 17, TEAL, True)], anchor=MSO_ANCHOR.MIDDLE)
    texto(s, 3.4, y + 0.12, 8.9, 0.65, [(b, 15, INK, False)], anchor=MSO_ANCHOR.MIDDLE)

# 5 Cierre
s = prs.slides.add_slide(BLANK)
titulo(s, "Resumen", "Lo que socializamos hoy", 5)
resumen = [
    ("Integrantes", "Jhoan Sebastian Puerta Uribe y Carol Victoria"),
    ("Stack", "Python 3 + Streamlit"),
    ("Método", "Gran M (implementación propia)"),
    ("Alcance de la app", "Entrada validada, solución directa, paso a paso, gráfico 2D y sensibilidad"),
]
for i, (h, b) in enumerate(resumen):
    y = 1.85 + i * 1.15
    caja(s, 0.7, y, 11.9, 1.0, CARD, borde=LINE)
    texto(s, 1.0, y + 0.28, 3.0, 0.5, [(h, 18, TEAL, True)])
    texto(s, 4.2, y + 0.28, 8.0, 0.5, [(b, 18, INK, False)])

out = HERE / "Propuesta_Sprint1_PL.pptx"
prs.save(out)
print("Listo:", out)
