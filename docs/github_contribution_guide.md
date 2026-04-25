# GitHub Setup & Contribution Guide — DVA_B1_T3

## Step 1 — Create the repo (Project Lead only)
1. Go to github.com → New repository
2. Name: `DVA_B1_T3_OnlineRetailAnalytics`
3. Visibility: **Public** | Initialize with README: Yes → Create

## Step 2 — Add all 5 members as collaborators
Repo Settings → Collaborators → Add by GitHub username → Role: Write

## Step 3 — Branch ownership (so everyone gets commits for marks)

| Member | Branch | Owns |
|---|---|---|
| Rudransh Gupta | `feat/etl-pipeline` | scripts/, notebooks/01, notebooks/02 |
| Rounak Kumar Saw | `feat/eda` | notebooks/03 |
| Pankaj Yadav | `feat/statistical-analysis` | notebooks/04 |
| Priyabrata Singh | `feat/final-load-tableau` | notebooks/05, tableau/ |
| Priyanshu Verma | `feat/report-docs` | reports/, docs/, README.md |

Each member runs:
```bash
git checkout -b feat/YOUR-BRANCH-NAME
git push -u origin feat/YOUR-BRANCH-NAME
# Do your work → commit → open Pull Request into main → another member reviews → merge
```

## Minimum required per member (for marks)
- ≥ 3 commits on their branch
- ≥ 1 merged Pull Request into main
- ≥ 1 PR review on someone else's PR

## Commit the raw dataset (Member 1)
```bash
# After downloading online_retail_II_raw.csv into data/raw/:
git add data/raw/online_retail_II_raw.csv
git commit -m "data: add raw Online Retail II dataset (UCI)"
git push
```
> If file size > 100MB run `git lfs install && git lfs track "*.csv"` first.

## After running notebooks, commit processed outputs (Member 4)
```bash
git add data/processed/
git add reports/*.png
git commit -m "data: add cleaned dataset and KPI exports"
git push
```

## Commit message convention
| Prefix | Use for |
|---|---|
| `feat:` | New notebook section or feature |
| `fix:` | Bug fix |
| `data:` | Data files |
| `docs:` | README, dictionary, report |
| `viz:` | Tableau screenshots, charts |

## Final submission checklist
- [ ] All notebooks have visible outputs (Run All → Save → Commit)
- [ ] data/raw/ has the original unedited CSV
- [ ] data/processed/ has all 6 CSVs committed
- [ ] tableau/dashboard_links.md has the live Tableau Public URL
- [ ] tableau/screenshots/ has ≥ 3 dashboard screenshots
- [ ] docs/data_dictionary.md is fully filled
- [ ] reports/project_report.pdf committed
- [ ] reports/presentation.pdf committed
- [ ] Every member has ≥ 3 commits and ≥ 1 merged PR
- [ ] Repository is Public
