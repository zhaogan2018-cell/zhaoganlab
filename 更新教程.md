# 网站更新教程

## 第一次替换网站
1. 打开 GitHub Desktop，File → Clone repository，选择 zhaogan2018-cell/zhaoganlab。
2. 点击 Fetch origin，确保本地同步。Branch → New branch，创建 website-content-update。
3. Repository → Show in Explorer 打开仓库。另行备份旧文件。
4. 将“网站更新完整包”内所有文件和文件夹复制到仓库根目录，选择替换。不要把整个外层文件夹放进去。包含隐藏目录 .github 和 .nojekyll；保留 CNAME。
5. 在 GitHub Desktop 检查 Changes，填写说明，Commit，再 Publish branch。
6. Create Pull Request，在 GitHub 查看修改，确认后 Merge。等待仓库 Actions 的 Pages 部署完成。
7. 打开 https://www.zhaoganlab.cn，Ctrl+Shift+R 强制刷新，逐页检查手机和电脑显示。

## 本地预览
双击“启动预览.cmd”，保持窗口打开，然后浏览器访问 http://localhost:8000。需要已安装 Node.js。不要直接双击 HTML：成员、新闻与论文由 JSON 加载，须通过本地 HTTP 服务。

## 更新成员
1. 照片放入 assets/photos，使用英文文件名与 jpg/png 格式。
2. 打开 content/people.json，复制一个成员对象。
3. 修改 name/name_zh、role/role_zh、image、year。group 为 0=PI、1=实验室管理、2=博士后、3=博士生、4=硕士生。
4. 同组按 year 升序排列；同年按文件内顺序。博士后入组时间尚无素材依据，补入真实年份后即可自动排序。
5. 毕业成员从 people.json 移除，在 alumni.json 中添加 {"name":"姓名","destination":"毕业年份 · 去向"}。
6. JSON 的对象之间加逗号，最后一个对象后不加逗号。

## 更新新闻
1. 编辑 content/news.json，复制已有对象，填写 date（YYYY 或 YYYY-MM-DD）、category、title/title_zh、summary/summary_zh、image。
2. category 使用 学术动态 / 研究进展 / 团队活动。仅有年份的活动不要虚构具体日期。
3. 照片放 assets/photos。按日期倒序显示。可用 url 添加原始报道链接。

## 更新研究成果
1. 编辑 content/publications.json，复制条目，填写唯一 id、year、title、authors、journal、citation、pmid、doi。
2. kind=featured 表示一作/通讯，collaborative 表示合作。确认共同贡献和通讯符号。
3. figure 指向论文原图文件；figure_source 记录原文页面。可替换为自己选取且有使用权限的原文小图；科研图用 contain 展示，避免裁切坐标或图例。
4. 自动下载图选取原文首幅可用图，未作科学内容改绘；如需特定 panel，请替换为保留标尺、标注的高分辨率裁图。

## 修改方向、环境、合作团队、联系
研究方向：research.html；主页：index.html；环境与合作：join.html；联系：contact.html。页面中文与英文分别位于 data-zh/data-en 属性，修改时两种都更新。页眉背景在 assets/photos/header-*.jpg；通用样式在 assets/css/style.css。字体沿用旧版。

## 自动化与 AI 协助
原有 .github/workflows/pubmed-sync.yml 与 scripts/sync_pubmed.py 已保留：按计划检索 PubMed，候选论文进入 content/pubmed_candidates.json。先核对身份和作者贡献，再移入 publications.json。不要将同名作者检索结果自动发布。
每次更新可把新素材交给 Codex，说明：“按更新教程维护此仓库；核实事实和论文图片来源，更新 JSON，运行检查，生成供我审核的分支。”不需要网站 API 密钥。当前未配置付费 AI 服务，也未启动无人值守发布。

## 回退
GitHub 上找到这次合并的 Pull Request，使用 Revert 创建回退 PR 并合并；或者在 GitHub Desktop 恢复备份后重新提交。不要删除 CNAME 或改动域名设置。

## 本次素材与待补信息
成员身份、年份按用户提供照片文件名；同年先后顺序未提供。实验室助理按用户指定管理岗位顺序展示，具体职称仍写“实验室助理”。未补写仪器型号、未提供的学术活动、研究进展和毕业去向。合作关系按用户说明录入。联系页面正文保留原版，仅使用指定背景。

本次更新：news.json 支持 images 图片路径数组，照片按数组顺序组成相册，点击可查看原图。研究方向以未来方向为主，前期基础引用在 research.html 中维护。全部论文配图以 figure/figure_source 维护。

首页方向卡片现为白色关键词，完整说明在 research.html；关键词修改 index.html 中 research-tile 的 data-zh/data-en。导航logo使用 assets/photos/lab-logo.jpg（用户新增Lablogo1.jpg），CSS负责留白裁切；头像宽度在style.css末尾统一控制。
