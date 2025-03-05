## Setting Up a Python Virtual Environment

### 1. Create the Virtual Environment
Run the following command in your project root:
```bash
python -m venv venv
```

This creates a folder named venv with a fresh Python environment.

### 2. Activate the Virtual Environment
On Windows:
```bash
venv\Scripts\activate
```

On macOS and Linux (including WSL):
```bash
source venv/bin/activate
```

Once activated, your command prompt should show (venv) indicating the environment is active.

### 3. Deactivate the Virtual Environment
When you're done, simply run:
```bash 
deactivate
```
This will return you to the global Python environment.
