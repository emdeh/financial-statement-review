# Local Azure Functions Test Environment Setup

This document explains how to set up a local test environment for the Azure Functions using Azurite (the local Azure Storage emulator) and Azure Storage Explorer. Follow these steps to download, install, and validate your environment.

---

## Prerequisites

- **Node.js and npm:** Required to install Azurite.
- **Azure Functions Core Tools:** Installed globally.

---

## 1. Install and Configure Azure Functions Core Tools

### Method (for Ubuntu/WSL)
1. **Install prerequisites:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y wget apt-transport-https
   ```

2. **Download and install Microsoft package signing key:**
   ```bash
   wget -q https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
   sudo dpkg -i packages-microsoft-prod.deb
   sudo apt-get update
   ```

3. **Install Azure Functions Core Tools:**
   ```bash
   sudo apt-get install azure-functions-core-tools-4
   ```
4. **Verify Installation:**
   ```bash
   func --version
   ```

---

## 2. Install and Run Azurite

Azurite emulates Azure Storage locally, which is essential for testing blob triggers.

### a. Install Azurite Globally via npm
```bash
npm install -g azurite
```

### b. Create a Dedicated Workspace Folder (Recommended)
Decide on a location (e.g., at your project root). For example:
```bash
mkdir ~/azurite_workspace
```

### c. Start Azurite
Run Azurite in its own terminal (it does not need to be in your virtual environment):
```bash
azurite --location ~/azurite_workspace
```
Azurite will now listen on the default ports for Blob, Queue, and Table services.

---

## 3. Install Azure Storage Explorer

Azure Storage Explorer is a free tool that lets you view and interact with your Azure storage accounts, including your local Azurite instance.

1. **Download:**  
   Visit the [Azure Storage Explorer download page](https://azure.microsoft.com/en-us/features/storage-explorer/) and download the installer for your operating system.

2. **Install:**  
   Run the installer and follow the on-screen instructions.

3. **Connect to Local Storage:**
   - Open Azure Storage Explorer.
   - Click on the plug icon or "Add an Account".
   - Choose to connect to a local storage account. You can use the connection string `UseDevelopmentStorage=true` or select the local Azurite option if detected automatically.

---

## 4. Create Your Azure Functions Project with function subfolder

Assuming you have created the Azure Functions project in a folder (e.g., `AzureFunctions/`), the basic structure should look like this:

```
├── AzureFunctions/
│   ├── host.json
│   ├── local.settings.json
│   ├── requirements.txt         
│   ├── ProcessPDF/              # IMPORTANT: Subfolder for each function
│   │   ├── function.json        # Function configuration                     
│   │   └── main.py              # Azure Function entry point
│   │
│   └── services/

```

---

## 5. Configure Blob Trigger and Local Settings

### a. Configure the Blob Trigger Binding

In `function.json`, set the trigger to listen to the correct container (e.g., "pdf-uploads"):
```json
{
  "bindings": [
    {
      "name": "myblob",
      "type": "blobTrigger",
      "direction": "in",
      "path": "pdf-uploads/{name}",
      "connection": "AzureWebJobsStorage"
    }
  ],
  "scriptFile": "main.py"
}
```
*Note:* If using `__init__.py` instead of `main.py`, update the `"scriptFile"` accordingly.

### b. Setup Local Settings

In `local.settings.json`, ensure you have the correct connection string for local development:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

### c. Example Function Code in `main.py`

```python
import logging
import azure.functions as func

def main(myblob: func.InputStream):
    logging.info("Blob trigger function processed blob")
    logging.info("Name: %s", myblob.name)
```

> For blob triggers define the function with a single parameter for the blob (of type `func.InputStream`) and then access its name via the blob object itself (i.e. `myblob.name`). Trying to do something like the following signature seems to fail:
 ```python
 def main(myblob: func.InputStream, name: str):
   ```
---

## 6. Validate the Local Setup

### a. Start the Function Host

1. Activate your Python virtual environment (e.g., `venv-AzureFunction`):
   ```bash
   source venv-AzureFunction/bin/activate
   ```
2. Navigate to your `AzureFunctions/` folder and run:
   ```bash
   func start --verbose
   ```
   - Look for log messages indicating that your function has been registered (e.g., "Registered function: main").
   - If you see "No job functions found", double-check your `function.json` and file placement.

### b. Trigger the Function via Blob Upload

> Don't forget to start `azurite` as described in Step 2.

1. **Using Azure Storage Explorer:**
   - Connect to your local Azurite instance.
   - Navigate to the storage account (using the connection string `UseDevelopmentStorage=true`).
   - Create (or locate) the container named **pdf-uploads**.
   - Upload a sample PDF file into the container.
2. **Observe the Logs:**
   - The Azure Functions host (running in your terminal) should log the blob’s name and size, confirming that the trigger was executed.

### c. Troubleshooting

- If no functions are found, ensure:
  - The entry point file (e.g., `main.py` or `__init__.py`) is in the same folder as `function.json`.
  - The `"scriptFile"` setting in `function.json` correctly points to your function code.
  - The function signature is correct (e.g., `def main(myblob: bytes, name: str):`).

- Use the verbose mode (`func start --verbose`) for detailed output.

---

## 7. Final Verification

- **Function Registration:**  
  You should see logs similar to:
  ```
  Registered function: main
  Found 1 function(s) in ...
  Host started (listening on http://127.0.0.1:7071)
  ```

- **Blob Trigger Execution:**  
  After uploading a PDF to the **pdf-uploads** container, logs should indicate that the blob was processed, displaying the blob name and size.

---

## Conclusion

Following these steps sets up your local development environment with:
- Azure Functions Core Tools
- Azurite for local storage emulation
- Azure Storage Explorer for managing local storage

This configuration allows you to develop, test, and validate your Azure Functions locally before deploying to Azure. Adjust your function code and settings as needed for further integration (OCR, ML endpoints, Cosmos DB, etc.).