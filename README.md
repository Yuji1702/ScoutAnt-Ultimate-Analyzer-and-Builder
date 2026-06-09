# ScoutAnt-Ultimate-Analyzer-and-Builder

**ScoutAnt** is a comprehensive Valorant match data analyzer and team-building assistant. This tool helps you evaluate player performance, agent efficiency, map stats, and suggest optimal team compositions. It's ideal for players, team coaches, or analysts who want a tactical edge.

---

## 🎯 Objective

The main goal of this project is to build an **intelligent system that scrapes, analyzes, and visualizes Valorant player and match data** to assist in:

- Understanding team and player strengths/weaknesses.
- Making informed decisions on agent and map strategies.
- Building optimized 5-man team compositions for specific maps.
- Predicting potential win/loss outcomes based on previous patterns.

ScoutAnt aims to become the **go-to pre-match planning and post-match review tool** for competitive Valorant environments.

---

## ✅ Current Progress

### ✅ Completed Features:
- 🔍 **Player Match History Scraper** – Extracts player data from publicly available sources (e.g., Tracker.gg).
- 🔧 **Modular Codebase** – Code is being structured into reusable components (scrapers, analyzers, visualizers)

---

## 🚧 Upcoming Features:
- 🧠 Win Probability Predictor using machine learning.
- 📈 Enhanced visual dashboards (via Plotly/Matplotlib).
- 📂 Exportable reports (PDF/HTML formats).
- 🕵️‍♂️ Integration with official APIs (if/when available).
- 💡 Real-time suggestions based on meta trends.
- 📊 **Statistical Analysis Module** – Computes player averages, KD ratio, ACS, agent win rates, and more.
- 🗺️ **Map-Agent Breakdown** – Visual representation of agent usage per map.
- 🧮 **Team Performance Metrics** – Calculates overall team synergy and performance based on past data.


---

## 📦 Installation

Clone and set up the project locally:

```bash
git clone https://github.com/Yuji1702/ScoutAnt-Ultimate-Analyzer-and-Builder.git
cd ScoutAnt-Ultimate-Analyzer-and-Builder

## Git Push with Git LFS

This repository already includes Git LFS patterns in `.gitattributes` for large files (e.g. `*.pkl`, `*.parquet`, `*.json`, and `match_stats_db.json`). To prepare and push the repository to GitHub with LFS-managed files, you can use the provided helper scripts in the `scripts/` folder.

- PowerShell (Windows):

```powershell
.
scripts/setup_and_push_git_lfs.ps1 -remote "https://github.com/OWNER/REPO.git"
```

- Bash (Linux/macOS/WSL):

```bash
scripts/setup_and_push_git_lfs.sh https://github.com/OWNER/REPO.git
```

What the helper scripts do:
- Run `git lfs install`.
- Ensure `.gitattributes` is staged.
- Stage all changes and commit (if any).
- Optionally add the `origin` remote if provided.
- Push the current branch to `origin`.

If you prefer to run commands manually, these are the steps:

```bash
git lfs install
git add .gitattributes
git add -A
git commit -m "Prepare repo and track large files with Git LFS"
git remote add origin https://github.com/OWNER/REPO.git   # if not set
git push -u origin main
```

Replace `https://github.com/OWNER/REPO.git` with your repository URL and `main` with your default branch if different.

