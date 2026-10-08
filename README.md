# Django---Login-Authentication

Django authentication exercise with account-related views, forms, templates, and database models.

## Repository guide

### Contents

- [authentication_system](authentication_system)
- [requirements.txt](requirements.txt)

### Getting started

```bash
git clone https://github.com/Raimal-Raja/Django---Login-Authentication.git
cd Django---Login-Authentication
```

Create and activate a virtual environment, then install the project dependencies:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r "requirements.txt"
```

Run each Django project from the folder containing its manage.py file:

```bash
cd "authentication_system"
python manage.py check
python manage.py migrate
python manage.py runserver
```

### Configuration and limitations

### Validation

Reviewed on 2026-10-08. Python syntax checks passed for 16 source files. Syntax validation does not establish runtime correctness or dependency compatibility.

### Contributions

Describe the issue, reproduction steps, environment, and expected behavior when proposing a change. Keep generated environments, credentials, and unnecessary build artifacts out of new commits.

### License

No top-level license file was found during this review.
