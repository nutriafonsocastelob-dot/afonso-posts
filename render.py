"""Gera os slides do Instagram de Afonso Castelo Branco (1080x1350, JPEG).

Uso: python3 render.py post.json pasta_saida
post.json:
{
  "slides": [
    {"tipo": "capa",  "tag": "FISIOLOGIA", "titulo": "Seu músculo não cresce *durante* o treino.", "sub": "texto curto opcional"},
    {"tipo": "texto", "tag": "O MECANISMO", "titulo": "Título do slide", "corpo": "Parágrafo curto.\nOutro parágrafo."},
    {"tipo": "lista", "tag": "NA PRÁTICA", "titulo": "Título", "itens": ["item 1", "item 2"]},
    {"tipo": "imagem", "tag": "...", "titulo": "...", "imagem": "arquivo.png", "legenda": "fonte/nota curta"},
    {"tipo": "final", "titulo": "Conclusão em uma frase.", "corpo": "texto curto", "cta": "Salve para consultar depois"}
  ]
}
- Destaque em dourado: palavras entre *asteriscos* (em titulo, sub, corpo, itens).
- Todos os slides são azul-marinho (não existe mais tema claro).
"""
import sys, os, json, re
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
B = lambda f: os.path.join(AQUI, "brand", f)
FONTE = os.path.join(AQUI, "fonts", "Montserrat-VF.ttf")

W, H = 1080, 1350
NAVY = (15, 45, 71)
OURO = (214, 170, 92)        # dourado legível no azul (tom do gradiente da logo)
OURO_ESC = (140, 96, 52)     # bronze da logo (#8C6034) para fundo claro
BRANCO = (255, 255, 255)
CINZA_CL = (190, 200, 210)
TEXTO_CL = (40, 52, 64)


def fonte(peso, tam):
    f = ImageFont.truetype(FONTE, tam)
    f.set_variation_by_name(peso)
    return f


def tokens(texto):
    """Lista de palavras; cada palavra é uma lista de pedaços (texto, destaque).
    Quebra de linha vira a palavra None. Pontuação colada ao destaque fica na mesma palavra."""
    out, dest, colar_prox = [], False, False
    for parte in re.split(r"(\*)", texto):
        if parte == "*":
            dest = not dest
            continue
        for li, linha in enumerate(parte.split("\n")):
            if li > 0:
                out.append(None); colar_prox = False
            ws = linha.split()
            for wi, w in enumerate(ws):
                if wi == 0 and colar_prox and linha[:1].strip() and out and out[-1] is not None:
                    out[-1].append((w, dest))
                else:
                    out.append([(w, dest)])
            colar_prox = bool(linha) and not linha[-1:].isspace()
            if not ws:
                colar_prox = colar_prox and False
    return out


def larg_palavra(d, p, f):
    return sum(d.textlength(t, font=f) for t, _ in p)


def quebrar(d, texto, f, maxw):
    linhas, atual, w_atual = [], [], 0
    esp = d.textlength(" ", font=f)
    for p in tokens(texto):
        if p is None:
            linhas.append(atual); atual, w_atual = [], 0
            continue
        lp = larg_palavra(d, p, f)
        if atual and w_atual + esp + lp > maxw:
            linhas.append(atual); atual, w_atual = [], 0
        w_atual += (esp if atual else 0) + lp
        atual.append(p)
    if atual:
        linhas.append(atual)
    return linhas


def escrever(d, x, y, texto, f, maxw, cor, cor_dest, entre=1.18, centro=False):
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * entre)
    esp = d.textlength(" ", font=f)
    for linha in quebrar(d, texto, f, maxw):
        if not linha:
            y += lh // 2
            continue
        total = sum(larg_palavra(d, p, f) for p in linha) + esp * (len(linha) - 1)
        xx = x + (maxw - total) / 2 if centro else x
        for p in linha:
            for t, h in p:
                d.text((xx, y), t, font=f, fill=cor_dest if h else cor)
                xx += d.textlength(t, font=f)
            xx += esp
        y += lh
    return y


def altura(d, texto, f, maxw, entre=1.18):
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * entre)
    return sum(lh // 2 if not l else lh for l in quebrar(d, texto, f, maxw))


def caber(d, texto, peso, maior, menor, maxw, maxh, entre=1.18):
    tam = maior
    while tam > menor:
        f = fonte(peso, tam)
        if altura(d, texto, f, maxw, entre) <= maxh and all(
                larg_palavra(d, p, f) <= maxw for p in tokens(texto) if p is not None):
            return f
        tam -= 2
    return fonte(peso, menor)


def colar(img, arq, larg, xy):
    im = Image.open(arq).convert("RGBA")
    im = im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)
    img.paste(im, xy, im)
    return im.size


def tag(d, x, y, texto, escuro):
    f = fonte("Bold", 26)
    txt = texto.upper()
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle([x, y, x + tw + 44, y + 52], radius=26,
                        outline=OURO if escuro else OURO_ESC, width=3)
    d.text((x + 22, y + 11), txt, font=f, fill=OURO if escuro else OURO_ESC)
    return y + 52


def contador(d, i, n, escuro):
    f = fonte("Medium", 30)
    s = f"{i}/{n}"
    d.text((W - 90 - d.textlength(s, font=f), 92), s, font=f,
           fill=CINZA_CL if escuro else (120, 130, 140))


def base(escuro):
    return Image.open(B("fundo.png")).convert("RGB")


def slide(s, i, n, pasta):
    tipo = s.get("tipo", "texto")
    escuro = True  # decisão do Afonso: todos os slides em azul-marinho
    img = base(escuro)
    d = ImageDraw.Draw(img)
    cor = BRANCO if escuro else NAVY
    dest = OURO if escuro else OURO_ESC
    corpo_cor = (225, 230, 236) if escuro else TEXTO_CL
    X = 90 if escuro else 280          # no claro, a faixa azul ocupa a esquerda
    MAXW = W - X - 90

    contador(d, i, n, escuro)

    if tipo == "capa":
        y = 300
        if s.get("tag"):
            y = tag(d, X, y, s["tag"], True) + 50
        f = caber(d, s["titulo"], "ExtraBold", 104, 62, MAXW, 560, 1.08)
        y = escrever(d, X, y, s["titulo"], f, MAXW, cor, dest, 1.08) + 40
        if s.get("sub"):
            f2 = caber(d, s["sub"], "Medium", 42, 32, MAXW, 200)
            escrever(d, X, y, s["sub"], f2, MAXW, corpo_cor, dest)
        fa = fonte("SemiBold", 32)
        d.text((W - 90 - d.textlength("arraste →", font=fa), 1150), "arraste →", font=fa, fill=OURO)

    elif tipo == "final":
        y = 360
        f = caber(d, s["titulo"], "ExtraBold", 78, 50, MAXW, 380, 1.1)
        y = escrever(d, X, y, s["titulo"], f, MAXW, cor, dest, 1.1) + 40
        if s.get("corpo"):
            f2 = caber(d, s["corpo"], "Medium", 40, 30, MAXW, 260)
            y = escrever(d, X, y, s["corpo"], f2, MAXW, corpo_cor, dest) + 40
        if s.get("cta"):
            f3 = fonte("Bold", 34)
            tw = d.textlength(s["cta"], font=f3)
            d.rounded_rectangle([X, y, X + tw + 60, y + 76], radius=38, fill=OURO)
            d.text((X + 30, y + 19), s["cta"], font=f3, fill=NAVY)

    else:
        y = 230 if escuro else 200
        if s.get("tag"):
            y = tag(d, X, y, s["tag"], escuro) + 40
        f = caber(d, s.get("titulo", ""), "ExtraBold", 72, 46, MAXW, 300, 1.1)
        y = escrever(d, X, y, s.get("titulo", ""), f, MAXW, cor, dest, 1.1) + 36
        LIM = 1110 if escuro else 1250
        if tipo == "texto" and s.get("corpo"):
            f2 = caber(d, s["corpo"], "Medium", 42, 30, MAXW, LIM - y, 1.32)
            escrever(d, X, y, s["corpo"], f2, MAXW, corpo_cor, dest, 1.32)
        elif tipo == "lista":
            itens = s.get("itens", [])
            junto = "\n".join(itens)
            f2 = caber(d, junto, "SemiBold", 40, 28, MAXW - 50, LIM - y - 30 * len(itens), 1.25)
            for it in itens:
                asc, _ = f2.getmetrics()
                d.ellipse([X, y + asc // 2 - 4, X + 16, y + asc // 2 + 12], fill=dest)
                y = escrever(d, X + 46, y, it, f2, MAXW - 46, corpo_cor, dest, 1.25) + 30
        elif tipo == "imagem":
            ar = os.path.join(pasta, s["imagem"])
            im = Image.open(ar).convert("RGBA")
            maxh = LIM - y - (50 if s.get("legenda") else 0)
            esc = min(MAXW / im.width, maxh / im.height)
            im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
            img.paste(im, (X + (MAXW - im.width) // 2, y), im)
            y += im.height + 14
            if s.get("legenda"):
                d.text((X, y), s["legenda"], font=fonte("Medium", 24), fill=CINZA_CL if escuro else (110, 120, 130))
    return img


def main(arq, saida):
    post = json.load(open(arq, encoding="utf-8"))
    pasta = os.path.dirname(os.path.abspath(arq))
    os.makedirs(saida, exist_ok=True)
    n = len(post["slides"])
    for i, s in enumerate(post["slides"], 1):
        out = os.path.join(saida, f"slide-{i:02d}.jpg")
        slide(s, i, n, pasta).save(out, "JPEG", quality=92, optimize=True)
        print("ok", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
