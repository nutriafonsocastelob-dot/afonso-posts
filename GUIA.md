# GUIA OPERACIONAL — @nutriafonsocastelob

As regras de conteúdo estão em **PROMPT-MESTRE.md** (leia por inteiro, sempre). Este guia diz COMO executar.
Quando houver diferença entre os dois, vale este guia nos pontos operacionais e visuais abaixo (decisões do Afonso).

## 1. Decisões já tomadas pelo Afonso
- Conta: Instagram @nutriafonsocastelob, via conector Windsor.ai (connector "instagram", account id 17841477775196341).
- Frequência: carrossel científico às segundas e sextas. Às quartas existe outra tarefa (frase), que não é sua. Não produza frases.
- Cor de base: **azul-marinho #0F2D47** com dourado/bronze da logo (gradiente #8C6034 → #FFE79F). Não use grafite. Não invente cores.
- Fonte das artes: Montserrat (já em fonts/). Templates e logos já recortados em brand/.
- Publicação SÓ depois do "aprovado" explícito do Afonso na conversa (seção 17 do prompt mestre).

## 2. Passo a passo de cada execução
1. Leia PROMPT-MESTRE.md, este GUIA.md e historico.md por inteiro.
2. Confira a data de hoje (America/Maceio). Se já houver linha no historico.md com a data de hoje, pare e avise.
3. Leia os últimos posts do perfil com Windsor `get_data` (connector instagram; chame `get_fields` antes) para evitar repetição e, quando houver métricas, use-as para orientar o tema (seção 19).
4. Escolha o tema respeitando a distribuição mensal (conte no historico.md os eixos do mês). Pesquise com WebSearch/WebFetch (PubMed, Cochrane, periódicos, diretrizes). Registre título, autor, periódico, ano e DOI/link de cada fonte que você realmente abriu. Se não conseguir confirmar, troque de tema.
5. Escreva o carrossel (5 a 8 slides) num arquivo posts/AAAA-MM-DD/post.json e a legenda em posts/AAAA-MM-DD/legenda.txt (com referências no fim). Hashtags: no máximo 5, só se pertinentes.
6. Gere as imagens: `python3 render.py posts/AAAA-MM-DD/post.json posts/AAAA-MM-DD` (gera slide-01.jpg…; se faltar Pillow: `pip install --break-system-packages pillow`). Abra CADA imagem com Read e confira: texto inteiro, sem corte, acentos certos, legível no celular. Corrija e gere de novo se preciso.
7. Faça as duas auditorias (científica e linguística) e o checklist da seção 20.
8. Faça commit e push da pasta do post e confirme que cada URL raw responde (curl -sI → 200, content-type image/jpeg):
   https://raw.githubusercontent.com/<DONO>/<REPO>/main/posts/AAAA-MM-DD/slide-01.jpg
9. Acrescente a linha no historico.md com status "aguardando aprovação" e faça push.
10. Mostre ao Afonso: todas as imagens com SendUserFile (display "render", status "proactive", na ordem), depois a legenda completa exatamente como será publicada com SendUserMessage, e as fontes. Peça a aprovação explícita. Termine a vez aqui.
11. Quando ele responder:
    - Pediu ajuste → refaça, gere de novo, faça push, mostre de novo.
    - "Aprovado" (ou equivalente explícito) → publique com Windsor `execute_action`, action `create_carousel_post` (ou `create_image_post` para post único), account 17841477775196341, params { image_urls: [URLs raw na ordem], caption: legenda aprovada }. Use exatamente a versão aprovada.
    - Informe o resultado real retornado. Se falhar, diga que falhou e o erro. Atualize o historico.md (publicado + media_id, ou o erro) e faça push.

## 3. Formato do post.json (render.py)
Tipos de slide: capa, texto, lista, imagem, final. Destaque dourado: palavras entre *asteriscos* (use com moderação: 1 a 3 palavras por slide).
- capa: tag, titulo (curto, gancho), sub (opcional)
- texto: tag, titulo, corpo (use \n para parágrafo; máx. ~45 palavras)
- lista: tag, titulo, itens (3 a 5, curtos)
- imagem: tag, titulo, imagem (arquivo na pasta do post, PNG com fundo transparente ou JPG), legenda (curta)
- final: titulo, corpo, cta (curto, cabe em uma linha)
Todos os slides são azul-marinho (o Afonso não quer slides de fundo branco). Crie ritmo variando o tipo de slide (texto, lista, imagem/esquema), não a cor.
Imagens de apoio (esquemas fisiológicos, moléculas, gráficos): desenhe você mesmo em código (SVG/matplotlib) com as cores da marca. Não baixe fotos da internet nem de pessoas.

## 4. Limites do Instagram/Windsor
JPEG, até 8 MB, proporção 4:5 (1080×1350), 2 a 10 imagens no carrossel, legenda até 2.200 caracteres.
