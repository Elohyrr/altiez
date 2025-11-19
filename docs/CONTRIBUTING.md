# Contributing to Altissia Bot

First off, thank you for considering contributing to Altissia Bot! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Workflow](#development-workflow)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)

---

## Code of Conduct

This project adheres to a simple code of conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

---

## How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check existing issues to avoid duplicates.

When creating a bug report, include:

- **Clear title** describing the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, etc.)
- **Screenshots** if applicable
- **Error messages** or logs

Example:
```
Title: Login fails with special characters in password

Description:
When my password contains `@` or `#`, the bot fails to login.

Steps to reproduce:
1. Set password with special characters in .env
2. Run `python main.py`
3. Login fails with "incorrect password"

Expected: Login succeeds
Actual: Login fails

Environment:
- OS: Ubuntu 22.04
- Python: 3.10.0
- Playwright: 1.40.0
```

### Suggesting Enhancements ✨

Enhancement suggestions are welcome! Please include:

- **Clear use case** - why is this needed?
- **Expected behavior** - what should happen?
- **Possible implementation** - if you have ideas

### Code Contributions 💻

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feat/amazing-feature`)
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with conventional commits**
6. **Push to your fork**
7. **Open a Pull Request**

---

## Development Workflow

### 1. Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/altissia-bot.git
cd altissia-bot

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Install development tools
pip install black flake8 mypy
```

### 2. Create a branch

```bash
# Feature branch
git checkout -b feat/your-feature-name

# Bug fix branch
git checkout -b fix/bug-description

# Documentation
git checkout -b docs/what-you-document
```

### 3. Make changes

Write clean, well-documented code:

```python
def my_function(param: str) -> bool:
    """
    Brief description of what this does.
    
    Args:
        param: Description of parameter
    
    Returns:
        Description of return value
    """
    # Implementation
    pass
```

### 4. Test your changes

```bash
# Run manually to verify
python run.py

# Check code style
black altissia_bot/ run.py
flake8 altissia_bot/ run.py --max-line-length=100
```

### 5. Commit

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add support for multiple choice questions"
git commit -m "fix: resolve login timeout issue"
git commit -m "docs: update README with new examples"
```

### 6. Push and create PR

```bash
git push origin feat/your-feature-name
```

Then open a Pull Request on GitHub.

---

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear and automated changelog generation.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding tests
- **chore**: Maintenance tasks

### Examples

**Feature:**
```
feat(automations): add support for multiple choice questions

- Implement new selector for choice buttons
- Add logic to detect and click correct answer
- Update tests

Closes #42
```

**Bug fix:**
```
fix(login): handle special characters in password

Special characters like @ and # were not properly encoded,
causing login failures.

Fixes #38
```

**Documentation:**
```
docs(readme): add troubleshooting section

Add common issues and solutions for:
- Login failures
- Selector timeouts
- Browser detection
```

### Breaking Changes

If your change breaks backward compatibility:

```
feat(api)!: change answer collection return type

BREAKING CHANGE: collect_answer() now returns a list instead of string
to support multiple blanks per question.

Migration guide:
- Old: answer = collect_answer(page, 1)
- New: answers = collect_answer(page, 1)
```

---

## Pull Request Process

### Before submitting

- [ ] Code follows the style guide
- [ ] Commit messages follow conventional commits
- [ ] You've tested your changes manually
- [ ] Documentation is updated if needed
- [ ] No unnecessary files are included

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How you tested your changes

## Checklist
- [ ] Code follows style guide
- [ ] Commit messages are conventional
- [ ] Documentation updated
- [ ] Tested manually
```

### Review Process

1. Automated checks run (lint, commitlint)
2. Maintainer reviews code
3. Feedback is addressed
4. PR is merged
5. Changelog is automatically updated

---

## Style Guide

### Python Code Style

We use **Black** for formatting with these settings:

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py37']
```

**Format code:**
```bash
black altissia_bot/ run.py
```

### Linting Rules

We use **flake8** with:

```ini
# .flake8
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv
ignore = E203, W503
```

**Lint code:**
```bash
flake8 altissia_bot/ run.py
```

### Code Principles

1. **Keep it simple** - prefer clarity over cleverness
2. **Document generously** - docstrings for all functions
3. **Error handling** - try/except with meaningful messages
4. **Type hints** - use them where it adds clarity
5. **Constants** - uppercase names (e.g., `SELECTORS`)

### Example

**Good:**
```python
def collect_answer(page: Page, question_number: int) -> list:
    """
    Collect answer from a question without filling it.
    
    Args:
        page: Playwright page object
        question_number: Question index starting from 1
    
    Returns:
        List of correct answers, or None if collection failed
    """
    try:
        # Click validate to reveal answer
        page.click(SELECTORS['validate_button'])
        
        # Get all correct answer elements
        answers = page.locator(SELECTORS['correct_answer']).all()
        
        return [elem.inner_text() for elem in answers]
    except Exception as e:
        print_error(f"Failed to collect answer: {e}")
        return None
```

**Bad:**
```python
def ca(p, n):  # Unclear names
    # No docstring
    try:
        p.click('button')  # Magic string
        a = []
        for e in p.locator('span').all():
            a.append(e.inner_text())
        return a
    except:  # Bare except
        return None
```

---

## Questions?

Feel free to:
- Open an issue for discussion
- Ask in your PR
- Reach out to maintainers

Thank you for contributing! 🚀

---

**📍 Location**: This file is located at `docs/CONTRIBUTING.md`
