# 🐰 CodeRabbit.ai Integration Guide

This project is configured for **CodeRabbit**, an AI-powered code review assistant. It will automatically review your Pull Requests, providing feedback on code quality, security, and accessibility.

---

## 🚀 Setup Instructions

Since CodeRabbit is a GitHub App, you need to install it on your repository to activate it.

### 1. Push Code to GitHub
Ensure this project is pushed to a GitHub repository.
```bash
git add coderabbit.yaml
git commit -m "feat: integrate coderabbit.ai configuration"
git push origin main
```

### 2. Install CodeRabbit App
1. Go to [CodeRabbit.ai](https://coderabbit.ai/)
2. Click **"Sign up with GitHub"** or **"Install"**
3. Select the repository `healthassistant-final` (or whatever you named it)
4. Grant the necessary permissions

### 3. Verify Integration
1. Create a new branch: `git checkout -b test-coderabbit`
2. Make a small change (e.g., add a comment to `README.md`)
3. Push the branch and create a **Pull Request**
4. Within minutes, CodeRabbit will comment on your PR with a summary and review!

---

## ⚙️ Configuration Details

The configuration is stored in `coderabbit.yaml` in the root directory.

### Key Features Enabled:
- **Healthcare Focus**: Reviews check for accessibility and readability for elderly users.
- **Multilingual Checks**: Ensures new languages are added correctly without hardcoding.
- **Security Scanning**: Detects hardcoded API keys and PII logging.
- **Tone**: "Chill" profile (constructive and friendly feedback).

### Customizing the Reviewer
To change how CodeRabbit reviews your code, edit the `instructions` section in `coderabbit.yaml`.

Example:
```yaml
instructions: |
  Please be very strict about Python type hinting.
  Ensure all functions have docstrings.
```

---

## 📊 What CodeRabbit Will Do

1. **Summarize Changes**: It provides a high-level summary of what your PR does.
2. **Line-by-Line Review**: It comments on specific lines of code that can be improved.
3. **Chat**: You can reply to its comments, and it will respond (e.g., "Why is this wrong?", "Generate a fix").
4. **Walkthrough**: It generates a walkthrough of the changes for easier understanding.

---

**Happy Coding! 🐰**
