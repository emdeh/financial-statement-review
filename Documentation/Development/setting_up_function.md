## `local.settings.json` Example
Here is an example of what you need in your local settings

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "DEBUG_MODE": "<False or True>",
    "APPINSIGHTS_INSTRUMENTATIONKEY": "11111111-1111-1111-1111-111111111111",
    "COMPUTER_VISION_ENDPOINT": "<your endpoint>",
    "COMPUTER_VISION_KEY": "<your key>"
  }
}

```

Note that `APPINSIGHTS_INSTRUMENTATIONKEY` needs to emulate an actual key GUID.