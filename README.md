## Project overview

This project aims to automate the validation of financial statements on a public register using Azure-based AI services. The primary objectives are to:

- **Automate Document Classification:** Differentiate genuine financial statements from unrelated or incorrect uploads.
- **Detect Critical Features:** Identify essential components—such as an auditor's signature—to ensure each document meets the required standards.
- **Enable Continuous Improvement:** Incorporate a human feedback loop that allows case officers to review and refine AI decisions, thus progressively enhancing model accuracy.
- **Ensure Scalability and Security:** Deploy a cost-effective, serverless solution using Azure Blob Storage, Functions, Machine Learning, and Cosmos DB, while following best security practices.
- **Provide Real-time Reporting:** Integrate with Power BI to generate dynamic dashboards that display processing metrics and model performance for ongoing oversight.

This solution will streamline the review process, reduce manual effort, and lay a strong foundation for further enhancements.

## Solution Design

The solution is centred around an **Azure Function**, which activates automatically when a new financial report is uploaded to the Register.

### Preliminary checks
Upon upload, the **Function** conducts a series of initial validation checks to quickly confirm document suitability:
- **PDF File Check:** Verifies that the uploaded file is indeed a PDF, as financial statements are typically submitted in this format.
- **Page Count Verification:** Counts the pages in the PDF. Financial statements generally range between 15 to 20 pages (?). Extremely short or excessively long documents are flagged as unlikely to be valid financial reports.
- **ABN Detection:** Scans the text within the PDF to detect the presence of an Australian Business Number (ABN), a key indicator that the document pertains to a legitimate entity.

Following these preliminary checks, the function uses advanced AI methods to examine the content in greater depth:

### Secondary checks

#### Document Chunking and Embeddings

The PDF is broken down into smaller, overlapping text segments called *"chunks"*. Each chunk typically consists of a few sentences or paragraphs to ensure detailed analysis without losing context.

These chunks are then processed through an **AI-based embeddings model**. An embedding converts text into a numeric representation, known as a "*vector*" in high-dimensional space. Vectors capture the semantic meaning of the text in a format that computers can efficiently analyse and compare.

#### Advanced Content Analysis using Large Language Model (LLM):

When checking for specific sections, such as a profit and loss statement, the solution formulates a textual query (e.g., *"Does this document contain a profit or loss statement?"*).

This query is converted into its own vector representation in the same high-dimensional space. The solution then compares the query vector to the vectors of all document chunks for the report in question.

By measuring similarity between the two vectors, the model identifies the most relevant chunks that indicate the presence or absence of the requested information.

The LLM provides a YES or NO answer based on this analysis. If the answer is YES, it also records the original page number(s) where the information was found, facilitating human verification.

Finally, all validation results are stored in a database. This structured data is then readily available for generating real-time insights and dynamic reports.

Example fields stored in Cosmos DB include:


```python
isPDF: # Indicates if the file is a valid PDF.
pageCount: # Number of pages in the PDF.
hasABN: # Whether an ABN was detected.
ABN: # The actual ABN found.
hasProfitLoss: # Indicates if a profit or loss statement is present.
profitLossPages: # Specific page numbers where the profit or loss statement is located.
blobUrl: # Direct URL to the original uploaded document.
```

## Costings

For detailed costings please see the [Costings page](/Documentation/Solution_Design/costing.md)

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

