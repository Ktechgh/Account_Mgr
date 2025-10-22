# Account_Manager
A software for closing daily account at filling station



# ⚙️ 1. Check Current Git Setup

Use these to inspect your current configuration and remote settings.

git config --global --list
git remote -v


# 🔍 What they do:

git config --global --list → Shows your saved Git identity (name, email, etc.)

git remote -v → Displays the current remote repository URL(s) linked to your local project (fetch & push).
# -----------------------------------------


# 👤 2. Set or Change Git Identity

These commands set who you are globally (applies to all repos).

git config --global user.email "kennarttechnologies@gmail.com"
git config --global user.name "Kennarttechl"



# 🧠 Explanation:
This sets your Git commit signature — each commit you make will show up under this name and email.
If you ever commit under a wrong email, you can fix it with the same commands.
# -----------------------------------------


# 🔐 3. Clear Saved GitHub Credentials

These commands remove stored login tokens or passwords from the Windows credential manager (or your OS’s keychain).

git credential-manager erase


Then Git will prompt for:

protocol=https
host=github.com


# 🧠 Why?

This clears the saved credentials (useful when switching between GitHub accounts or fixing authentication conflicts).

If it gives fatal: Missing 'protocol' input argument, use the interactive version as shown above.
# -----------------------------------------


# 🔗 4. Remove and Re-add Remote Repository

If your local repo is pointing to the wrong GitHub URL, remove and add the correct one.

git remote remove origin
git remote add origin https://github.com/Kennarttechl/Account_Manager.git


# 🧠 Explanation:

origin is the default name for your remote GitHub repository.

Removing and re-adding ensures your local project is correctly linked to the intended GitHub repo.
# -----------------------------------------


# 🔄 5. Update Existing Remote URL

If you just want to change the URL (instead of removing & adding):

git remote set-url origin https://github.com/Kennarttechl/Account_Manager.git


# 🧠 When to use:
If your remote already exists but points to the wrong repository (e.g., old account or repo name).
# -----------------------------------------


# 📦 6. Stage and Commit Changes

Add modified files to the staging area and create a commit.

git add .
git commit -m "Refactor all"


# 🧠 Explanation:

git add . → Adds all modified files for the next commit.

git commit -m "message" → Creates a new commit with a message describing the change.