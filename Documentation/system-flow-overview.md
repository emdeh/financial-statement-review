# System Flow Overview
Imagine a financial statement is being reviewed. Here’s how the components interact:

## 1. Document Ingestion:
- A financial statement (PDF) is uploaded to the **Storage Account**.
- **Event Grid** detects the new blob and sends an event to trigger the **Function App**.

## 2. Document Processing:
- The Azure Function is activated.
- It uses **Cognitive Services** to perform OCR and extract text (and possibly table data) from the PDF.
- The extracted text is then sent to the **Azure Machine Learning Workspace** endpoint, where the document classifier (using embeddings and supervised learning) determines if it’s a valid AFS.
- In parallel, the function may perform additional checks, such as looking for an auditor’s signature either by searching for textual cues or by calling another model (which could also be hosted in AML).


## 3. Result Storage and Feedback:
- The outcome—classification result, confidence level, and signature detection status—is stored in **Cosmos DB**.
- Any errors or alerts can be logged and monitored through **Application Insights** (if integrated).
- **Azure Key Vault** is used during processing to securely retrieve secrets or API keys.
- **Managed Identity** ensures the function securely accesses Cosmos DB, Key Vault, and Cognitive Services.

## 4. Review and Reporting:
- A dashboard (e.g. via **Power BI**) can later query **Cosmos DB** to provide daily reports and visual insights on processed documents.
- Officers can review the results, and their feedback can be fed back into the **Azure ML Workspace** for continuous learning.

Below is a simple diagram of the flow:
```mermaid
flowchart TD
    A[User Uploads PDF] --> B[Storage Account]
    B --> C[Event Grid]
    C --> D[Function App]
    D --> E[Cognitive Services (OCR)]
    D --> F[Azure ML Workspace (Classifier)]
    D --> G[Azure Key Vault (Secrets)]
    D --> H[Cosmos DB (Results Storage)]
    subgraph Monitoring & Feedback
      I[Application Insights]
      J[Power BI Dashboard]
    end
    D --> I
    H --> J
```