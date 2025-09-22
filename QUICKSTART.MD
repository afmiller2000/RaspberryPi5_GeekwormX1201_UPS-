# 🚀 Raspberry Pi & GitHub Quick Start Reference

This document is your personal, beginner-friendly guide for using GitHub with your Raspberry Pi projects!

---

## 1. Creating a GitHub Repository

1. Go to [Create a new GitHub repository](https://github.com/new)
2. Fill out:
   - Name: `RaspberryPi5_GeekwormX1201_UPS-`
   - Description: `Comprehensive UPS monitoring and management for Geekworm X1201 on Raspberry Pi 5`
   - Select Public (for sharing) or Private
   - [x] Add a README
   - [x] Add .gitignore → Python
   - [x] Choose a license (MIT recommended)
3. Click **Create repository**

---

## 2. Cloning Your Repo to Your Pi or Laptop

```bash
git clone https://github.com/afmiller2000/RaspberryPi5_GeekwormX1201_UPS-.git
cd RaspberryPi5_GeekwormX1201_UPS-
```

---

## 3. Making and Pushing Changes

1. Edit files locally (code, docs, scripts)
2. Stage changes:
   ```bash
   git add .
   ```
3. Commit:
   ```bash
   git commit -m "Describe your change"
   ```
4. Push:
   ```bash
   git push
   ```

---

## 4. Best Practices

- Commit often, push regularly (your work is backed up)
- Use descriptive commit messages
- Don’t commit secrets or passwords
- Keep your README updated

---

## 5. Working from Multiple Devices

- Use `git pull` to sync before starting
- Can use [GitHub Desktop](https://desktop.github.com/) on Mac/Windows for a GUI
- SSH is optional—HTTPS is fine for beginners

---

## 6. Useful Links

- [GitHub Hello World Guide](https://docs.github.com/en/get-started/quickstart/hello-world)
- [GitHub Using Git](https://docs.github.com/en/get-started/using-git)
- [GitHub Markdown](https://guides.github.com/features/mastering-markdown/)
- [Create a new file on GitHub](https://github.com/afmiller2000/RaspberryPi5_GeekwormX1201_UPS-/new/main)
- [Upload files via the web](https://github.com/afmiller2000/RaspberryPi5_GeekwormX1201_UPS-/upload/main)
- [Edit README directly](https://github.com/afmiller2000/RaspberryPi5_GeekwormX1201_UPS-/edit/main/README.md)

---

## 7. How to Create a Document in Your Repo (Web method)

1. Go to your repo
2. Click **Add file** > **Create new file**
3. Name it (e.g., `notes.md` or `QUICKSTART.md`)
4. Paste your notes/info
5. Scroll down, write a commit message, and click **Commit new file**

---

## 8. How to Add a File from Terminal

```bash
nano notes.md   # Or use any text editor
# Paste your info and save
git add notes.md
git commit -m "Add notes doc"
git push
```

---

## 9. When in Doubt

- Open an issue in your repo with your question
- Ask Copilot, ChatGPT, or the community for help

---

## 10. You Got This!

Don't be afraid to experiment—your repo is your sandbox. Every mistake is progress!
