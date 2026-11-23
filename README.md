# SYNTHRANK — versão simples

Site HTML/CSS/JS com thumbnails do YouTube, links diretos e dados do Achikochi Data.

## Uso imediato
Abra `index.html`. Sem instalação, ele exibe o ranking histórico de 100 músicas. Se `ranking.json` existir e for servido por HTTP, o site carrega a versão sincronizada com links diretos e thumbnails.

## Atualização diária, sem chave API
1. Crie um repositório no GitHub e envie **todos** os arquivos, inclusive a pasta `.github`.
2. Em **Actions**, habilite workflows e execute **Atualizar ranking Vocaloid → Run workflow** pela primeira vez.
3. Em **Settings → Pages**, publique a branch `main`, pasta `/ (root)`.
4. O GitHub Actions executará diariamente às 13:30 UTC. O arquivo `ranking.json` será atualizado e publicado automaticamente após o commit.

**Importante:** um arquivo HTML aberto diretamente (`file://`) não pode sincronizar com o site de terceiros. GitHub Pages é gratuito para repositórios públicos, sujeito às políticas e limites do GitHub. O script lê a página pública e depois a página de detalhes de cada música para descobrir o ID exato do YouTube. A fonte pode mudar o HTML, limitar acessos ou bloquear a coleta; nesse caso o workflow falhará sem substituir o último arquivo válido. Verifique os termos e `robots.txt` da fonte antes de publicar uma rotina de coleta recorrente. A atualização é diária, não em tempo real. Não há garantia de execução no horário exato.

## Miniaturas e vídeos
O script extrai IDs dos links reais do YouTube presentes nas páginas individuais da fonte; thumbnails são carregadas de `i.ytimg.com/vi/VIDEO_ID/mqdefault.jpg`. Nunca usa busca do YouTube para abrir uma música. Até a primeira sincronização, entradas sem ID não apresentam botão de vídeo, para não criar links errados.

## Origem
https://achikochi-data.com/youtube_video_ranking_vocaloid/
