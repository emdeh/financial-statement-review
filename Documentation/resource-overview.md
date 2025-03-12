# Brief Documentation for Each Resource

## Resource Group:
A logical container to group and manage all related Azure resources. It helps with unified access control and billing.

## Storage Account:
Holds the uploaded PDFs. This is where financial statements and other documents are stored, and it triggers further processing via Event Grid.

## Function App:
Hosts the serverless functions. It orchestrates the workflow by reacting to events (e.g. new blob upload) and executing processing steps like OCR extraction and classification.

## Azure Function (Placeholder):
The actual function that will process documents. It will extract text, call Cognitive Services, interact with the ML workspace, and write results to Cosmos DB.

## Event Grid (Placeholder):
A fully managed event routing service that notifies the Function App when a new document is uploaded to the Storage Account.

## Cosmos DB:
A NoSQL database for storing document metadata and processing results (e.g. classification outcome, confidence scores, signature flags).

## Cognitive Services:
Provides OCR capabilities (via the Read API or Document Intelligence) to extract text from both scanned and digitally generated PDFs.

## Azure Key Vault:
Securely stores API keys, connection strings, and other sensitive information. Services (like the Function App) can retrieve these securely at runtime.

## Managed Identity:
Allows the Function App and other services to authenticate to Azure resources (like Cosmos DB or Key Vault) without embedding credentials in code.

## Azure Machine Learning Workspace:
A central hub for developing, training, and deploying the document classification model. This workspace manages experiments, model versions, and production endpoints.

## (Consider) Application Insights:
For real-time monitoring, logging, and diagnostics of the Function App. This helps track performance and troubleshoot issues.