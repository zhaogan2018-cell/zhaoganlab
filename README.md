# Gan Zhao Lab — Official website

Bilingual, multi-page, static website for **www.zhaoganlab.cn**. Runs on **GitHub Pages**, no server required. Built with HTML/CSS/vanilla JS; each section is independent.

## 1. Files and maintenance

| Page/section | Where to edit |
| --- | --- |
| Homepage | `index.html` |
| Research | `research.html` |
| Publications | **`content/publications.json`** (no HTML editing needed) |
| People | **`content/people.json`** and photos under `assets/img/` |
| News | **`content/news.json`** |
| Join Us | `join.html` |
| Contact | `contact.html` |
| Shared navigation/footer, language toggle, publication filters | `assets/js/site.js` |
| Colors, spacing, typography, responsive design | `assets/css/style.css` |
| Automatic PubMed search | `scripts/sync_pubmed.py` + `.github/workflows/pubmed-sync.yml` |

Each page loads shared `assets/css/style.css` + `assets/js/site.js`. Upload all files and folders to the **root** of your current `zhaoganlab` repo (not into another nested folder). Preserve `CNAME` exactly as `www.zhaoganlab.cn`.

## 2. GitHub Desktop, safely

1. GitHub Desktop → **File → Clone repository** → `zhaogan2018-cell/zhaoganlab`.
2. **Branch → New branch** named `website-v2`. In GitHub Desktop use **Repository → Show in Explorer**.
3. Copy the *contents of this ZIP* to the cloned repository folder. Replace the old `index.html` and README. Ensure hidden `.github` folder is included; on Windows Explorer `View → Show → Hidden items` if needed.
4. Review changes → **Commit to website-v2** → **Publish branch**.
5. GitHub → compare & pull request → merge `website-v2` into `main` when satisfied. Existing GitHub Pages continues serving `main`, and after merge deploys the updated site.
6. Confirm at https://www.zhaoganlab.cn/ and https://www.zhaoganlab.cn/publications.html.

To preview locally (because browsers restrict `fetch()` from `file://`): from the website folder run `python -m http.server 8000` and open `http://localhost:8000/`. Or use VS Code Live Server.

## 3. Publications

There are 19 curated papers organized by **publication year, descending**. Five lead/co-first/corresponding author papers have unique original SVG thematic illustrations. These graphics are **not original figures from the articles**; replace images with your own permitted figures for authentic article images. Each article's title opens PubMed. When an exact PMID has been verified it links directly; other papers initially use a PubMed **exact-title search** URL until their PMID is resolved.

`content/publications.json` has 19 records and fields `year`, `title`, `authors`, `journal`, `citation`, `pmid`, `doi`, `topic`, `kind`, `figure`.

- `kind: "featured"`: lead/co-first/corresponding-author representative papers.
- `kind: "collaborative"`: other coauthored work.
- `figure`: a path like `assets/img/feature-01.svg`.
- Keep `#` (equal contribution) and `*` (corresponding author) only after checking the journal record. User-provided contribution annotations are included as provided.
- To add a paper, copy an existing JSON object, give it a unique `id`, and set the `year`. It will sort automatically.
- Use a JSON validator when editing, especially commas and double quotes.

## 4. Automatic PubMed sync — important distinctions

The GitHub Actions workflow `Update PubMed bibliography` runs each Monday and can also be run manually from **Actions → Update PubMed bibliography → Run workflow**. If the Actions tab asks to enable workflows, enable it. This workflow requests **read/write repository contents** permission. If blocked by repository policy, go to **Settings → Actions → General → Workflow permissions → Read and write permissions**, or use PR-based updates instead.

The script uses official NCBI E-utilities (ESearch and EFetch). It:

1. Looks up the **exact titles** of curated papers with missing PMIDs; it fills a PMID only when the normalized PubMed title matches and the author list contains Zhao.
2. For verified PMID/title pairs, fills any missing DOI, keeping the curated authorship and contribution markers unchanged.
3. Searches for potentially related publications under `Zhao G`/`Zhao Gan` and lung-related terms, and writes unmatched results to **`content/pubmed_candidates.json`** for your review. **These candidates do not appear on the public site.**
4. Writes the last update time to `content/pubmed_status.json`.

**To approve a new paper:** open `content/pubmed_candidates.json`, check the title, authors and PMID on PubMed (and verify it is really your work), then **manually add a record** to `content/publications.json` with its authors, year and contribution type. Do NOT automatically publish all results from `Zhao G` because this is ambiguous. No API key is required at the script's low request rate. The script uses a contact email and respects the NCBI no-key limit (3 requests/sec).

The script does not infer first or corresponding authorship from PubMed (such roles can be ambiguous). It does not update the displayed year, user-verified citation text or author-contribution annotations automatically.

## 5. People

Edit `content/people.json`. Each person should have:

```json
{
  "name": "Example Researcher",
  "name_zh": "示例成员",
  "role": "Graduate Student",
  "role_zh": "研究生",
  "bio": "Research interests...",
  "bio_zh": "研究方向……",
  "image": "assets/img/example.jpg",
  "email": ""
}
```

Add their photo file to `assets/img/`. Until confirmed, the website includes only Gan Zhao's public academic profile and a placeholder for colleagues. Do not publish private contact information or photos without permission.

## 6. News

Edit `content/news.json`, initially `[]`. Example object:

```json
{
  "date": "2026-11-04",
  "title": "A new publication",
  "title_zh": "新论文发表",
  "summary": "A brief English update.",
  "summary_zh": "简短中文消息。",
  "url": "https://pubmed.ncbi.nlm.nih.gov/38295183/"
}
```

No news has been invented; add items when confirmed.

## 7. Colors and fonts

XMU-inspired **royal blue**, teal and warm orange, plus clean white. Modern academic typography uses `Manrope`, `DM Sans`, and `Noto Sans SC` (fallback system sans-serif). Fonts are loaded from Google Fonts and will fall back locally if unavailable; no proprietary font files are distributed.

## 8. Troubleshooting

- If old content persists, hard-refresh Ctrl+Shift+R and check GitHub **Actions** for Pages deployment status. Cloudflare caching can also delay updates.
- If publications/people/news are empty when opening `index.html` locally as a file, preview with HTTP (`python -m http.server 8000`).
- `CNAME` must stay in the repository root; otherwise custom domain linkage may break.
- Featured SVG images are *original conceptual graphics*, not journal figures.
- This is a static site. For an editor UI later, add a Git-backed CMS, but it is not necessary for easy JSON updates.
