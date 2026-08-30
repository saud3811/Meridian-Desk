#!/bin/bash
# One-command first deploy. Run from inside this folder:
#     ./deploy.sh YOUR-GITHUB-USERNAME [repo-name]
#
# It creates the local git repo, commits, pushes to GitHub, and tells you the
# two things you must click. It does not create the GitHub repo for you —
# make an empty one at https://github.com/new first (Public, no README).

set -euo pipefail
cd "$(dirname "$0")"

USER_NAME="${1:-}"
REPO="${2:-meridian-desk}"

if [ -z "$USER_NAME" ]; then
  echo "Usage: ./deploy.sh YOUR-GITHUB-USERNAME [repo-name]"
  echo
  echo "First create an empty PUBLIC repo at https://github.com/new"
  echo "with no README, no .gitignore and no licence."
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is not installed. On macOS run:  xcode-select --install"
  exit 1
fi

if [ -z "$(git config --global user.name || true)" ]; then
  echo "git does not know who you are yet. Set it once:"
  echo
  echo "  git config --global user.name  \"Your Name\""
  echo "  git config --global user.email \"you@example.com\""
  exit 1
fi

REMOTE="https://github.com/${USER_NAME}/${REPO}.git"
echo "Pushing to ${REMOTE}"
echo

[ -d .git ] || git init -b main
git add -A
git commit -m "Meridian News Desk" || echo "  (nothing new to commit)"

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE"
else
  git remote add origin "$REMOTE"
fi

echo
echo "If you are asked for a password, GitHub wants a Personal Access Token,"
echo "not your account password. Create one at:"
echo "  github.com -> Settings -> Developer settings -> Personal access tokens"
echo "  -> Tokens (classic), with the 'repo' and 'workflow' scopes ticked."
echo

git push -u origin main

cat <<EOF

────────────────────────────────────────────────────────────────
Pushed. Two things left, both in your repo on github.com:

  1. Settings -> Pages -> Source -> choose "GitHub Actions"
     (not "Deploy from a branch")

  2. Actions -> "Refresh and deploy" -> Run workflow
     First run takes about four minutes.

Your dashboard will then be live at:

     https://${USER_NAME}.github.io/${REPO}/

It rebuilds itself every two hours from then on.
────────────────────────────────────────────────────────────────
EOF
