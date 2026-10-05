# GitHub Profile Setup Guide

This guide outlines the few quick steps required to push your polished profile and activate your automated contribution snake.

---

## 📁 Summary of Files Configured

All files have already been edited and formatted for you in this workspace:
- **`README.md`**: Polished GitHub profile featuring your positioning in Data Science & Business Analytics, verified tech stack badges, proprietary and public project spotlights, light/dark-adaptive GitHub stats, and contribution snake integration.
- **`.github/workflows/snake.yml`**: GitHub Actions workflow that automatically computes your contribution graph and publishes dual light/dark SVG animations to the dedicated `output` branch.
- **`SETUP.md`**: This step-by-step setup guide.

---

## Step 1: Commit and Push Changes to GitHub

Run these commands in your terminal from inside this repository folder:

```bash
git status
git add README.md .github/workflows/snake.yml SETUP.md
git commit -m "Polish profile README and configure automated contribution snake"
git push origin main
```

---

## Step 2: Enable Workflow Write Permissions (Required)

By default, GitHub Actions workflows have read-only access. To allow the workflow to commit the generated snake SVGs to your `output` branch:

1. Open your repository on GitHub: [`https://github.com/Parv-spamz/Parv-spamz`](https://github.com/Parv-spamz/Parv-spamz).
2. Click **Settings** (top menu bar of the repo).
3. In the left sidebar, click **Actions** → **General**.
4. Scroll down to the **Workflow permissions** section.
5. Select **Read and write permissions**.
6. Click **Save**.

---

## Step 3: Run the Snake Workflow for the First Time

Once pushed and permissions are granted:

1. Go to the **Actions** tab in your repository.
2. In the left sidebar under *Workflows*, click **Generate contribution snake**.
3. Click the **Run workflow** dropdown on the right side.
4. Keep the branch set to `main` and click the green **Run workflow** button.
5. Wait ~30 to 45 seconds for the workflow run to turn green.

> [!TIP]
> The workflow will now automatically re-run every day at 00:15 UTC to keep your snake animation up to date. You can also trigger it manually whenever you want.

---

## Step 4: Include Private Contributions on Your GitHub Profile

Since a large part of your work is proprietary, make sure your GitHub contribution graph reflects all your private commits without exposing code:

1. Click your profile avatar in the top-right corner of GitHub → **Settings**.
2. Under **Public profile** (or **Contributions & Activity**):
3. Check the box for **"Include private contributions on my profile"**.
4. Click **Update preferences**.

**What this does:**
- Your daily contribution green squares and GitHub streak will reflect commits made across all your private and organizational repositories.
- Specific repository names, file contents, and commit descriptions remain 100% private and invisible to the public.

---

## Step 5: Pin Your Featured Repositories

On your public GitHub profile (`https://github.com/Parv-spamz`), click **Customize your pins** and select:
1. `Parv_Arora_Anshika_Trikha_Doctor_Appointment_Scheduling_System` (Primary public portfolio project)
2. `Parv-spamz` (Your profile configuration repository)

---

## ℹ️ Notes on GitHub Stats & Caching

- The GitHub Stats, Top Languages, and Streak cards query GitHub's public API and cache responses for approximately 2–4 hours.
- If you push new commits or change profile visibility settings, stats cards may take a few hours to refresh their cached SVGs.
