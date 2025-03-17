## Project overview

This project aims to automate the validation of financial statements on a public register using Azure-based AI services. The primary objectives are to:

- **Automate Document Classification:** Use OCR and an embedding-based machine learning classifier to differentiate genuine financial statements from unrelated or incorrect uploads.
- **Detect Critical Features:** Identify essential components—such as an auditor's signature—to ensure each document meets the required standards.
- **Enable Continuous Improvement:** Incorporate a human feedback loop that allows case officers to review and refine AI decisions, thus progressively enhancing model accuracy.
- **Ensure Scalability and Security:** Deploy a cost-effective, serverless solution using Azure Blob Storage, Functions, Machine Learning, and Cosmos DB, while following best security practices.
- **Provide Real-time Reporting:** Integrate with Power BI to generate dynamic dashboards that display processing metrics and model performance for ongoing oversight.

This solution will streamline the review process, reduce manual effort, and lay a strong foundation for further enhancements.


## Project structure

```bash
├── Documentation/
│   ├── decompile-arm-templates.md
│   ├── prereq.md
│   ├── resource-overview.md
│   ├── setting-up-the-venv.md
│   ├── solution-brief.md
│   ├── system-flow-overview.md
│   ├── local-testing-storage.md
│   └── architecture-diagram.png            # //TODO
│
├── AzureFunctions/
│   ├── host.json
│   ├── local.settings.json                 # For local dev, see example below
│   ├── requirements.txt                    # Function-specific dependencies
│   │
│   ├── ProcessPDF/
│   │   ├── main.py                         # Main processing logic
│   │   └── function.json                   # Function configuration
│   │
│   └── services/
│       ├── __init__.py
│       ├── logger.py
│       ├── tracer.py                     
│       ├── classification_service.py            
│       ├── db_service.py                   
│       └── ocr_service.py                  
│
├── Models/
│   ├── Classification/
│   │   ├── train.py                        # Training script for the document classifier
│   │   ├── model.py                        # Model definition and utilities
│   │   ├── predict.py                      # Inference logic (if separate)
│   │   └── requirements.txt                # Dependencies for model training/inference
│   └── CustomVision/                       # (Optional: for signature detection)
│       ├── train.py
│       ├── model.py
│       └── requirements.txt
│
├── infra/
│   ├── deploy.sh                           # Bash script to deploy Azure resources
│   ├── setup.sh                            # Bash script for initial setup/configuration
│   ├── retrain_pipeline.sh                 # Script to trigger model retraining
│   ├── bicep/                              # Bicep templates used in infra scripts.
│   └── scripts/                            # Contains infrastructure-related scripts                      
│
├── Notebooks/
│   ├── Exploratory_Data_Analysis.ipynb     # For initial data exploration
│   └── ModelTraining.ipynb                 # Jupyter notebook for training experiments
│
├── Tests/
│   ├── test_document_processing.py         # Unit tests for Azure Functions logic
│   └── test_model_classification.py        # Unit tests for classification model
│
├── .gitignore                              # Ignore file (Python, VS Code, Azure Functions, etc.)
├── README.md                               # High-level project overview and instructions
├── .code-workspace                         # See .venv setup instructions in Documentation/
└── requirements.txt                        # Global dependencies (if applicable)
```

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