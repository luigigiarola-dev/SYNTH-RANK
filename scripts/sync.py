"""Atualiza ranking a partir das páginas públicas do Achikochi Data.
Requer requests e beautifulsoup4. Falha sem substituir o último snapshot válido.
"""
import json, re, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

ROOT='https://achikochi-data.com/youtube_video_ranking_vocaloid/'
OUT=Path(__file__).resolve().parents[1]/'ranking.json'
session=requests.Session()
session.headers.update({'User-Agent':'Mozilla/5.0 (compatible; SynthRankPersonalProject/1.0; public ranking reader)'})

def soup(url):
    r=session.get(url,timeout=25)
    r.raise_for_status()
    return BeautifulSoup(r.text,'html.parser')

def views_number(raw):
    raw=raw.replace(',','').replace(' ','')
    total=0
    for n,unit in re.findall(r'(\d+(?:\.\d+)?)(億|万)',raw):
        total+=float(n)*(100000000 if unit=='億' else 10000)
    return int(total) if total else None

def video_id(detail):
    # Páginas de detalhes possuem link explícito para o vídeo do YouTube.
    for a in detail.select('a[href]'):
        url=a.get('href','')
        if 'youtube.com/watch' in url:
            candidate=parse_qs(urlparse(url).query).get('v',[''])[0]
            if re.fullmatch(r'[A-Za-z0-9_-]{11}',candidate):return candidate
        if 'youtu.be/' in url:
            candidate=urlparse(url).path.strip('/').split('/')[0]
            if re.fullmatch(r'[A-Za-z0-9_-]{11}',candidate):return candidate
    for tag in detail.select('iframe[src]'):
        match=re.search(r'/embed/([\w-]{11})',tag['src'])
        if match:return match.group(1)
    return None

def main():
    page=soup(ROOT)
    rows=[]
    for tr in page.select('tr'):
        cols=tr.find_all('td')
        if len(cols)<3:continue
        m=re.search(r'(\d+)\s*位',cols[0].get_text(' ',strip=True))
        if not m:continue
        rank=int(m.group(1))
        if rank>100:continue
        detail_link=cols[1].select_one('a[href*="/content/youtube_video/"]')
        if not detail_link:continue
        views=views_number(cols[-1].get_text(' ',strip=True))
        if views is None:continue
        title=detail_link.get_text(' ',strip=True)
        raw=cols[1].get_text(' ',strip=True)
        channel=re.search(r'チャンネル名\s*[:：]\s*(.*?)\s*動画投稿日',raw)
        artist=channel.group(1).strip() if channel else '—'
        rows.append({'rank':rank,'title':title,'artist':artist,'views':views,'detailUrl':urljoin(ROOT,detail_link['href'])})
    if len(rows)<95:raise RuntimeError(f'Página não retornou Top 100 válido: {len(rows)} linhas')
    old={}
    if OUT.exists():
        try:old={s['detailUrl']:s.get('videoId') for s in json.loads(OUT.read_text())['songs']}
        except (KeyError,ValueError):pass
    missing=0
    for i,row in enumerate(rows):
        vid=old.get(row['detailUrl'])
        if not vid:
            try:vid=video_id(soup(row['detailUrl']))
            except requests.RequestException as e:print('Detalhe indisponível:',row['rank'],e,file=sys.stderr)
            time.sleep(.35)
        row['videoId']=vid
        if not vid:missing+=1
    if missing>10:raise RuntimeError(f'IDs insuficientes: {missing} não resolvidos; snapshot preservado')
    date_match=re.search(r'集計日\s*[:：]\s*(\d{4})/(\d{1,2})/(\d{1,2})',page.get_text(' ',strip=True))
    source_date='-'.join([date_match.group(1),date_match.group(2).zfill(2),date_match.group(3).zfill(2)]) if date_match else None
    payload={'source':ROOT,'sourceDate':source_date,'songs':sorted(rows,key=lambda s:s['rank'])}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Atualizado:',len(rows),'músicas;',missing,'sem link; fonte:',source_date)

if __name__=='__main__':main()
