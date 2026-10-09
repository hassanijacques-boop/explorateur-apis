#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrait les APIs du README de public-apis et genere une page HTML de recherche."""
import re, json, html, pathlib

SRC = pathlib.Path("/workspace/public-apis/README.md")
OUT_JSON = pathlib.Path("/workspace/public-apis/api_data.json")
OUT_HTML = pathlib.Path("/workspace/public-apis/index.html")

texte = SRC.read_text(encoding="utf-8", errors="ignore")

# 1) decouper par categorie (### Nom)
blocs = re.split(r"^### (.+)$", texte, flags=re.M)
categories = {}
courante = None
for i in range(1, len(blocs), 2):
    nom = blocs[i].strip()
    corps = blocs[i+1]
    lignes = []
    for ligne in corps.split("\n"):
        # | [Nom](url) | Description | Auth | HTTPS | CORS |
        m = re.match(r"^\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|(.+)$", ligne.strip())
        if m:
            nom_api = m.group(1).strip()
            url = m.group(2).strip()
            reste = [c.strip() for c in m.group(3).split("|")]
            desc   = reste[0] if len(reste) > 0 else ""
            auth   = reste[1] if len(reste) > 1 else ""
            https  = reste[2] if len(reste) > 2 else ""
            cors   = reste[3] if len(reste) > 3 else ""
            api = {"n": nom_api, "u": url, "d": desc, "a": auth, "h": https, "c": cors}
            # liens associes (?/? = doc, /!\\ = impossible)
            for marque, cle in [("?/?", "doc"), ("/!\\\\", "nocors")]:
                if marque in reste:
                    api[cle] = True
            lignes.append(api)
    if lignes:
        # exclure les blocs publicitaires / parasites du README
        bas = nom.lower()
        if any(x in bas for x in ["apilayer", "sponsor", "covered under"]):
            print(f"  [exclue] bloc publicitaire : {nom} ({len(lignes)} entrees)")
            continue
        if len(lignes) < 3:
            print(f"  [exclue] bloc trop petit : {nom} ({len(lignes)} entrees)")
            continue
        categories[nom] = lignes

total = sum(len(v) for v in categories.values())
print(f"  {len(categories)} categories, {total} APIs extraites")

# 2) JSON
OUT_JSON.write_text(json.dumps(categories, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"  JSON : {OUT_JSON.stat().st_size//1024} Ko")

# 3) HTML
data_js = json.dumps(categories, ensure_ascii=False)

CAT_COLORS = {
    "Animals":"#22d3ee","Anime":"#f472b6","Anti-Malware":"#ef4444","Art & Design":"#a855f7",
    "Authentication & Authorization":"#6366f1","Blockchain":"#f59e0b","Books":"#84cc16",
    "Business":"#0ea5e9","Calendar":"#14b8a6","Cloud Storage & File Sharing":"#3b82f6",
    "Continuous Integration":"#8b5cf6","Cryptocurrency":"#eab308","Currency Exchange":"#10b981",
    "Data Validation":"#06b6d4","Development":"#64748b","Dictionaries":"#f97316",
    "Documents & Productivity":"#ec4899","Email":"#8b5cf6","Entertainment":"#d946ef",
    "Environment":"#22c55e","Events":"#f43f5e","Finance":"#16a34a","Food & Drink":"#fb923c",
    "Games & Comics":"#a3e635","Geocoding":"#0d9488","Government":"#475569",
    "Health":"#dc2626","Jobs":"#7c3aed","Machine Learning":"#6366f1","Music":"#c026d3",
    "News":"#0891b2","Open Data":"#0e7490","Open Source Projects":"#059669",
    "Patent":"#6d28d9","Personality":"#db2777","Phone":"#2563eb","Photography":"#7c3aed",
    "Programming":"#334155","Science & Math":"#0284c7","Security":"#b91c1c",
    "Shopping":"#ea580c","Social":"#e11d48","Sports & Fitness":"#65a30d",
    "Test Data":"#0f766e","Text Analysis":"#4f46e5","Tracking":"#dc2626",
    "Transportation":"#1d4ed8","URL Shorteners":"#7c3aed","Vehicle":"#a16207",
    "Video":"#be123c","Weather":"#0891b2",
}

def couleur(cat):
    return CAT_COLORS.get(cat, "#a855f7")

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Public APIs — explorer 2 058 APIs gratuites</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;background:#05050a;color:#fff;min-height:100vh}
.halo{position:fixed;border-radius:50%;filter:blur(100px);opacity:.4;z-index:0;pointer-events:none}
.h1{width:520px;height:520px;background:#a855f7;top:-160px;left:-120px;animation:fl 20s ease-in-out infinite}
.h2{width:460px;height:460px;background:#22d3ee;top:120px;right:-140px;animation:fl 26s ease-in-out infinite reverse}
@keyframes fl{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(80px,60px) scale(1.15)}}
.wrap{position:relative;z-index:2;max-width:1400px;margin:0 auto;padding:44px 24px 90px}
header{text-align:center;margin-bottom:38px}
h1{font-size:clamp(26px,5vw,46px);font-weight:800;letter-spacing:-.03em}
h1 span{background:linear-gradient(100deg,#22d3ee,#a855f7,#f472b6);-webkit-background-clip:text;background-clip:text;color:transparent}
.sous{color:#ffffff66;margin-top:12px;font-size:15px}
.stats{display:flex;gap:26px;justify-content:center;margin-top:22px;flex-wrap:wrap}
.stat{background:#ffffff0d;border:1px solid #ffffff1a;border-radius:14px;padding:12px 22px;backdrop-filter:blur(14px)}
.stat b{display:block;font-size:23px;background:linear-gradient(100deg,#22d3ee,#a855f7);-webkit-background-clip:text;background-clip:text;color:transparent}
.stat span{font-size:11.5px;color:#ffffff5e;text-transform:uppercase;letter-spacing:.12em}
.bar{position:sticky;top:0;z-index:20;padding:18px 0;background:#05050aee;backdrop-filter:blur(20px);border-bottom:1px solid #ffffff12;margin:0 -24px 26px;padding-left:24px;padding-right:24px}
.search{position:relative;max-width:760px;margin:0 auto}
.search input{width:100%;padding:17px 22px 17px 52px;border-radius:16px;border:1px solid #ffffff1f;
  background:#ffffff0d;color:#fff;font-size:15.5px;outline:none;backdrop-filter:blur(14px);transition:.3s}
.search input:focus{border-color:#a855f780;background:#ffffff14;box-shadow:0 0 0 4px #a855f71f}
.search input::placeholder{color:#ffffff45}
.search svg{position:absolute;left:19px;top:50%;transform:translateY(-50%);opacity:.45}
.filtres{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:15px;max-height:118px;overflow-y:auto}
.filtres::-webkit-scrollbar{width:6px}.filtres::-webkit-scrollbar-thumb{background:#ffffff20;border-radius:3px}
.fbtn{padding:7px 15px;border-radius:999px;border:1px solid #ffffff1c;background:#ffffff09;color:#ffffffb0;
  font-size:12.5px;cursor:pointer;transition:.22s;white-space:nowrap}
.fbtn:hover{background:#ffffff16;color:#fff}
.fbtn.on{background:linear-gradient(100deg,#22d3ee,#a855f7);color:#fff;border-color:transparent;font-weight:600}
.grille{display:grid;grid-template-columns:repeat(auto-fill,minmax(325px,1fr));gap:15px}
.carte{background:#ffffff08;border:1px solid #ffffff12;border-radius:18px;padding:20px;transition:.3s;position:relative;overflow:hidden}
.carte:hover{background:#ffffff0f;border-color:#ffffff26;transform:translateY(-3px)}
.carte::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--c);opacity:.85}
.cat{display:inline-block;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--c);background:color-mix(in srgb,var(--c) 15%,transparent);border-radius:999px;padding:4px 11px;margin-bottom:11px}
.carte h3{font-size:16.5px;margin-bottom:7px;letter-spacing:-.01em}
.carte h3 a{color:#fff;text-decoration:none}
.carte h3 a:hover{color:var(--c)}
.carte p{color:#ffffff70;font-size:13.5px;line-height:1.55;margin-bottom:13px;min-height:38px}
.tags{display:flex;gap:7px;flex-wrap:wrap}
.tag{font-size:11px;padding:3px 10px;border-radius:7px;border:1px solid #ffffff1a;color:#ffffff8a;background:#ffffff08}
.tag.ok{border-color:#22c55e55;color:#4ade80;background:#22c55e14}
.tag.no{border-color:#ef444455;color:#f87171;background:#ef444414}
.vide{text-align:center;color:#ffffff45;padding:70px 20px;font-size:15px;grid-column:1/-1}
footer{text-align:center;color:#ffffff35;font-size:12.5px;margin-top:60px;line-height:1.9}
footer a{color:#a855f7;text-decoration:none}
.compteur{text-align:center;color:#ffffff50;font-size:13px;margin-bottom:20px}
</style>
</head>
<body>
<div class="halo h1"></div><div class="halo h2"></div>
<div class="wrap">
<header>
  <h1>Public <span>APIs</span></h1>
  <p class="sous">Explorateur des APIs publiques gratuites — données du repo public-apis (486 921 ⭐, licence MIT)</p>
  <div class="stats">
    <div class="stat"><b id="s-api">—</b><span>APIs</span></div>
    <div class="stat"><b id="s-cat">—</b><span>catégories</span></div>
    <div class="stat"><b id="s-grat">—</b><span>sans clé</span></div>
  </div>
</header>
<div class="bar">
  <div class="search">
    <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
    <input id="q" type="search" placeholder="Rechercher une API…  (météo, avions, devises, images…)" autocomplete="off">
  </div>
  <div class="filtres" id="filtres"></div>
</div>
<p class="compteur" id="compteur"></p>
<div class="grille" id="grille"></div>
<footer>
  Source : <a href="https://github.com/public-apis/public-apis" target="_blank">github.com/public-apis/public-apis</a> — MIT<br>
  Interface générée automatiquement · 2 058 APIs · mise à jour avec le repo
</footer>
</div>
<script>
const DATA = __DATA__;
const COULEURS = __COULEURS__;
const API_URL = "https://github.com/public-apis/public-apis";

const toutes = [];
for (const [cat, list] of Object.entries(DATA)) {
  for (const a of list) toutes.push({...a, cat});
}
document.getElementById('s-api').textContent = toutes.length.toLocaleString('fr-FR');
document.getElementById('s-cat').textContent = Object.keys(DATA).length;
document.getElementById('s-grat').textContent = toutes.filter(a => (a.a||'').toLowerCase() === 'no').length.toLocaleString('fr-FR');

const catsOrdonnees = Object.keys(DATA).sort((a,b) => DATA[b].length - DATA[a].length);
const fd = document.getElementById('filtres');
const tousBtn = document.createElement('button');
tousBtn.className = 'fbtn on'; tousBtn.textContent = 'Toutes';
tousBtn.onclick = () => { catActive = null; maj(); };
fd.appendChild(tousBtn);
catsOrdonnees.forEach(c => {
  const b = document.createElement('button');
  b.className = 'fbtn';
  b.textContent = c + ' (' + DATA[c].length + ')';
  b.dataset.cat = c;
  b.onclick = () => { catActive = (catActive === c) ? null : c; maj(); };
  fd.appendChild(b);
});
let catActive = null;

const grille = document.getElementById('grille');
const compteur = document.getElementById('compteur');
const champ = document.getElementById('q');

function normale(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}

function affiche() {
  const q = normale(champ.value.trim());
  let res = toutes.filter(a => {
    if (catActive && a.cat !== catActive) return false;
    if (!q) return true;
    return normale(a.n).includes(q) || normale(a.d).includes(q) || normale(a.cat).includes(q);
  });
  compteur.textContent = res.length.toLocaleString('fr-FR') + ' API' + (res.length > 1 ? 's' : '') + ' affichée' + (res.length > 1 ? 's' : '');
  if (!res.length) { grille.innerHTML = '<p class="vide">Aucun résultat.<br>Essayez un autre mot-clé.</p>'; return; }
  grille.innerHTML = res.slice(0, 400).map(a => {
    const c = COULEURS[a.cat] || '#a855f7';
    const auth = (a.a||'').toLowerCase();
    const tAuth = auth === 'no' ? '<span class="tag ok">Sans clé</span>' : '<span class="tag">Clé API</span>';
    const tHttps = (a.h||'').toLowerCase() === 'yes' ? '<span class="tag ok">HTTPS</span>' : '<span class="tag">HTTP</span>';
    const tCors = (a.c||'').toLowerCase() === 'yes' ? '<span class="tag ok">CORS</span>'
                 : (a.c||'').toLowerCase() === 'no' ? '<span class="tag no">Pas de CORS</span>' : '<span class="tag">CORS ?</span>';
    return `<article class="carte" style="--c:${c}">
      <span class="cat">${a.cat}</span>
      <h3><a href="${a.u}" target="_blank" rel="noopener">${a.n} ↗</a></h3>
      <p>${a.d || '—'}</p>
      <div class="tags">${tAuth}${tHttps}${tCors}</div>
    </article>`;
  }).join('');
  if (res.length > 400) grille.innerHTML += '<p class="vide">… affinez votre recherche (plus de 400 résultats)</p>';
}

function maj(){ tousBtn.classList.toggle('on', !catActive);
  document.querySelectorAll('.fbtn[data-cat]').forEach(b => b.classList.toggle('on', b.dataset.cat === catActive));
  affiche(); }

champ.addEventListener('input', affiche);
affiche();
</script>
</body>
</html>"""

HTML = HTML.replace("__DATA__", data_js).replace("__COULEURS__", json.dumps(CAT_COLORS, ensure_ascii=False))
OUT_HTML.write_text(HTML, encoding="utf-8")
print(f"  HTML : {OUT_HTML.stat().st_size//1024} Ko")
print("\n  Apercu des 8 plus grosses categories :")
for c in sorted(categories, key=lambda k: -len(categories[k]))[:8]:
    print(f"    {c:42s} {len(categories[c]):>4} APIs")
