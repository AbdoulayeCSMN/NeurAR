"""
Generation de la presentation PowerPoint du projet NeurAR.
Style chic et epure : peu de texte par diapositive, palette de couleurs
agreable, aucun cadre/bordure rectangulaire mince en decoration.
Quelques blocs de couleur pleins (panneaux, schemas) sont utilises comme
elements de design, mais jamais de simples rectangles-contours.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn

# ----------------------------------------------------------------------
# Palette "chic"
# ----------------------------------------------------------------------
NAVY = RGBColor(0x1B, 0x2A, 0x4A)        # bleu nuit (titres, panneaux)
TEAL = RGBColor(0x2E, 0xC4, 0xB6)        # turquoise (accent principal)
GOLD = RGBColor(0xE9, 0xC4, 0x6A)        # or doux (accent secondaire)
SOFT_BG = RGBColor(0xF4, 0xF6, 0xF8)     # fond gris tres clair
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK = RGBColor(0x2D, 0x31, 0x42)
TEXT_GRAY = RGBColor(0x8D, 0x99, 0xAE)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H

BLANK = prs.slide_layouts[6]


def add_slide():
    return prs.slides.add_slide(BLANK)


def set_background(slide, color=WHITE):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def no_line(shape):
    shape.line.fill.background()


def add_title(slide, text, accent=TEAL):
    """Petit bloc de couleur (tag) + titre. Pas de ligne/cadre."""
    tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(0.55),
                                  Inches(0.35), Inches(0.7))
    tag.fill.solid()
    tag.fill.fore_color.rgb = accent
    no_line(tag)

    box = slide.shapes.add_textbox(Inches(1.25), Inches(0.4), Inches(11.4), Inches(1.0))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(34)
    run.font.bold = True
    run.font.color.rgb = NAVY
    run.font.name = "Calibri"
    return box


def add_bullets(slide, items, left=1.25, top=2.0, width=10.8, height=4.7, font_size=24):
    """Bullets courts avec une puce carree de couleur (pas de texte dense)."""
    for i, (text, color) in enumerate(items):
        y = top + i * (height / max(len(items), 1))
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(left), Inches(y + 0.18),
                                      Inches(0.2), Inches(0.2))
        dot.fill.solid()
        dot.fill.fore_color.rgb = color
        no_line(dot)

        box = slide.shapes.add_textbox(Inches(left + 0.45), Inches(y - 0.05), Inches(width - 0.45), Inches(1.0))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = text
        run.font.size = Pt(font_size)
        run.font.color.rgb = TEXT_DARK
        run.font.name = "Calibri"


def add_footer(slide, text):
    box = slide.shapes.add_textbox(Inches(0.7), Inches(7.05), Inches(12), Inches(0.35))
    tf = box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(11)
    run.font.color.rgb = TEXT_GRAY
    run.font.name = "Calibri"


def add_box(slide, left, top, width, height, text, fill_color=NAVY, text_color=WHITE,
             font_size=14, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE):
    shp = slide.shapes.add_shape(shape_type, Inches(left), Inches(top), Inches(width), Inches(height))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_color
    no_line(shp)
    tf = shp.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.color.rgb = text_color
    run.font.bold = True
    run.font.name = "Calibri"
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return shp


def add_arrow(slide, x1, y1, x2, y2, color=TEAL):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    conn.line.color.rgb = color
    conn.line.width = Pt(2.25)
    line = conn.line._get_or_add_ln()
    head = line.makeelement(qn('a:tailEnd'), {'type': 'triangle'})
    line.append(head)
    return conn


def add_circle(slide, left, top, diameter, fill_color):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(left), Inches(top), Inches(diameter), Inches(diameter))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_color
    no_line(shp)
    return shp


def add_caption(slide, text, top=6.3):
    box = slide.shapes.add_textbox(Inches(1.25), Inches(top), Inches(10.8), Inches(0.6))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(16)
    run.font.italic = True
    run.font.color.rgb = TEXT_GRAY
    run.font.name = "Calibri"


# ========================================================================
# Slide 1 : page de titre
# ========================================================================
slide = add_slide()
set_background(slide, WHITE)

# panneau de couleur plein a gauche (element de design, pas un cadre)
panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(4.6), SLIDE_H)
panel.fill.solid()
panel.fill.fore_color.rgb = NAVY
no_line(panel)

# touche de couleur
accent_shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1.2), Inches(-1.2), Inches(3.5), Inches(3.5))
accent_shape.fill.solid()
accent_shape.fill.fore_color.rgb = TEAL
no_line(accent_shape)

accent_shape2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-0.6), Inches(5.6), Inches(2.6), Inches(2.6))
accent_shape2.fill.solid()
accent_shape2.fill.fore_color.rgb = GOLD
no_line(accent_shape2)

# titre principal
title_box = slide.shapes.add_textbox(Inches(5.2), Inches(2.0), Inches(7.6), Inches(2.2))
tf = title_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
run = p.add_run()
run.text = "NeurAR"
run.font.size = Pt(64)
run.font.bold = True
run.font.color.rgb = NAVY
run.font.name = "Calibri"

p2 = tf.add_paragraph()
run2 = p2.add_run()
run2.text = "Un reseau de neurones a decouvrir en realite augmentee"
run2.font.size = Pt(22)
run2.font.color.rgb = TEXT_GRAY
run2.font.name = "Calibri"
p2.space_before = Pt(10)

# infos auteur / encadrants
info_box = slide.shapes.add_textbox(Inches(5.2), Inches(4.7), Inches(7.6), Inches(2.3))
tf = info_box.text_frame
tf.word_wrap = True
lines = [
    ("CHAIBOU SAIDOU ABDOULAYE", 22, True, NAVY),
    ("", 6, False, NAVY),
    ("Encadrants", 16, True, TEAL),
    ("Pr. Tawfik Masrour", 17, False, TEXT_DARK),
    ("Pr. Ajebli Aymane", 17, False, TEXT_DARK),
    ("Pr. Maalouf Imad", 17, False, TEXT_DARK),
]
for i, (text, size, bold, color) in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"
    p.space_after = Pt(4)


# ========================================================================
# Slide 2 : Sommaire
# ========================================================================
slide = add_slide()
set_background(slide, SOFT_BG)
add_title(slide, "Sommaire")
items = [
    ("Contexte et objectifs", TEAL),
    ("Architecture de la solution", GOLD),
    ("Le modele de reseau de neurones", TEAL),
    ("Communication temps reel", GOLD),
    ("Application Unity en realite augmentee", TEAL),
    ("Resultats, apports et perspectives", GOLD),
]
add_bullets(slide, items, font_size=26, top=2.0, height=4.6)


# ========================================================================
# Slide 3 : Contexte
# ========================================================================
slide = add_slide()
set_background(slide, WHITE)
add_title(slide, "Contexte")
items = [
    ("Un reseau de neurones reste une 'boite noire' difficile a comprendre", TEAL),
    ("La realite augmentee permet d'explorer un objet 3D dans le monde reel", GOLD),
    ("Idee : afficher et animer un reseau de neurones en AR, en temps reel", TEAL),
]
add_bullets(slide, items, font_size=26, top=2.3, height=3.6)


# ========================================================================
# Slide 4 : Objectifs
# ========================================================================
slide = add_slide()
set_background(slide, SOFT_BG)
add_title(slide, "Objectifs du projet")
items = [
    ("Entrainer un reseau MLP avec PyTorch sur MNIST", TEAL),
    ("Exposer son etat en temps reel via une API et un WebSocket", GOLD),
    ("Visualiser le reseau en 3D dans une application Unity AR", TEAL),
    ("Animer le forward pass et le backward pass, et permettre l'interaction", GOLD),
]
add_bullets(slide, items, font_size=24, top=2.0, height=4.4)


# ========================================================================
# Slide 5 : Architecture generale (diagramme)
# ========================================================================
slide = add_slide()
set_background(slide, WHITE)
add_title(slide, "Architecture generale")

add_box(slide, 0.9, 2.7, 3.6, 1.5, "Application Unity\n(client AR)", fill_color=NAVY, font_size=16)
add_arrow(slide, 4.5, 3.1, 6.05, 3.1, color=TEAL)
add_arrow(slide, 6.05, 3.7, 4.5, 3.7, color=GOLD)

add_box(slide, 6.05, 2.7, 3.6, 1.5, "Backend FastAPI\nREST + WebSocket", fill_color=TEAL, text_color=NAVY, font_size=16)
add_arrow(slide, 9.65, 3.1, 11.2, 3.1, color=TEAL)
add_arrow(slide, 11.2, 3.7, 9.65, 3.7, color=GOLD)

add_box(slide, 9.65, 2.7, 2.95, 1.5, "Modele PyTorch\n(NeuroARNet)", fill_color=GOLD, text_color=NAVY, font_size=16)

add_caption(slide, "Unity envoie des commandes, le backend interroge le modele et renvoie l'etat du reseau", top=4.7)


# ========================================================================
# Slide 6 : Le modele MLP (schema)
# ========================================================================
slide = add_slide()
set_background(slide, SOFT_BG)
add_title(slide, "Le modele : un reseau MLP")

layer_sizes = [4, 5, 4, 3]
layer_x = [1.8, 5.0, 8.2, 11.4]
layer_names = ["Entree\n784", "Cachee 1\n128", "Cachee 2\n64", "Sortie\n10"]
diameter = 0.45
top_base = 4.0

# connexions dessinees avant les cercles
for li in range(len(layer_sizes) - 1):
    n1, n2 = layer_sizes[li], layer_sizes[li + 1]
    x1 = layer_x[li] + diameter
    x2 = layer_x[li + 1]
    start_y1 = top_base - (n1 - 1) * 0.35
    start_y2 = top_base - (n2 - 1) * 0.35
    for i in range(n1):
        for j in range(n2):
            y1 = start_y1 + i * 0.7 + diameter / 2
            y2 = start_y2 + j * 0.7 + diameter / 2
            conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
            conn.line.color.rgb = RGBColor(0xD7, 0xDE, 0xE6)
            conn.line.width = Pt(0.5)

colors_cycle = [GOLD, TEAL, TEAL, GOLD]
for li, (n, x) in enumerate(zip(layer_sizes, layer_x)):
    start_y = top_base - (n - 1) * 0.35
    for i in range(n):
        y = start_y + i * 0.7
        add_circle(slide, x, y, diameter, colors_cycle[li])
    name_box = slide.shapes.add_textbox(Inches(x - 0.45), Inches(top_base + n * 0.35 + 0.5), Inches(1.4), Inches(0.8))
    tf = name_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = layer_names[li]
    run.font.size = Pt(15)
    run.font.bold = True
    run.font.color.rgb = NAVY
    run.font.name = "Calibri"

add_caption(slide, "Linear + BatchNorm + ReLU sur les couches cachees, Softmax en sortie", top=6.2)


# ========================================================================
# Slide 7 : Fonctionnement du modele
# ========================================================================
slide = add_slide()
set_background(slide, WHITE)
add_title(slide, "Fonctionnement du modele")
items = [
    ("Architecture configurable (ex. 784 - 128 - 64 - 10) via un fichier .env", TEAL),
    ("Active sur le dataset MNIST, avec calcul de la perte et de la precision", GOLD),
    ("A chaque passe, activations, poids et biais sont extraits et normalises", TEAL),
]
add_bullets(slide, items, font_size=24, top=2.3, height=3.6)


# ========================================================================
# Slide 8 : Communication temps reel
# ========================================================================
slide = add_slide()
set_background(slide, SOFT_BG)
add_title(slide, "Communication temps reel")

# deux colonnes : REST / WebSocket
col1 = slide.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(5.6), Inches(0.6))
p = col1.text_frame.paragraphs[0]
run = p.add_run()
run.text = "API REST"
run.font.size = Pt(24)
run.font.bold = True
run.font.color.rgb = TEAL

rest_items = [
    "/health, /architecture",
    "/network",
    "/forward",
]
box = slide.shapes.add_textbox(Inches(1.0), Inches(2.6), Inches(5.6), Inches(3.2))
tf = box.text_frame
tf.word_wrap = True
for i, t in enumerate(rest_items):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    run = p.add_run()
    run.text = t
    run.font.size = Pt(20)
    run.font.color.rgb = TEXT_DARK
    p.space_after = Pt(14)

col2 = slide.shapes.add_textbox(Inches(7.0), Inches(1.9), Inches(5.6), Inches(0.6))
p = col2.text_frame.paragraphs[0]
run = p.add_run()
run.text = "WebSocket /ws"
run.font.size = Pt(24)
run.font.bold = True
run.font.color.rgb = GOLD

ws_items = [
    "get_network -> etat initial",
    "forward_pass -> animation couche par couche",
    "backward_pass -> mise a jour des poids",
    "reset -> nouveau modele",
]
box = slide.shapes.add_textbox(Inches(7.0), Inches(2.6), Inches(5.6), Inches(3.2))
tf = box.text_frame
tf.word_wrap = True
for i, t in enumerate(ws_items):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    run = p.add_run()
    run.text = t
    run.font.size = Pt(20)
    run.font.color.rgb = TEXT_DARK
    p.space_after = Pt(14)


# ========================================================================
# Slide 9 : Animation du forward pass (sequence)
# ========================================================================
slide = add_slide()
set_background(slide, WHITE)
add_title(slide, "Animation du forward pass")

add_box(slide, 1.0, 2.0, 3.0, 0.8, "Unity", fill_color=NAVY, font_size=18)
add_box(slide, 9.3, 2.0, 3.0, 0.8, "Backend", fill_color=TEAL, text_color=NAVY, font_size=18)

steps = [
    "Couche 0 (entree)",
    "Couche 1 (+100 ms)",
    "Couche 2 (+100 ms)",
    "Couche 3 / sortie (+100 ms)",
]
y = 3.2
for s in steps:
    add_arrow(slide, 9.3, y, 4.0, y, color=GOLD)
    label = slide.shapes.add_textbox(Inches(4.2), Inches(y - 0.35), Inches(5.0), Inches(0.6))
    p = label.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = s
    run.font.size = Pt(18)
    run.font.color.rgb = TEXT_DARK
    y += 0.85

add_caption(slide, "Chaque couche est diffusee separement pour une animation fluide en AR", top=6.7)


# ========================================================================
# Slide 10 : Application Unity AR
# ========================================================================
slide = add_slide()
set_background(slide, SOFT_BG)
add_title(slide, "Application Unity AR")
items = [
    ("Placement du reseau virtuel dans l'environnement reel", TEAL),
    ("Rendu 3D : couches, neurones et connexions animes", GOLD),
    ("Reception des donnees du backend via WebSocket", TEAL),
    ("Interactions : rotation, zoom, selection d'un neurone", GOLD),
]
add_bullets(slide, items, font_size=24, top=2.0, height=4.4)


# ========================================================================
# Slide 11 : Fonctionnalites cles
# ========================================================================
slide = add_slide()
set_background(slide, WHITE)
add_title(slide, "Fonctionnalites cles")
items = [
    ("Visualisation du reseau couche par couche, en 3D et en AR", TEAL),
    ("Animation du forward pass et du backward pass", GOLD),
    ("Affichage en direct des activations, poids et biais", TEAL),
    ("Suivi de la perte et de la precision, reinitialisation du modele", GOLD),
]
add_bullets(slide, items, font_size=24, top=2.0, height=4.4)


# ========================================================================
# Slide 12 : Points forts du projet
# ========================================================================
slide = add_slide()
set_background(slide, SOFT_BG)
add_title(slide, "Points forts du projet")
items = [
    ("Approche pedagogique originale : rendre visible l'invisible", TEAL),
    ("Backend decouple, reutilisable et configurable", GOLD),
    ("Communication temps reel fluide et compatible Unity/C#", TEAL),
    ("Projet transversal : IA, backend et realite augmentee", GOLD),
]
add_bullets(slide, items, font_size=24, top=2.0, height=4.4)


# ========================================================================
# Slide 13 : Difficultes et solutions
# ========================================================================
slide = add_slide()
set_background(slide, WHITE)
add_title(slide, "Difficultes et solutions")
items = [
    ("Messages volumineux (~2,4 Mo) -> limite WebSocket augmentee", TEAL),
    ("Animation trop rapide -> diffusion couche par couche (100 ms)", GOLD),
    ("Format JSON different de C# -> alias camelCase automatiques", TEAL),
]
add_bullets(slide, items, font_size=24, top=2.3, height=3.6)


# ========================================================================
# Slide 14 : Perspectives et conclusion
# ========================================================================
slide = add_slide()
set_background(slide, SOFT_BG)
add_title(slide, "Perspectives et conclusion")
items = [
    ("NeurAR relie IA et realite augmentee dans un outil pedagogique complet", TEAL),
    ("Pistes : autres architectures (CNN, RNN), mode multi-utilisateurs", GOLD),
    ("Pistes : entrainement interactif, deploiement sur casques AR/VR", TEAL),
]
add_bullets(slide, items, font_size=24, top=2.3, height=3.6)


# ========================================================================
# Slide 15 : Merci
# ========================================================================
slide = add_slide()
set_background(slide, WHITE)

panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(4.6), SLIDE_H)
panel.fill.solid()
panel.fill.fore_color.rgb = NAVY
no_line(panel)

accent_shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1.2), Inches(5.5), Inches(3.5), Inches(3.5))
accent_shape.fill.solid()
accent_shape.fill.fore_color.rgb = TEAL
no_line(accent_shape)

accent_shape2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-0.6), Inches(-1.0), Inches(2.6), Inches(2.6))
accent_shape2.fill.solid()
accent_shape2.fill.fore_color.rgb = GOLD
no_line(accent_shape2)

box = slide.shapes.add_textbox(Inches(5.2), Inches(2.8), Inches(7.5), Inches(2))
tf = box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
run = p.add_run()
run.text = "Merci pour votre attention"
run.font.size = Pt(44)
run.font.bold = True
run.font.color.rgb = NAVY
run.font.name = "Calibri"

p2 = tf.add_paragraph()
run2 = p2.add_run()
run2.text = "Questions et discussion"
run2.font.size = Pt(22)
run2.font.color.rgb = TEXT_GRAY
run2.font.name = "Calibri"
p2.space_before = Pt(10)


# ========================================================================
prs.save("NeurAR_presentation.pptx")
print("Presentation generee : NeurAR_presentation.pptx")
