#!/usr/bin/env python3
"""
Genera los 4 portfolios de Camila Mihalyczo (UX/UI y Creative, EN y ES).

Todo el contenido vive en el dict CONTENT de abajo: para cambiar un texto,
editás ahí y volvés a correr el script. Las 4 salidas quedan sincronizadas.

    python3 build_portfolios.py

Salidas en assets/portfolio/:
    camila-mihalyczo-portfolio-uxui-en.pdf      camila-mihalyczo-portfolio-uxui-es.pdf
    camila-mihalyczo-portfolio-creative-en.pdf  camila-mihalyczo-portfolio-creative-es.pdf
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

HERE = os.path.dirname(os.path.abspath(__file__))
IMG  = os.path.join(HERE, 'assets', 'img', 'work')
OUT  = os.path.join(HERE, 'assets', 'portfolio')
os.makedirs(OUT, exist_ok=True)

# ── paleta: la misma del sitio ──
BG      = HexColor('#0a0a0f')
BG2     = HexColor('#111118')
SURFACE = HexColor('#1e1e2e')
BORDER  = HexColor('#2a2a3e')
BORDER2 = HexColor('#3a3a55')
TEXT    = HexColor('#e2e0f0')
MUTED   = HexColor('#8888aa')
DIM     = HexColor('#555570')
GREEN   = HexColor('#00ff88')
CYAN    = HexColor('#00d4ff')
VIOLET  = HexColor('#a78bfa')

pdfmetrics.registerFont(TTFont('Unb',   os.path.join(HERE, 'unbounded900.ttf')))
pdfmetrics.registerFont(TTFont('UnbB',  os.path.join(HERE, 'unbounded700.ttf')))
pdfmetrics.registerFont(TTFont('Mono',  os.path.join(HERE, 'jbmono400.ttf')))
pdfmetrics.registerFont(TTFont('MonoB', os.path.join(HERE, 'jbmono700.ttf')))

W, H = 1440, 810
M = 90  # margen

CONTACT = {
    'mail': 'camilamihalyczo@gmail.com',
    'site': 'camilamihalyczo.vercel.app',
    'li':   'linkedin.com/in/camila-mihalyczo',
    'gh':   'github.com/camilamihalyczo-dotcom',
    'tel':  '+54 11 5126-8940',
}


# ────────────────────────────── helpers de dibujo ──────────────────────────────
def bg(c, shade=BG):
    c.setFillColor(shade)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def grid(c, step=60, alpha=0.30):
    c.saveState()
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.6)
    c.setStrokeAlpha(alpha)
    x = 0
    while x <= W:
        c.line(x, 0, x, H); x += step
    y = 0
    while y <= H:
        c.line(0, y, W, y); y += step
    c.restoreState()


def wrap(text, font, size, maxw):
    """Corta un texto en líneas que entren en maxw."""
    words, lines, cur = text.split(), [], ''
    for wd in words:
        probe = (cur + ' ' + wd).strip()
        if pdfmetrics.stringWidth(probe, font, size) <= maxw:
            cur = probe
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(c, text, x, y, maxw, font='Mono', size=15, leading=26, color=MUTED):
    c.setFont(font, size)
    c.setFillColor(color)
    for i, ln in enumerate(wrap(text, font, size, maxw)):
        c.drawString(x, y - i * leading, ln)
    return y - len(wrap(text, font, size, maxw)) * leading


def eyebrow(c, text, x, y, color=GREEN, size=13, prefix='> '):
    c.setFont('Mono', size)
    c.setFillColor(DIM)
    c.drawString(x, y, prefix)
    c.setFillColor(color)
    c.drawString(x + pdfmetrics.stringWidth(prefix, 'Mono', size), y, text.upper())


def section_label(c, text, x, y, color=GREEN, size=12):
    c.setFont('Mono', size)
    c.setFillColor(DIM)
    c.drawString(x, y, '// ')
    c.setFillColor(color)
    c.drawString(x + pdfmetrics.stringWidth('// ', 'Mono', size), y, text.upper())


def tag(c, text, x, y, size=11):
    pad = 10
    tw = pdfmetrics.stringWidth(text, 'Mono', size)
    c.setStrokeColor(BORDER2); c.setFillColor(SURFACE); c.setLineWidth(0.8)
    c.rect(x, y - 6, tw + pad * 2, size + 12, fill=1, stroke=1)
    c.setFillColor(MUTED); c.setFont('Mono', size)
    c.drawString(x + pad, y + 1, text)
    return x + tw + pad * 2 + 8


def tag_row(c, tags, x, y, maxw, size=11):
    cx, cy = x, y
    for t in tags:
        tw = pdfmetrics.stringWidth(t, 'Mono', size) + 28
        if cx + tw > x + maxw:
            cx, cy = x, cy - 34
        cx = tag(c, t, cx, cy, size)
    return cy


def image_panel(c, path, x, y, bw, bh, pad=18):
    """Dibuja la imagen contenida (sin recortar) dentro de un panel."""
    c.setFillColor(BG2); c.setStrokeColor(BORDER); c.setLineWidth(1)
    c.rect(x, y, bw, bh, fill=1, stroke=1)
    if not os.path.exists(path):
        c.setFillColor(DIM); c.setFont('Mono', 12)
        c.drawCentredString(x + bw / 2, y + bh / 2, '— pending —')
        return
    img = ImageReader(path)
    iw, ih = img.getSize()
    aw, ah = bw - pad * 2, bh - pad * 2
    sc = min(aw / iw, ah / ih)
    dw, dh = iw * sc, ih * sc
    c.drawImage(img, x + (bw - dw) / 2, y + (bh - dh) / 2, dw, dh,
                preserveAspectRatio=True, mask='auto')


def bullet_mark(c, x, y, size=6, color=GREEN):
    """Triangulito dibujado: JetBrains Mono no trae el glifo ▸ y sale como caja."""
    c.setFillColor(color)
    path = c.beginPath()
    path.moveTo(x, y)
    path.lineTo(x, y + size * 1.6)
    path.lineTo(x + size, y + size * 0.8)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def footer(c, page_no, total, lang):
    c.setStrokeColor(BORDER); c.setLineWidth(1)
    c.line(M, 52, W - M, 52)
    c.setFont('Mono', 11); c.setFillColor(DIM)
    c.drawString(M, 32, CONTACT['site'])
    c.drawRightString(W - M, 32, f'{page_no:02d} / {total:02d}')
    c.setFillColor(GREEN); c.setFont('MonoB', 11)
    c.drawCentredString(W / 2, 32, 'CM_')


def cover(c, t):
    bg(c); grid(c, 60, 0.25)
    c.setFillColor(GREEN)
    c.rect(0, H - 6, W, 6, fill=1, stroke=0)
    eyebrow(c, t['cover_eyebrow'], M, H - 150)
    c.setFont('Unb', 96); c.setFillColor(TEXT)
    c.drawString(M, H - 300, t['cover_l1'])
    c.setFillColor(GREEN)
    c.drawString(M, H - 410, t['cover_l2'])
    c.setFont('Mono', 20); c.setFillColor(MUTED)
    c.drawString(M, H - 480, 'Camila Mihalyczo')
    c.setFont('Mono', 16); c.setFillColor(CYAN)
    c.drawString(M, H - 520, t['cover_role'])
    c.setFont('Mono', 14); c.setFillColor(DIM)
    c.drawString(M, H - 590, f"{CONTACT['mail']}   ·   {CONTACT['tel']}   ·   Buenos Aires, Argentina")
    c.setFont('Mono', 14); c.setFillColor(DIM)
    c.drawString(M, H - 620, f"{CONTACT['site']}   ·   {CONTACT['li']}")


def closing(c, t):
    bg(c); grid(c, 60, 0.2)
    section_label(c, t['contact_label'], M, H - 130)
    c.setFont('Unb', 64); c.setFillColor(TEXT)
    c.drawString(M, H - 230, t['contact_title'])
    para(c, t['contact_body'], M, H - 300, 760, size=16, leading=30)
    rows = [('EMAIL', CONTACT['mail']), ('SITE', CONTACT['site']),
            ('LINKEDIN', CONTACT['li']), ('PHONE / WA', CONTACT['tel'])]
    y = H - 430
    for label, val in rows:
        c.setFillColor(SURFACE); c.setStrokeColor(BORDER); c.setLineWidth(1)
        c.rect(M, y - 14, 760, 46, fill=1, stroke=1)
        c.setFont('Mono', 11); c.setFillColor(DIM)
        c.drawString(M + 20, y + 3, label)
        c.setFont('Mono', 15); c.setFillColor(TEXT)
        c.drawString(M + 190, y + 2, val)
        y -= 58


def project_page(c, t, p, img_path):
    """Página de proyecto: texto a la izquierda, imagen a la derecha."""
    bg(c)
    section_label(c, p['kicker'], M, H - 120, GREEN)
    c.setFont('Unb', 52); c.setFillColor(TEXT)
    yy = H - 200
    for ln in wrap(p['title'], 'Unb', 52, 560):
        c.drawString(M, yy, ln); yy -= 62
    c.setFont('Mono', 15); c.setFillColor(CYAN)
    c.drawString(M, yy - 6, p['role'])
    yy = para(c, p['body'], M, yy - 60, 560, size=15, leading=28)
    if p.get('bullets'):
        yy -= 22
        for b in p['bullets']:
            bullet_mark(c, M, yy + 2)
            lines = wrap(b, 'Mono', 14, 520)
            c.setFillColor(MUTED)
            for i, ln in enumerate(lines):
                c.drawString(M + 24, yy - i * 24, ln)
            yy -= len(lines) * 24 + 14
    tag_row(c, p['tags'], M, 130, 560)
    image_panel(c, img_path, 720, 150, W - 720 - M, H - 300)


# ────────────────────────────── contenido ──────────────────────────────
CONTENT = {
'uxui': {
 'en': {
  'title': 'Camila Mihalyczo — UX/UI Portfolio',
  'cover_eyebrow': 'portfolio 2026',
  'cover_l1': 'UX/UI', 'cover_l2': 'design',
  'cover_role': 'UX/UI & Multimedia Designer — Frontend Developer',
  'approach_label': '01 — approach',
  'approach_title': 'how I work',
  'approach_intro': 'I design interfaces and then build them. Working across both sides means fewer decisions get lost between the mockup and the shipped screen.',
  'approach': [
   ('Research', 'I start from the people using the thing: what they came to do, where they get stuck, what they already expect from similar products.'),
   ('Interaction', 'Flows and states before pixels. What happens on empty, on error, on the slow connection — designed, not left to chance.'),
   ('Visual', 'Type, spacing and colour as a system, not per screen. Built in Figma, handed off in a way a developer can actually implement.'),
  ],
  'approach_note': 'My designs focus on ease of use and accessibility.',
  'p1': {'kicker': '02 — project', 'title': 'Simply Shopping', 'role': 'Mobile app — UX/UI',
         'body': 'A mobile-first e-commerce app built around discovery. The brief was a simple, accessible interface where finding something you like takes as few taps as possible.',
         'bullets': ['Screens for discovery, weekly deals and personalised recommendations.',
                     'Editorial type paired with generous product imagery to keep the browse experience calm.',
                     'One clear action per card, so the path to a product is never ambiguous.'],
         'tags': ['Figma', 'Mobile-first', 'User flows', 'E-commerce UX', 'App design']},
  'p2': {'kicker': '03 — project', 'title': 'Agile Technology', 'role': 'Responsive interface — UI',
         'body': 'A responsive interface for a tech product, designed as a system rather than a set of screens: the same components rearrange across sizes instead of being redrawn.',
         'bullets': ['Sign-up flow and product showcase, tablet through desktop.',
                     'High-contrast layout splitting product imagery from the form, so the action always reads first.',
                     'Component and spacing rules documented for handoff.'],
         'tags': ['Figma', 'Design system', 'Responsive UI', 'Interface design']},
  'more_label': '04 — also in progress',
  'more_title': 'design meets code',
  'more_intro': 'Beyond Figma, these are live products where I did both the design and the build. Screens for these are being prepared — they are all public and can be visited today.',
  'more': [
   ('Activity Blog', 'activityblog.vercel.app', 'Activity platform for online English classes. Admin panel to create and control sessions and track student progress, behind authenticated access.', ['React', 'Supabase', 'Auth', 'Admin dashboard']),
   ('Netianas', 'netianas.vercel.app', 'Mobile-first site designed and built end to end, with a contact flow running on my own Node API deployed on Railway.', ['Visual design', 'Node.js', 'REST API', 'Railway']),
   ('VNS Matrix', 'camilamihalyczo-dotcom.github.io', 'Immersive cyberfeminist web experience — art direction and interface built around a glitch aesthetic, with non-linear navigation.', ['Art direction', 'Interaction design', 'JavaScript']),
  ],
  'contact_label': '05 — contact',
  'contact_title': "let's make something",
  'contact_body': 'Open to remote opportunities — full-time, part-time or freelance. Comfortable working with international teams in English or Spanish.',
 },
 'es': {
  'title': 'Camila Mihalyczo — Portfolio UX/UI',
  'cover_eyebrow': 'portfolio 2026',
  'cover_l1': 'diseño', 'cover_l2': 'UX/UI',
  'cover_role': 'Diseñadora UX/UI & Multimedial — Desarrolladora Frontend',
  'approach_label': '01 — enfoque',
  'approach_title': 'cómo trabajo',
  'approach_intro': 'Diseño interfaces y después las construyo. Trabajar de los dos lados hace que se pierdan menos decisiones entre el mockup y la pantalla publicada.',
  'approach': [
   ('Investigación', 'Arranco por las personas que van a usarlo: a qué vinieron, dónde se traban, qué esperan de un producto parecido.'),
   ('Interacción', 'Flujos y estados antes que píxeles. Qué pasa cuando está vacío, cuando falla, cuando la conexión es lenta — diseñado, no librado al azar.'),
   ('Visual', 'Tipografía, espaciado y color como sistema, no pantalla por pantalla. Hecho en Figma y entregado de una forma que un dev pueda implementar.'),
  ],
  'approach_note': 'Mis diseños se enfocan en la facilidad de uso y la accesibilidad.',
  'p1': {'kicker': '02 — proyecto', 'title': 'Simply Shopping', 'role': 'App mobile — UX/UI',
         'body': 'Una app de e-commerce mobile-first construida alrededor del descubrimiento. El pedido era una interfaz simple y accesible, donde encontrar algo que te guste tome la menor cantidad de taps posible.',
         'bullets': ['Pantallas de descubrimiento, ofertas semanales y recomendaciones personalizadas.',
                     'Tipografía editorial combinada con imágenes de producto grandes para que navegar sea una experiencia tranquila.',
                     'Una sola acción clara por tarjeta, para que el camino al producto nunca sea ambiguo.'],
         'tags': ['Figma', 'Mobile-first', 'Flujos de usuario', 'UX de e-commerce', 'Diseño de app']},
  'p2': {'kicker': '03 — proyecto', 'title': 'Agile Technology', 'role': 'Interfaz responsive — UI',
         'body': 'Una interfaz responsive para un producto tecnológico, diseñada como sistema y no como un conjunto de pantallas: los mismos componentes se reacomodan según el tamaño en vez de volver a dibujarse.',
         'bullets': ['Flujo de registro y showcase de producto, de tablet a desktop.',
                     'Layout de alto contraste que separa la imagen de producto del formulario, para que la acción se lea primero.',
                     'Reglas de componentes y espaciado documentadas para la entrega.'],
         'tags': ['Figma', 'Design system', 'UI responsive', 'Diseño de interfaz']},
  'more_label': '04 — también en curso',
  'more_title': 'diseño y código',
  'more_intro': 'Más allá de Figma, estos son productos publicados donde hice el diseño y el desarrollo. Las capturas están en preparación — los tres son públicos y se pueden visitar hoy.',
  'more': [
   ('Activity Blog', 'activityblog.vercel.app', 'Plataforma de actividades para clases de inglés online. Panel de administración para crear y controlar sesiones y seguir el progreso de cada alumno, con acceso autenticado.', ['React', 'Supabase', 'Auth', 'Panel admin']),
   ('Netianas', 'netianas.vercel.app', 'Sitio mobile-first diseñado y construido de punta a punta, con un flujo de contacto que corre sobre una API propia en Node desplegada en Railway.', ['Diseño visual', 'Node.js', 'REST API', 'Railway']),
   ('VNS Matrix', 'camilamihalyczo-dotcom.github.io', 'Experiencia web cyberfeminista inmersiva — dirección de arte e interfaz construidas sobre una estética glitch, con navegación no lineal.', ['Dirección de arte', 'Diseño de interacción', 'JavaScript']),
  ],
  'contact_label': '05 — contacto',
  'contact_title': 'hagamos algo',
  'contact_body': 'Abierta a oportunidades remotas — tiempo completo, medio tiempo o freelance. Cómoda trabajando con equipos internacionales en inglés o español.',
 },
},
'creative': {
 'en': {
  'title': 'Camila Mihalyczo — Creative Portfolio',
  'cover_eyebrow': 'portfolio 2026',
  'cover_l1': 'creative', 'cover_l2': 'portfolio',
  'cover_role': 'Content Creator · Community Manager · Digital Marketing',
  'about_label': '01 — about',
  'about_title': 'about me',
  'about_body': 'Bilingual content creator and community manager with 6+ years building brand presence across digital channels. I develop content strategies, manage multi-platform communities and produce the visual assets that go with them. Background in education, marketing and international operations, currently finishing a Bachelor\'s in Multimedia Arts at Universidad Nacional de las Artes.',
  'edu_label': 'education',
  'edu': [('2023 — now', 'Multimedia Arts — UNA'), ('2024', 'UI/UX Design'), ('2023', 'Digital Marketing')],
  'exp_label': 'experience',
  'exp': [('2025', 'Freelancer at WeWant Studio', 'Branding, product content, community management and Meta Ads for national and international clients.'),
          ('2024', 'Content Creator — Social Media', 'Posts, stories and copy for emerging artists; content for art galleries.'),
          ('2022', 'Marketing Director — AIESEC Argentina', 'Creative team and social media management. International support and follow-up.')],
  'skills_label': 'skills',
  'skills': ['Community & Meta Ads management', 'Social media design', 'Video editing', 'Canva & Adobe Suite', 'Copywriting EN / ES'],
  'w1': {'kicker': '02 — client work', 'title': 'AIESEC Argentina', 'role': 'Campaign & social — 2022',
         'body': 'AIESEC is a non-profit focused on international volunteer programs, and on guiding students near the end of their degrees toward a first formal work experience abroad.',
         'bullets': ['Visual approach designed to be eye-catching, youthful and fresh.',
                     'Full campaign across feed and stories, in Spanish and English.',
                     'Led the creative team and the social media operation.'],
         'tags': ['Campaign', 'Social design', 'Community', 'Copywriting']},
  'w2': {'kicker': '03 — client work', 'title': 'Galleries & artists', 'role': 'Freelance content — 2024',
         'body': 'Freelance content creation and community management for clients in the art industry: digital campaigns and content for galleries, artists and private clients.',
         'bullets': ['Posters and event pieces for film cycles, exhibitions and community events.',
                     'Feed design keeping a consistent visual identity across each cycle.',
                     'Copy and scheduling for each launch.'],
         'tags': ['Poster design', 'Art direction', 'Feed design', 'Cultural comms']},
  'w3': {'kicker': '04 — client work', 'title': 'Tiberio Food & Coffee', 'role': 'WeWant Studio — 2025',
         'body': 'In 2025 I joined the freelance studio WeWant as a content creator and community manager, running Meta Ads campaigns for national and international clients. Tiberio is a Buenos Aires gastronomy client, included here as an example.',
         'bullets': ['Product content and brand pieces for feed, stories and ads.',
                     'Consistent typographic system across every piece.',
                     'Meta Ads campaign management.'],
         'tags': ['Brand content', 'Meta Ads', 'Gastronomy', 'Community']},
  'motion_label': '05 — motion',
  'motion_title': 'motion & video',
  'motion_intro': 'Short-form pieces for feed, stories and ads — edited and animated end to end. These are video: the frames below are stills, and the full pieces play on the site.',
  'motion_sample': 'SAMPLE',
  'motion_watch': 'Watch them at',
  'motion': [
   ('tiberio-ad', 'Tiberio Food & Coffee', 'brand ad — 6s', False),
   ('tiberio-desayuno', 'Tiberio — Desayuno', 'social piece — 10s', False),
   ('coming-soon', 'Coming Soon', 'campaign teaser — 5s', False),
   ('sample-promo', 'Sale Promo', 'sample piece — 15s', True),
   ('sample-sale', 'Spring Sale', 'sample piece — 15s', True),
  ],
  'contact_label': '06 — contact',
  'contact_title': "let's work together",
  'contact_body': 'Open to remote opportunities — full-time, part-time or freelance. Comfortable working with international teams in English or Spanish.',
 },
 'es': {
  'title': 'Camila Mihalyczo — Portfolio Creativo',
  'cover_eyebrow': 'portfolio 2026',
  'cover_l1': 'portfolio', 'cover_l2': 'creativo',
  'cover_role': 'Creadora de Contenido · Community Manager · Marketing Digital',
  'about_label': '01 — sobre mí',
  'about_title': 'sobre mí',
  'about_body': 'Creadora de contenido y community manager bilingüe con más de 6 años construyendo presencia de marca en canales digitales. Desarrollo estrategias de contenido, gestiono comunidades multiplataforma y produzco las piezas visuales que las acompañan. Vengo de la educación, el marketing y la gestión de operaciones internacionales, y estoy terminando la Licenciatura en Artes Multimediales en la Universidad Nacional de las Artes.',
  'edu_label': 'formación',
  'edu': [('2023 — hoy', 'Artes Multimediales — UNA'), ('2024', 'Diseño UI/UX'), ('2023', 'Marketing Digital')],
  'exp_label': 'experiencia',
  'exp': [('2025', 'Freelance en WeWant Studio', 'Branding, contenido de producto, community management y Meta Ads para clientes nacionales e internacionales.'),
          ('2024', 'Creadora de Contenido — Redes', 'Posteos, stories y copy para artistas emergentes; contenido para galerías de arte.'),
          ('2022', 'Directora de Marketing — AIESEC Argentina', 'Gestión del equipo creativo y de las redes. Soporte y seguimiento internacional.')],
  'skills_label': 'habilidades',
  'skills': ['Community & gestión de Meta Ads', 'Diseño para redes', 'Edición de video', 'Canva & Adobe Suite', 'Copywriting EN / ES'],
  'w1': {'kicker': '02 — trabajo para clientes', 'title': 'AIESEC Argentina', 'role': 'Campaña y redes — 2022',
         'body': 'AIESEC es una organización sin fines de lucro enfocada en programas de voluntariado internacional, y en acompañar a estudiantes que están terminando la carrera hacia su primera experiencia laboral formal en el exterior.',
         'bullets': ['Enfoque visual pensado para ser llamativo, joven y fresco.',
                     'Campaña completa en feed y stories, en español e inglés.',
                     'Conducción del equipo creativo y de la operación de redes.'],
         'tags': ['Campaña', 'Diseño para redes', 'Community', 'Copywriting']},
  'w2': {'kicker': '03 — trabajo para clientes', 'title': 'Galerías y artistas', 'role': 'Contenido freelance — 2024',
         'body': 'Creación de contenido y community management freelance para clientes de la industria del arte: campañas digitales y contenido para galerías, artistas y clientes privados.',
         'bullets': ['Posters y piezas de evento para ciclos de cine, muestras y encuentros de comunidad.',
                     'Diseño de feed sosteniendo una identidad visual consistente en cada ciclo.',
                     'Copy y programación de cada lanzamiento.'],
         'tags': ['Diseño de posters', 'Dirección de arte', 'Diseño de feed', 'Comunicación cultural']},
  'w3': {'kicker': '04 — trabajo para clientes', 'title': 'Tiberio Food & Coffee', 'role': 'WeWant Studio — 2025',
         'body': 'En 2025 me sumé al estudio freelance WeWant como creadora de contenido y community manager, gestionando campañas de Meta Ads para clientes nacionales e internacionales. Tiberio es un cliente gastronómico de Buenos Aires, incluido acá como ejemplo.',
         'bullets': ['Contenido de producto y piezas de marca para feed, stories y ads.',
                     'Sistema tipográfico consistente en todas las piezas.',
                     'Gestión de campañas de Meta Ads.'],
         'tags': ['Contenido de marca', 'Meta Ads', 'Gastronomía', 'Community']},
  'motion_label': '05 — motion',
  'motion_title': 'motion y video',
  'motion_intro': 'Piezas cortas para feed, stories y ads — editadas y animadas de punta a punta. Son video: los frames de abajo son capturas, y las piezas completas se reproducen en el sitio.',
  'motion_sample': 'MUESTRA',
  'motion_watch': 'Se ven en',
  'motion': [
   ('tiberio-ad', 'Tiberio Food & Coffee', 'pieza de marca — 6s', False),
   ('tiberio-desayuno', 'Tiberio — Desayuno', 'pieza de redes — 10s', False),
   ('coming-soon', 'Coming Soon', 'teaser de campaña — 5s', False),
   ('sample-promo', 'Sale Promo', 'pieza de muestra — 15s', True),
   ('sample-sale', 'Spring Sale', 'pieza de muestra — 15s', True),
  ],
  'contact_label': '06 — contacto',
  'contact_title': 'trabajemos juntos',
  'contact_body': 'Abierta a oportunidades remotas — tiempo completo, medio tiempo o freelance. Cómoda trabajando con equipos internacionales en inglés o español.',
 },
},
}


# ────────────────────────────── documentos ──────────────────────────────
def build_uxui(lang, path):
    t = CONTENT['uxui'][lang]
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle(t['title']); c.setAuthor('Camila Mihalyczo')
    c.setSubject('UX/UI design portfolio')
    TOTAL = 6

    cover(c, t); c.showPage()

    # 2 — approach
    bg(c, BG2)
    section_label(c, t['approach_label'], M, H - 120)
    c.setFont('Unb', 60); c.setFillColor(TEXT)
    c.drawString(M, H - 200, t['approach_title'])
    para(c, t['approach_intro'], M, H - 270, 900, size=16, leading=30)
    colw, gap = (W - M * 2 - 60) / 3, 30
    for i, (head, body) in enumerate(t['approach']):
        x = M + i * (colw + gap)
        c.setStrokeColor(BORDER); c.setFillColor(BG); c.setLineWidth(1)
        c.rect(x, 200, colw, 240, fill=1, stroke=1)
        c.setFillColor(GREEN); c.rect(x, 438, colw, 2, fill=1, stroke=0)
        c.setFont('UnbB', 22); c.setFillColor(TEXT)
        c.drawString(x + 26, 380, head)
        para(c, body, x + 26, 340, colw - 52, size=13, leading=24)
    c.setFont('Mono', 15); c.setFillColor(CYAN)
    c.drawString(M, 145, '“' + t['approach_note'] + '”')
    footer(c, 2, TOTAL, lang); c.showPage()

    project_page(c, t, t['p1'], os.path.join(IMG, 'simply-shopping.jpg'))
    footer(c, 3, TOTAL, lang); c.showPage()

    project_page(c, t, t['p2'], os.path.join(IMG, 'agile-technology.jpg'))
    footer(c, 4, TOTAL, lang); c.showPage()

    # 5 — also in progress
    bg(c)
    section_label(c, t['more_label'], M, H - 120)
    c.setFont('Unb', 56); c.setFillColor(TEXT)
    c.drawString(M, H - 195, t['more_title'])
    para(c, t['more_intro'], M, H - 255, 1000, size=15, leading=28)
    y = H - 370
    for name, url, desc, tags in t['more']:
        c.setFillColor(SURFACE); c.setStrokeColor(BORDER); c.setLineWidth(1)
        c.rect(M, y - 78, W - M * 2, 118, fill=1, stroke=1)
        c.setFillColor(GREEN); c.rect(M, y + 38, W - M * 2, 2, fill=1, stroke=0)
        c.setFont('UnbB', 22); c.setFillColor(TEXT)
        c.drawString(M + 28, y + 4, name)
        c.setFont('Mono', 12); c.setFillColor(CYAN)
        c.drawString(M + 28, y - 22, url)
        para(c, desc, M + 430, y + 4, 450, size=13, leading=22)
        # los tags van en su propia columna y envuelven: en ES son más largos
        tag_row(c, tags[:4], M + 930, y + 6, 330, 9)
        y -= 150
    footer(c, 5, TOTAL, lang); c.showPage()

    closing(c, t); footer(c, 6, TOTAL, lang); c.showPage()
    c.save()
    return path


def build_creative(lang, path):
    t = CONTENT['creative'][lang]
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle(t['title']); c.setAuthor('Camila Mihalyczo')
    c.setSubject('Creative / content portfolio')
    TOTAL = 7

    cover(c, t); c.showPage()

    # 2 — about + formación + experiencia + skills
    bg(c, BG2)
    section_label(c, t['about_label'], M, H - 110)
    c.setFont('Unb', 56); c.setFillColor(TEXT)
    c.drawString(M, H - 180, t['about_title'])
    para(c, t['about_body'], M, H - 240, 620, size=14, leading=26)

    x2 = M + 700
    c.setFont('Mono', 12); c.setFillColor(GREEN)
    c.drawString(x2, H - 240, t['edu_label'].upper())
    c.setStrokeColor(BORDER); c.line(x2, H - 252, W - M, H - 252)
    y = H - 285
    for when, what in t['edu']:
        c.setFont('Mono', 12); c.setFillColor(DIM); c.drawString(x2, y, when)
        c.setFont('Mono', 14); c.setFillColor(TEXT); c.drawString(x2 + 140, y, what)
        y -= 34

    y -= 24
    c.setFont('Mono', 12); c.setFillColor(GREEN)
    c.drawString(x2, y, t['exp_label'].upper())
    c.setStrokeColor(BORDER); c.line(x2, y - 12, W - M, y - 12)
    y -= 42
    for when, what, desc in t['exp']:
        c.setFont('Mono', 12); c.setFillColor(DIM); c.drawString(x2, y, when)
        c.setFont('MonoB', 14); c.setFillColor(TEXT); c.drawString(x2 + 140, y, what)
        para(c, desc, x2 + 140, y - 24, 420, size=12, leading=20)
        y -= 76

    c.setFont('Mono', 12); c.setFillColor(GREEN)
    c.drawString(M, 300, t['skills_label'].upper())
    c.setStrokeColor(BORDER); c.line(M, 288, M + 620, 288)
    tag_row(c, t['skills'], M, 245, 620, 12)
    footer(c, 2, TOTAL, lang); c.showPage()

    project_page(c, t, t['w1'], os.path.join(IMG, 'aiesec-intercambio.jpg'))
    footer(c, 3, TOTAL, lang); c.showPage()

    # 4 — galerías y artistas: grilla de posters
    bg(c)
    section_label(c, t['w2']['kicker'], M, H - 110)
    c.setFont('Unb', 50); c.setFillColor(TEXT)
    ty = H - 180
    for ln in wrap(t['w2']['title'], 'Unb', 50, 500):   # "Galerías y artistas" no entra en una línea
        c.drawString(M, ty, ln); ty -= 58
    c.setFont('Mono', 14); c.setFillColor(CYAN)
    c.drawString(M, ty - 4, t['w2']['role'])
    para(c, t['w2']['body'], M, ty - 54, 500, size=14, leading=26)
    yy = ty - 190
    for b in t['w2']['bullets']:
        bullet_mark(c, M, yy + 2)
        lines = wrap(b, 'Mono', 13, 440)
        c.setFillColor(MUTED)
        for i, ln in enumerate(lines):
            c.drawString(M + 22, yy - i * 22, ln)
        yy -= len(lines) * 22 + 12
    tag_row(c, t['w2']['tags'], M, 130, 500, 10)

    # 7 piezas: fila de 4 arriba y de 3 abajo, para que no quede un hueco suelto
    pieces = [['adolescencia.jpg', 'ciclo-cortos.jpg', 'demian-rugna.jpg', 'julieta.jpg'],
              ['falopa-feed.jpg', 'brunch-yoga.jpg', 'ilustracion.jpg']]
    gx, gy, gw, gh, gap = 620, 140, 180, 290, 16
    for row, rowpieces in enumerate(pieces):
        for col, p in enumerate(rowpieces):
            image_panel(c, os.path.join(IMG, p),
                        gx + col * (gw + gap), gy + (1 - row) * (gh + gap), gw, gh, pad=8)
    footer(c, 4, TOTAL, lang); c.showPage()

    project_page(c, t, t['w3'], os.path.join(IMG, 'tiberio-almuerzo.jpg'))
    footer(c, 5, TOTAL, lang); c.showPage()

    # 6 — motion: el PDF no reproduce video, así que van frames + dónde verlos
    bg(c, BG2)
    section_label(c, t['motion_label'], M, H - 110)
    c.setFont('Unb', 52); c.setFillColor(TEXT)
    c.drawString(M, H - 180, t['motion_title'])
    para(c, t['motion_intro'], M, H - 240, 900, size=14, leading=26)

    vw, vh, vgap = 200, 300, 26
    vx, vy = M, 190
    for i, (slug, name, kind, sample) in enumerate(t['motion']):
        x = vx + i * (vw + vgap)
        image_panel(c, os.path.join(IMG, slug + '.jpg'), x, vy, vw, vh, pad=8)
        # chapita: video, y si corresponde, muestra
        c.setFillColor(BG); c.setStrokeColor(GREEN); c.setLineWidth(0.8)
        c.rect(x + 10, vy + vh - 26, 46, 16, fill=1, stroke=1)
        c.setFont('Mono', 8); c.setFillColor(GREEN)
        c.drawCentredString(x + 33, vy + vh - 21, 'VIDEO')
        if sample:
            tw = pdfmetrics.stringWidth(t['motion_sample'], 'Mono', 8) + 14
            c.setFillColor(BG); c.setStrokeColor(HexColor('#fbbf24'))
            c.rect(x + vw - tw - 10, vy + vh - 26, tw, 16, fill=1, stroke=1)
            c.setFillColor(HexColor('#fbbf24')); c.setFont('Mono', 8)
            c.drawCentredString(x + vw - tw / 2 - 10, vy + vh - 21, t['motion_sample'])
        c.setFont('MonoB', 12); c.setFillColor(TEXT)
        for j, ln in enumerate(wrap(name, 'MonoB', 12, vw)):
            c.drawString(x, vy - 22 - j * 18, ln)
        c.setFont('Mono', 10); c.setFillColor(DIM)
        c.drawString(x, vy - 62, kind)

    c.setFont('Mono', 12); c.setFillColor(CYAN)
    c.drawString(M, 92, t['motion_watch'] + '  ' + CONTACT['site'] + '/#portfolio')
    footer(c, 6, TOTAL, lang); c.showPage()

    closing(c, t); footer(c, 7, TOTAL, lang); c.showPage()
    c.save()
    return path


if __name__ == '__main__':
    jobs = [
        (build_uxui,     'en', 'camila-mihalyczo-portfolio-uxui-en.pdf'),
        (build_uxui,     'es', 'camila-mihalyczo-portfolio-uxui-es.pdf'),
        (build_creative, 'en', 'camila-mihalyczo-portfolio-creative-en.pdf'),
        (build_creative, 'es', 'camila-mihalyczo-portfolio-creative-es.pdf'),
    ]
    for fn, lang, name in jobs:
        p = fn(lang, os.path.join(OUT, name))
        print(f'{name:48s} {os.path.getsize(p)/1e6:.2f} MB')
