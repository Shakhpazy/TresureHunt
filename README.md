# TresureHunt
This is for TCSS 435 AI

## Set up the virtual environment

Run these commands from the project folder. If Python is not installed, install it first.

### Windows

Create the environment:

```powershell
py -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or activate it in Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### macOS

Create the environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Install dependencies

With the environment activated, install dependencies if the project has a `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

If there is no `requirements.txt`, skip this step. To exit the environment on either platform, run:

```bash
deactivate
```
