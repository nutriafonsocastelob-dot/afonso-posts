"""Post de frase das quartas - Afonso Castelo Branco (1080x1350, fundo claro liso, serifa).
Uso (na raiz do repositorio): python3 frase.py "Dieta|termina.|*Habito*|fica." posts/AAAA-MM-DD/frase.jpg
Linhas separadas por |; o destaque (uma palavra ou expressao) entre *asteriscos*.
Saida .jpg (JPEG, exigido pelo Instagram) ou .png. Fontes em fonts/ (DM Serif Display).
Nao altere cores, fonte nem posicoes (padrao visual aprovado pelo Afonso)."""
import sys, os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
REG_F = os.path.join(AQUI, "fonts", "DMSerifDisplay-Regular.ttf")
ITA_F = os.path.join(AQUI, "fonts", "DMSerifDisplay-Italic.ttf")
W, H = 1080, 1350
FUNDO, AZUL, BRONZE = (234, 234, 234), (15, 45, 71), (140, 98, 57)
MAXW, TOPO, BASE = 900, 110, 1240      # area util do bloco de texto
CENTRO = 640                           # centro vertical do bloco


def partes(linha):
    return [(p, i % 2 == 1) for i, p in enumerate(linha.split('*')) if p]


def largura(d, linha, reg, ita):
    return sum(d.textlength(t, font=ita if h else reg) for t, h in partes(linha))


def main(texto, saida):
    linhas = [l.strip() for l in texto.split('|') if l.strip()]
    img = Image.new('RGB', (W, H), FUNDO)
    d = ImageDraw.Draw(img)
    size = 164
    while True:
        reg = ImageFont.truetype(REG_F, size)
        ita = ImageFont.truetype(ITA_F, size)
        lh = round(size * 1.06)
        bloco = 6 + 44 + lh * len(linhas)
        if (max(largura(d, l, reg, ita) for l in linhas) <= MAXW
                and bloco <= BASE - TOPO) or size <= 60:
            break
        size -= 4
    y = max(TOPO, min(CENTRO - bloco // 2, BASE - bloco))
    d.rectangle([W // 2 - 48, y, W // 2 + 48, y + 6], fill=BRONZE)
    y += 6 + 44
    asc, desc = reg.getmetrics()
    for l in linhas:
        x = (W - largura(d, l, reg, ita)) / 2
        base = y + (lh - (asc + desc)) / 2
        for t, h in partes(l):
            f = ita if h else reg
            d.text((x, base), t, font=f, fill=BRONZE if h else AZUL)
            x += d.textlength(t, font=f)
        y += lh
    os.makedirs(os.path.dirname(os.path.abspath(saida)), exist_ok=True)
    if saida.lower().endswith(('.jpg', '.jpeg')):
        img.save(saida, 'JPEG', quality=95, subsampling=0)
    else:
        img.save(saida)
    print('ok', saida, 'fonte', size, 'linhas', len(linhas))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
