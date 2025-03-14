## Setting Up Python Virtual Environments and a VS Code Multi-root Workspace

This guide covers how to create separate Python virtual environments for your main project and your Azure Functions component, and how to configure a multi-root workspace in VS Code so that the correct interpreter is automatically used based on the folder you’re working in.

---

### 1. Create the Primary Virtual Environment

In your project root, run:
```bash
python -m venv venv
```
This creates a folder named `venv` with a fresh Python environment.

#### Activate the Primary Virtual Environment

- **On Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **On macOS and Linux (including WSL):**
  ```bash
  source venv/bin/activate
  ```

Your command prompt should now show `(venv)` indicating that the environment is active.

#### Deactivate the Primary Virtual Environment

When you're done, run:
```bash
deactivate
```
This will return you to the global Python environment.

---

### 2. Create the Azure Functions Virtual Environment

Navigate to the `AzureFunctions/` directory (which is a subfolder of your project) and run:
```bash
python -m venv venv-AzureFunction
```
This creates a second virtual environment specifically for your Azure Functions.

**Tip:** Consider activating this environment in a separate terminal:

- **On Windows:**
  ```bash
  AzureFunctions\venv-AzureFunction\Scripts\activate
  ```
- **On macOS and Linux (including WSL):**
  ```bash
  source AzureFunctions/venv-AzureFunction/bin/activate
  ```

---

### 3. Setting Up a Multi-root Workspace in VS Code

A multi-root workspace lets you configure folder-specific settings, such as which Python interpreter to use, for different parts of your project.

#### Create and Configure the Workspace

1. **Add Folders to the Workspace:**
   - Open VS Code.
   - Go to **File > Add Folder to Workspace...**.
   - Add your project root (e.g., `.`) and the `AzureFunctions/` folder as separate entries.

2. **Save the Workspace:**
   - Go to **File > Save Workspace As...** and save your workspace (for example, `my-project.code-workspace`).

#### Example `.code-workspace` File

```json
{
  "folders": [
    {
      "name": "ProjectRoot",
      "path": "."
    },
    {
      "name": "AzureFunctions",
      "path": "AzureFunctions"
    }
  ],
  "settings": {}
}
```

#### Configure Folder-specific Settings

- **For the Project Root:**
  In the project root folder, create a `.vscode/settings.json` file with:
  ```json
  {
    "python.defaultInterpreterPath": "venv/bin/python"
  }
  ```
  
- **For the AzureFunctions Folder:**
  In the `AzureFunctions/` folder, create (or update) `.vscode/settings.json` with:
  ```json
  {
    "azureFunctions.deploySubpath": ".",
    "azureFunctions.scmDoBuildDuringDeployment": true,
    "azureFunctions.pythonVenv": "venv-AzureFunction",
    "azureFunctions.projectLanguage": "Python",
    "azureFunctions.projectRuntime": "~4",
    "debug.internalConsoleOptions": "neverOpen",
    "azureFunctions.projectLanguageModel": 2,
    "python.defaultInterpreterPath": "venv-AzureFunction/bin/python"
  }
  ```
  Make sure that `"azureFunctions.pythonVenv"` matches the actual name of your Azure Functions virtual environment folder.

#### Opening the Workspace in VS Code

From your project folder in the terminal, open the workspace by running:
```bash
code my-project.code-workspace
```
This will open VS Code using the multi-root workspace configuration, ensuring that each folder’s settings (including the Python interpreter) are applied correctly.

---

### 4. Managing Terminals with Multiple Environments

While VS Code’s Python extension automatically switches the interpreter for the editor based on the folder, the integrated terminal does not. It is recommended to open separate terminals for each environment:

- **Terminal for the Project Root:**
  ```bash
  cd /path/to/my-project
  source venv/bin/activate
  ```
- **Terminal for Azure Functions:**
  ```bash
  cd /path/to/my-project/AzureFunctions
  source venv-AzureFunction/bin/activate
  ```

This way, you can run commands in each terminal using the correct virtual environment.

---

This setup allows you to maintain isolated environments for different parts of your project while leveraging a multi-root workspace in VS Code for a seamless development experience.
