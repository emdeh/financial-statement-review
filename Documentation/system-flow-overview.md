# System Flow Overview
Imagine a financial statement is being reviewed. Here’s how the components interact:

## 1. Document Ingestion:
- A financial statement (PDF) is uploaded to the **Storage Account**.
- **Event Grid** detects the new blob and sends an event to trigger the **Function App**.

## 2. Document Processing and Validation:
When the Azure Function is activated, it performs a series of sequential checks and extraction steps before any AI classification:

1. **PDF Validation**  
   The function reads the raw blob bytes and verifies the `%PDF-` header to ensure the file is a valid PDF. Non-PDF files are logged with `isPDF=false` in Cosmos DB and processing stops.

2. **Page Count Extraction**  
   Using PyPDF2, the function counts the number of pages in the PDF and records this as `pageCount` for reporting.

3. **Text Extraction**  
   - **Embedded Text**: for digitally generated PDFs, text is extracted directly via PyPDF2.
   - **OCR Fallback**: if embedded text is empty or on parse errors, Azure Cognitive Services' OCR is invoked to extract text from scanned pages.

4. **ABN Detection**  
   The extracted text is scanned with a regex for an Australian Business Number (ABN). If found, the normalized 11-digit ABN is stored under `abn` and a boolean `hasABN=true`.

5. **AI Classification & Feature Checks**  
   The cleaned text or its embedding is sent to an Azure ML Workspace endpoint which returns:
   - `isValidAFS`: whether the document is a valid Annual Financial Statement (AFS)
   - `afsConfidence`: confidence score of the classification
   Additional feature checks (e.g., signature detection) can be added in this step.

## 3. Result Storage and Feedback:
- The function constructs a single JSON document with all collected fields (`isPDF`, `pageCount`, `blobUrl`, `extractionMethod`, `abn`, `hasABN`, `isValidAFS`, `afsConfidence`, `timestamp`, etc.) and upserts it into **Cosmos DB** via a Pydantic-backed model.
- Any errors or alerts are logged to **Application Insights**.
- **Azure Key Vault** and **Managed Identity** secure access to secrets and database.

## 4. Review and Reporting:
- A dashboard (e.g., **Power BI**) queries Cosmos DB to provide daily reports on document counts, PDF validity rates, page counts, ABN presence, classification outcomes, and override statistics.
- Case officers can review and provide feedback that feeds back into the ML Workspace for continuous learning.

Below is the updated diagram of the flow:
```mermaid
flowchart TD
    A[User Uploads PDF] --> B[Storage Account]
    B --> C[Event Grid]
    C --> D[Function App]
    subgraph "Validation & Extraction"
      D --> D1[Validate PDF Header]
      D --> D2[Count Pages]
      D --> D3[Extract Text (Embedded/OCR)]
      D --> D4[Detect ABN]
      D --> D5[Classify & Feature Checks]
    end
    D --> H[Cosmos DB (Results Storage)]
    D --> E[Cognitive Services (OCR)]
    D --> F[Azure ML Workspace (Classifier)]
    D --> G[Azure Key Vault (Secrets)]
    subgraph Monitoring & Feedback
      I[Application Insights]
      J[Power BI Dashboard]
    end
    D --> I
    H --> J
```
