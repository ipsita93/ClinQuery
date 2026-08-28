# Publish this project on GitHub

The repo is meant to be **public**. There is no PHI and no credentials in the sample files.

## Fast path (GitHub CLI)

1. Install [GitHub CLI](https://cli.github.com/) and run `gh auth login`.
2. From the repo root:

```bash
chmod +x scripts/publish_github.sh
./scripts/publish_github.sh omop-public-health-showcase
```

That creates a **public** repository under your account and pushes `main`.

## Manual path

```bash
git add -A
git commit -m "Add OMOP public-health data mart showcase"
gh repo create omop-public-health-showcase --public --source=. --remote=origin --push
```

Or create an empty public repo on github.com, then:

```bash
git remote add origin git@github.com:<your-username>/omop-public-health-showcase.git
git push -u origin main
```

## Before you push

- Confirm `.env` is not committed (`.gitignore` already lists it).
- Keep `data/raw/*.csv` — they are synthetic and make the clone runnable.
- Do not add real EHR extracts.

## Pin the README URL in applications

Link the GitHub repo and, if you deploy the app, the live dashboard. For networking emails, two sentences plus the repo URL is enough; point people at `docs/interview_talking_points.md` only if they ask for depth.
