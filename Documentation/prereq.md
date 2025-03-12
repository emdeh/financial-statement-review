# Register Azure Machine Learning resource provider.

In order to deploy resources like AML workspaces and online endpoints, you need to ensure that the Azure Machine Learning resource provider is registered.

1. Register the Resource Provider:
tegister the Azure Machine Learning resource provider using the Azure CLI. Run the following command to register the resource provider:
```bash
az provider register --namespace Microsoft.MachineLearningServices
```
This will register the Microsoft.MachineLearningServices resource provider, which is required for creating and managing Azure Machine Learning resources, including AML workspaces and online endpoints.

2. Verify Registration:
After running the above command, you can verify that the resource provider has been registered by using the following command:

```bash
az provider show --namespace Microsoft.MachineLearningServices | grep registrationState
```

Ensure that the `"registrationState": "Registered"` is displayed in the output. This confirms that the resource provider is now registered.

3. Install CLI Machine Learnign extension
You may need to install the CLI Machine Learning extension for AML-related provisioning to function properly.

If you're using Debian or Ubuntu, the fastest way to install the necessary CLI version and the Machine Learning extension is:

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash 
az extension add -n ml -y
```

For other environments check https://learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli?view=azureml-api-2&tabs=public

# Azure Function extension

Install the Azure Functions Extension:

Open VS Code.
Install the Azure Functions extension if you haven’t already.
Create a New Project:

Open the Command Palette (Ctrl+Shift+P on Windows/Linux or Cmd+Shift+P on macOS) and run:
sql
Copy
Azure Functions: Create New Project...
Choose a folder for your project.
Select your preferred language (e.g. JavaScript, Python, or C#).
When prompted for a template, choose Blob Trigger.
Enter a function name (e.g. ProcessPDFBlob).
Set the Blob path to point to your Storage Account container (for example, pdf-uploads/{name}).
Provide the name of the storage connection setting (commonly AzureWebJobsStorage).
Configure Local Settings:

In the local.settings.json file, ensure you have the connection string for your Storage Account under the key AzureWebJobsStorage.
