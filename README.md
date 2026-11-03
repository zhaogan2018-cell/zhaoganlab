# Gan Zhao Lab website

Static bilingual website for https://www.zhaoganlab.cn/ hosted by GitHub Pages.

## Deploy

Upload all files/folders to the root of the existing `zhaogan2018-cell/zhaoganlab` repository (keep its Pages settings). The `CNAME` file preserves the custom domain. GitHub Pages will deploy the changes after committing to `main` if it is configured to deploy from that branch.

## Routine editing

- **Research, team, header, Chinese/English copy:** Edit the `translations` object in `assets/site.js`.
- **Publications:** Edit the `publications` array in `assets/site.js` using verified `year`, `title`, `journal`, and full DOI URL.
- **News:** Edit the `news` array in `assets/site.js` with `date`, `en`, and `zh` text.
- **Colors and layout:** Edit `assets/style.css`.
- **Images:** Replace the abstract placeholder graphics with approved images; make sure to add alt text.

No build step or paid server required. Preview by opening `index.html` locally; deployment uses GitHub Pages. Avoid publishing unpublished results, private contact details, or member identities without approval.
