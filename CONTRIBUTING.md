# Development Setup
Configure tools, environments and dependencies to build code locally.

## Prerequisites
- [Python 3.8+](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/)
- [virtualenv](https://virtualenv.pypa.io/en/latest/)

## Create a virtual environment
```bash
python -m venv .venv
```

## Activate the virtual environment
### POSIX
```bash
source .venv/bin/activate
```
### Windows
```
.venv\Scripts\activate
```

## Install dependencies
```bash
pip install -r requirements.txt
```

## Run migrations
```bash
python manage.py migrate
```

## Set [Gmail app password](https://support.google.com/accounts/answer/185833)
`.env`:
```properties
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD="abcd efgh ijkl mnop"
```

## Start the development server
```bash
python manage.py runserver
```
