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
   - `Your Name` in the banner URL (use `%20` for spaces)
   - The typing lines (each line is separated by `;`, use `+` for spaces)
   - The `class Developer` code block under About Me
   - The Tech Stack icons: edit the `i=` list, using names from
     https://github.com/tandpfun/skill-icons#icons-list
   - `your-email@example.com`, `your-linkedin` and `your-instagram` under Connect
4. Commit. Your profile page at `github.com/spiderleagendary11-beep` now shows it.

## 3. Turn on the snake and stats cards
1. In the same repo, click **Add file → Create new file**.
2. Name it `.github/workflows/snake.yml` and paste in [`snake.yml`](.github/workflows/snake.yml).
3. Do the same for `.github/workflows/stats.yml` with [`stats.yml`](.github/workflows/stats.yml),
   and for `scripts/activity_graph.py` with [`activity_graph.py`](scripts/activity_graph.py).
   These draw the GitHub Stats, Most Used Languages and Contribution Activity cards into a
   `profile/` folder, because the public servers for those cards often break.
4. Commit, then go to **Actions** and click **Run workflow** on both
   "Generate snake animation" and "Update stats cards".
5. After about a minute, the snake and both stats cards show on your profile.
   After that, they update themselves every day.

If the workflow fails with a permissions error, go to **Settings → Actions → General →
Workflow permissions**, choose **Read and write permissions**, and save.

## 4. Pin your best repos
On your profile, click **Customize your pins** and pick up to 6 repos
(that's the "Popular repositories" grid under the README).

## Changing the look
- **Accent color:** electric cyan `00D9FF` is used everywhere (case doesn't matter).
  Find-and-replace it in `README.md` to re-theme the whole profile. Some ready-made swaps:

  | Look | Replace `00D9FF` with |
  |---|---|
  | Spider red (matches your username) | `FF1E3C` |
  | Hacker green | `39FF14` |
  | Gold | `FFB800` |

  The banner and footer also use dark navy `0a3d62`. Swap it for a dark shade of your new
  color (for example `5c0011` with red) so the gradient matches.
  Also change the colors in `snake.yml` (`color_snake`) and `stats.yml` (the `00d9ff` values), and `ACCENT` in `activity_graph.py`.
- **Typing text:** build your own at https://readme-typing-svg.demolab.com
- **Banner styles:** change `type=venom` to `waving`, `rect`, `slice` or `soft`.
  Previews: https://github.com/kyechan99/capsule-render

## If a card shows a broken image
The snake, stats and activity cards live in your own repo, so they don't break this way.
The other cards (streak, quote, banner) come from free public servers
that sometimes hit rate limits or go down.
(The broken "Contribution Activity" image in the screenshot you copied is exactly this.)
Usually it fixes itself within a few hours. If one stays broken, delete that section,
or deploy your own copy on Vercel (each project's GitHub page explains how).
