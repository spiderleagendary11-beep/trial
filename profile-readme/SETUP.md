# Setting up your GitHub profile README

## 1. Create the special repo
1. On GitHub, click **+ → New repository**.
2. Set **Repository name** to your username exactly: `spiderleagendary11-beep`.
   GitHub shows a message saying it's a ✨special✨ repository.
3. Make it **Public**, tick **Add a README file**, and click **Create repository**.

## 2. Add the README
1. Open `README.md` in the new repo and click the ✏️ pencil to edit it.
2. Paste in the contents of [`README.md`](README.md) from this folder.
3. Edit the parts that are about you:
   - `Your Name` in the banner URL (use `%20` for spaces) and in the typing line (use `+` for spaces)
   - The About Me text and bullets
   - The Tech Stack badges: delete the ones you don't use, or add more from https://simpleicons.org
   - `your-email@example.com` and `your-linkedin` under Contact Me
4. Commit. Your profile page at `github.com/spiderleagendary11-beep` now shows it.

## 3. Turn on the snake
1. In the same repo, click **Add file → Create new file**.
2. Name it `.github/workflows/snake.yml` and paste in [`snake.yml`](.github/workflows/snake.yml).
3. Commit, then go to **Actions → Generate snake animation → Run workflow**.
4. After about a minute, an `output` branch appears and the snake shows on your profile.
   After that, it updates itself every day.

If the workflow fails with a permissions error, go to **Settings → Actions → General →
Workflow permissions**, choose **Read and write permissions**, and save.

## 4. Pin your best repos
On your profile, click **Customize your pins** and pick up to 6 repos
(that's the "Popular repositories" grid under the README).

## Changing the look
- **Colors:** `a855f7` (purple) is used throughout. Find-and-replace it with any hex color.
- **Card themes:** change `theme=tokyonight` to `radical`, `dracula`, `synthwave`, `github_dark`, etc.
  Full list: https://github.com/anuraghazra/github-readme-stats/blob/master/themes/README.md
- **Typing text:** build your own at https://readme-typing-svg.demolab.com
- **Banner styles:** try `type=rect`, `type=slice`, `type=venom` at https://github.com/kyechan99/capsule-render

## If a card shows a broken image
These cards come from free public servers that sometimes hit rate limits or go down.
(The broken "Contribution Activity" image in the screenshot you copied is exactly this.)
Usually it fixes itself within a few hours. If one stays broken, delete that section,
or deploy your own copy on Vercel (each project's GitHub page explains how).
