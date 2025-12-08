# 🤖 Altissia Bot

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.40+-green.svg)](https://playwright.dev/python/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Automation bot for Altissia language exercises using Python and Playwright.

> ⚠️ **Educational purposes only** - Use responsibly and in accordance with Altissia's terms of service.

## ✨ Features

- 🔐 **Automatic login** with anti-bot detection bypass
- 📝 **Two-phase resolution**:
  - Phase 1: Collect all answers by going through the exercise
  - Phase 2: Return to start and auto-fill everything
- 🎯 **Supports multiple answer types**:
  - Single blank questions
  - Multiple blanks per question
- 🌐 **Headless mode** for background operation
- 💾 **Answer storage** for quick replay

---

## 📦 Quick Start

### Prerequisites

- Python 3.7+
- pip

### Installation

**Option 1: Automated script**

```bash
./scripts/install.sh
```

**Option 2: Manual installation**

```bash
# Install Python dependencies
pip install .

# Install development dependencies (optional)
pip install .[dev]

# Install Playwright browsers
playwright install chromium
```

### Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` with your Altissia credentials:

```env
ALTISSIA_USERNAME=your_email@example.com
ALTISSIA_PASSWORD=your_password
ALTISSIA_URL=https://www.altissia.com/
```

### Usage

**Interactive mode** (recommended for first use):

```bash
python run.py
# or
python -m altissia_bot
```

**Headless mode** (invisible browser):

```bash
python run.py --headless
# or
python -m altissia_bot --headless
```

**Automatic mode**:

```bash
python run.py --auto --exercise 1
# or
python -m altissia_bot --auto --exercise 1
```

---

## 🎯 How It Works

The bot uses a **two-phase approach** to solve exercises:

### Phase 1: Answer Collection 📝

1. Navigate through all questions
2. Click "Validate" without answering → reveals correct answer
3. Store the answer(s)
4. Click "Continue" to next question
5. Repeat until end

### Phase 2: Automatic Filling ⚡

1. You manually return to the start (click "Restart")
2. Bot fills all fields with stored answers
3. Validates each question
4. Completes the exercise automatically

### Example Output

```
✅ 10 questions collected!

📋 COLLECTED ANSWERS:
  Question 1 : House of Commons
  Question 2 : freedom / expression (2 blanks)
  Question 3 : Parliament
  ...

🔄 PHASE 2: Automatic filling
ℹ️  Return MANUALLY to the start of the exercise
```

---

## 🏗️ Project Structure

```
altissia-bot/
├── .github/
│   └── workflows/          # CI/CD workflows
│       ├── lint.yml        # Python linting
│       ├── commitlint.yml  # Commit message validation
│       └── release.yml     # Automated changelog
├── altissia_bot/          # Main package
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # Module entry point
│   ├── main.py            # Main script logic
│   ├── automations.py     # Core automation logic
│   └── utils.py           # Helper functions
├── docs/                  # Documentation
│   ├── CHANGELOG.md       # Version history
│   ├── CONTRIBUTING.md    # Contribution guidelines
│   └── CONTRIBUTORS.md    # Project contributors
├── scripts/               # Utility scripts
│   └── install.sh         # Automated installation
├── run.py                 # Convenience launcher
├── pyproject.toml         # Project config & dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── LICENSE               # Apache 2.0 License
└── README.md             # This file
```

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/altissia-bot.git
cd altissia-bot

# Install dependencies
pip install .

# Install development tools
pip install .[dev]

playwright install chromium
```

### Code Style

We use [Black](https://github.com/psf/black) for code formatting:

```bash
# Format code
black altissia_bot/ run.py

# Check formatting
black --check altissia_bot/ run.py
```

Linting with flake8:

```bash
flake8 altissia_bot/ run.py --max-line-length=100
```

Linting with mypy:

```bash
mypy altissia_bot/ run.py --ignore-missing-imports
```
### HTML Selectors Reference

If Altissia updates their HTML structure, update these selectors in `automations.py`:

```python
SELECTORS = {
    'input_field': 'input.c-iJOJc',
    'validate_button': 'button:has-text("Valider")',
    'correct_answer': 'span.c-gUxMKR-bkfbUO-isCorrect-true',
    'continue_button': 'button.c-jUtMbh, button.c-lfgsZH:has-text("Continuer")',
}
```

To find new selectors:
1. Open Altissia in a browser
2. Right-click on the element → Inspect
3. Note the `class`, `id`, or other attributes
4. Update the selector in the code

### Testing

**Manual testing:**

```bash
# Run in non-headless mode to see what's happening
python run.py
```

**Debug mode:**

Add to `main.py` for detailed logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:

- Code of conduct
- Development workflow
- Commit message conventions
- Pull request process

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for multiple choice questions
fix: resolve login issue with special characters
docs: update README with new features
refactor: simplify answer collection logic
```

---

## 📝 Changelog

See [CHANGELOG.md](docs/CHANGELOG.md) for a detailed history of changes.

---

## 🐛 Troubleshooting

### Login fails with "incorrect password"

**Cause**: Anti-bot detection  
**Solution**: The bot includes anti-detection measures. If it still fails:
- Verify credentials in `.env`
- Check if you use SSO/ENT (not supported)
- Try running in non-headless mode first

### No exercises found

**Cause**: Wrong page or HTML structure changed  
**Solution**:
- Navigate manually to the exercise page
- Press Enter when you see the questions
- Update selectors if Altissia changed their HTML

### "Timeout: element not found"

**Cause**: Slow connection or selectors outdated  
**Solution**:
- Increase timeouts in `automations.py`
- Check if Altissia updated their HTML structure
- Inspect the page to find new selectors

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 👥 Contributors

See [CONTRIBUTORS.md](docs/CONTRIBUTORS.md) for the list of contributors.

---

## ⚖️ Disclaimer

This bot is provided for **educational purposes only**. Users are responsible for:

- Complying with Altissia's terms of service
- Using the tool ethically and responsibly
- Any consequences of automated access

The authors assume no liability for misuse of this software.

---

## 🔗 Links

- [Playwright Documentation](https://playwright.dev/python/)
- [Python-dotenv](https://github.com/theskumar/python-dotenv)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Made with ❤️ for language learners**
