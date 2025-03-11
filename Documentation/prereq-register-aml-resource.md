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