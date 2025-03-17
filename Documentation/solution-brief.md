# Proposed Azure AI Solution for Financial Statements

## Overview
This project aims to automate the validation of financial statements on a public register using Azure-based AI services. The primary objectives are to:

- **Automate Document Classification:** Use OCR and an embedding-based machine learning classifier to differentiate genuine financial statements from unrelated or incorrect uploads.
- **Detect Critical Features:** Identify essential components—such as an auditor's signature—to ensure each document meets the required standards.
- **Enable Continuous Improvement:** Incorporate a human feedback loop that allows case officers to review and refine AI decisions, thus progressively enhancing model accuracy.
- **Ensure Scalability and Security:** Deploy a cost-effective, serverless solution using Azure Blob Storage, Functions, Machine Learning, and Cosmos DB, while following best security practices.
- **Provide Real-time Reporting:** Integrate with Power BI to generate dynamic dashboards that display processing metrics and model performance for ongoing oversight.

This solution will streamline the review process, reduce manual effort, and lay a strong foundation for further enhancements.

## Document Classification (FS vs. Other Files)
The first step is an AI-driven document classifier to flag whether an uploaded PDF is a Financial Statement (FS) or an incorrect file. The design will use Optical Character Recognition (OCR) to extract text from each PDF and then apply a machine learning model to classify the document type. Azure's Cognitive Services **Read OCR** (or Document Intelligence's Layout model) can extract text from PDFs, including scanned ones.

Key features for classification will include: the volume of financial terminology, presence of tables, and overall text length – FS documents are typically multi-page reports with tables and financial terms, whereas incorrect uploads (receipts, images, etc.) have less structured content.

**Approach:**  
The proposed design will use an embedding-based text classifier. The solution converts extracted text into a numerical vector (embedding) that captures the semantic context of the document. A pre-trained language model (e.g. Azure OpenAI embeddings or a fine-tuned BERT) can generate these document embeddings. The classifier (a lightweight neural network or logistic regression) then determines if the vector is similar to those of genuine AFS or not. This approach is robust to format variations because it considers the content's meaning, not just specific keywords.

To enhance accuracy, the design will incorporate simple checks (unsupervised filters). For example, if a document's embedding is very dissimilar to all known AFS embeddings (an outlier in vector space), we flag it as "not AFS" for manual review. This combination of supervised learning (trained on labelled examples) and unsupervised outlier detection provides an initial safety net against unknown document types.

## Feature Identification (Auditor's Signature Detection)
Beyond basic classification, the system will inspect each AFS for critical components. The initial feature to check is the presence of an auditor's signature since a signed auditor's report is a key validity indicator.

The solution will implement a detector that searches the document for signature cues. This can be done in two ways:

- **Textual cues:** Using OCR results, look for keywords and phrases commonly accompanying auditor signatures (e.g. "Independent Auditor's Report", "Auditor's Signature", auditor name, and date). If such phrases are found without an accompanying signature mark, it might indicate a missing signature.
- **Visual cues:** Many signatures are handwritten scribbles or images. The design can leverage Azure AI Document Intelligence's custom model capabilities to detect the presence of a signature image in the PDF. Azure's Document Intelligence service allows training a custom model with a "signature" field type that can recognise if a signature (handwritten mark) is present on a page.

Initially, the solution will be trained on sample financial statements with the signature area labelled so the model learns to return a "signed" indicator instead of an "unsigned" indicator.

In the first iteration, the solution will simply flag whether an auditor's signature is found. Over time, this feature set can expand – for example, checking for the presence of required financial statements (balance sheet, income statement, notes, etc.) or verifying that the report includes comparative figures.

The architecture is designed to be extensible, so new feature detectors (for other missing components) can be added into the pipeline as needed.

## Model Training and Continuous Learning

### Initial Training Data
The initial solution will rely on a training dataset of two classes: valid AFS and incorrect uploads. To compensate for limited real data, synthetic data generation will be used. Fake financial reports can be generated (e.g. using templates or mixing sections from real reports) to cover a variety of AFS formats. Likewise, a compilation of examples of common incorrect uploads (scanned receipts, images, unrelated PDFs) will be used to train the model on what not to accept.

This curated dataset of "good vs bad" examples will be used to train the classifier.

### Embedding-Based Model
The classifier model will treat each document as unstructured text and learn to differentiate based on content patterns. By using text embeddings, the solution captures semantic and contextual features of the entire document, rather than manual features. For example, the solution can use a pre-trained transformer to encode the document; such models inherently understand language structure and financial terminology, improving accuracy in identifying AFS content.

These embeddings can even be combined with simple metadata (like page count or presence of tables) for the model's input. Initially, a supervised learning algorithm (like logistic regression or a small neural network) will be trained on these embeddings to predict "AFS" or "Not AFS".

### Unsupervised Filtering
In addition to the primary classifier, the solution will investigate unsupervised learning to serve as an early filter. One idea is to use clustering or one-class classification: create an embedding of each document and use a one-class SVM or autoencoder trained only on genuine AFS to detect anomalies. Documents that are too far from the learned "AFS" manifold (e.g., a photo of a receipt with very different content) would be flagged as suspicious without needing an explicit second class. This unsupervised step can help catch outliers that the supervised model might be unsure about, and route them for review or secondary checks.

### Reinforcement Learning with User Feedback
The system will improve over time via continuous learning. The design will implement a feedback loop where case officers (human reviewers) review the AI's decisions and correct them if needed. Each time an officer confirms a correct classification or overrides a wrong one, that feedback is recorded. Over time, these human-labelled outcomes form an expanded training set to further train or fine-tune the model. The model can periodically retrain on all accumulated data (initial synthetic + new real examples with feedback labels). This approach is akin to reinforcement learning in the broad sense – the model learns from the "rewards/penalties" of its predictions being right or wrong. In practice, this may be implemented as scheduled retraining jobs (e.g. using Azure Machine Learning pipelines) that incorporate the latest feedback. This ensures the classifier keeps improving and adapting to any new types of errors or document formats encountered.

## Azure Architecture and Processing Pipeline

The entire solution will be deployed on Azure. The following architecture is proposed:

### Storage and Ingestion
- **Azure Blob Storage:** All uploaded documents will be stored in Azure Blob Storage (this mimics Production). When a new file is uploaded to the designated container, it will trigger an Azure Function via Event Grid. The Blob filename or metadata will carry the entity ID or submission ID to track it.

### Serverless Processing Pipeline
- **Azure Functions:** An Azure Function will serve as the orchestrator for processing each document. Azure Functions are cost-effective (pay-as-you-go) and can scale out to handle bursts of uploads in parallel. The function is triggered by the new blob event, then performs the following steps:
  1. **Text Extraction:**  
     The function calls Azure AI Document Intelligence (Form Recogniser) or the Computer Vision OCR API to extract text from the PDF.  
     If the PDF is a scanned image, the OCR will produce the text content; if it's digitally generated, text extraction is straightforward. The function can use the Layout model of Document Intelligence to get text lines and even table structures if needed.
  2. **Document Classification:**  
     The extracted text is passed to the ML classification model. We will deploy the custom classifier either as an Azure Machine Learning online endpoint or package it in the Azure Function (if small enough). For example, an Azure ML endpoint could host a PyTorch or scikit-learn model behind a REST API. Alternatively, the solution could containerise the model and use an Azure Container Instance. The function sends the text (or its embedding) to this model to get a classification result (AFS or not, along with a confidence score).
  3. **Feature Checks:**  
     If the document is classified as an AFS, additional feature identification is run. For the auditor's signature, the function can either analyse the OCR text for signature keywords or call a secondary AI model. The solution may train a small Custom Vision model or use Document Intelligence custom model to detect a signature image in the PDF.  
     This step returns a boolean flag (signature present: yes/no) and could be extended with other checks (like verifying if certain sections exist).
  4. **Result Storage:**  
     The results of the analysis are then stored for later retrieval and reporting. Azure Cosmos DB can be used to store a record for each document – including classification result, confidence score, and flags for each feature check. Cosmos DB is a good choice for scalable, schema-flexible storage of JSON results, and it integrates easily with Azure Functions. Each record would link to the blob URL and have fields like `IsAFS` (bool), `Confidence` (float), `SignaturePresent` (bool), etc.
  5. **Notification/Queue (Optional):**  
     To decouple processing or handle further steps asynchronously, the function can put a message on an Azure Service Bus or Storage Queue indicating the document has been classified. This could signal downstream systems or simply log the event for audit trails. In a simple design, this may not be necessary, and the function can directly update the database and return.

### Machine Learning Model Training
- **Azure Machine Learning:**  
  For training and updating the classification model, the solution will leverage Azure Machine Learning services. We can maintain the training scripts and data in Azure ML, using compute clusters to retrain when new data is available. The initial synthetic dataset can be stored in an Azure ML datastore (or Azure Blob). Training runs can be triggered manually or on a schedule (e.g., monthly retraining using accumulated feedback). Once a new model is trained and evaluated, it can be deployed to production. Azure ML allows versioning models and deploying as managed endpoints, making it easy to swap in an improved model without changing the function code (the function just calls the endpoint).

### Scalability
- Blob Storage and Functions will handle increases in load – and the design can process documents in parallel as each new file triggers its own function instance. Azure Functions consumption plan will scale out automatically, or a premium plan can be implemented for more consistent performance. The use of serverless components means the solution will only incur costs per execution, making it cost-effective during periods of low activity. Storing extracted text and results in Cosmos DB ensures low-latency retrieval and the ability to handle high throughput of insertions.

### Cost Considerations
- Expensive services are avoided where possible. The OCR via Azure AI (Read API) is relatively low-cost per page compared to fully managed form analysis. Heavy use of Form Recogniser's custom form extraction is excluded (unless needed later for deeper analysis), focusing on classification which is simpler. The custom ML model runs either in a lightweight container or Azure Function – both are cost-efficient. The solution design also processes PDFs in a way that, for example, if a document is clearly not an AFS after a quick check (like extremely short text), further analysis can be short-circuited to save processing time.

## User Feedback and Reinforcement Loop
To ensure the AI system remains accurate and accountable, a human feedback mechanism will be put in place. Each document's assessment can be reviewed by a case officer (especially those that are flagged as not AFS or missing features). To enable monitoring, the design will include a simple internal web dashboard (hosted on Azure App Service or as a Power BI report with write-back capability) for case officers to review AI results:

- The officer can see the document (rendered PDF or key extracted info), along with the AI's classification (AFS or not) and reasons/flags (e.g., "No auditor signature detected").
- There will be options to confirm the AI decision if it's correct, or override it if incorrect. For example, if the AI marked a filing as "Not AFS" but the officer sees it actually is an AFS, they can override and mark it as valid.
- Each confirmation/override is recorded in the results database. Specifically, a field like `OfficerOverride` and the corrected label is stored. This feedback data is extremely valuable. The pipeline will use it in model retraining – essentially applying reinforcement learning principles. Over time, the model learns from its mistakes as identified by humans.

We may implement an automated process where, for example, weekly the system gathers all new feedback and retrains or fine-tunes the classifier (perhaps giving more weight to recently misclassified examples). Azure ML's training pipeline can be scheduled to incorporate this feedback loop. Additionally, Azure AI Document Intelligence's custom classifier supports incremental learning by adding new samples to classes, so that could be leveraged to update a custom classification model if chosen.

The feedback loop not only improves the AI's accuracy, but also provides transparency. Case officers remain in control of final decisions, which is important for confidence and trust. It will also ensure that any time the AI's recommendation is overridden, that case is flagged in reports (to enable tracking of the AI's error rate and types of errors over time).

## Reporting and Power BI Integration
The solution will generate daily reports on the AFS submissions and AI assessments. Key metrics include:

- Number of documents processed per day.
- How many were classified as AFS vs not AFS.
- Confidence levels of classifications (e.g., count of low-confidence cases).
- Number of documents flagged for missing features (e.g., how many lacked an auditor signature).
- Override statistics: how often officers overruled the AI, and in which direction (false positives vs false negatives).

All this data is stored in the results database (Cosmos DB). An Azure Logic App or a scheduled Function will be used to aggregate daily stats (for example, grouping results by date and calculating counts and averages) and store these in a summary table. However, since Power BI can perform aggregations itself, separate summary storage may not be necessary – Power BI can directly query the results data source. For Power BI integration, there are two approaches:

- **Direct Query/Dataset:**  
  Connect Power BI to the results database (Cosmos DB can be accessed via the Azure Cosmos DB connector or Synapse Link, or Azure SQL can be used which Power BI easily queries). This allows the Power BI report to always fetch the latest data. Refreshes can be scheduled multiple times per day or even use DirectQuery mode for real-time updates.

- **Real-time Push:**  
  For instantaneous updates, events can be pushed to Power BI via streaming datasets. For example, the Azure Function can call the Power BI REST API to add a new row each time a document is processed (containing document ID, classification result, etc.). Power BI dashboards can then be set to use a streaming dataset that updates in real-time as the data is pushed. Although Microsoft provides integration from Azure Stream Analytics to Power BI for real-time charts, in this case an Azure Function pushing to a Power BI push dataset is simpler.

Using Power BI creates interactive dashboards for management. These can include charts (e.g., a daily trend of the number of valid AFS vs rejected files) and filters to view specifics (like viewing all documents flagged with missing signatures). This not only aids in oversight of the AI process but also in identifying any patterns (for instance, an uptick in incorrect uploads might indicate a need for better user guidance on the submission portal).

## Security and Compliance Considerations
Although the financial statements are public documents, the solution will adhere to strong security and coding best practices. The system will be designed with the Azure Well-Architected Framework pillars in mind, especially security.

- **Secure Access to Data:**  
  The Blob Storage container will be configured to allow access only via the application or authorised roles – even if the data isn't private, unauthorised modifications are prevented. Azure AD (Entra ID) will be used for authenticating access to storage and other resources, avoiding shared keys exposure.  
  For instance, the Azure Function will use a Managed Identity to read the PDFs from Blob and write to the database, so no secrets are embedded in code. All keys (for cognitive services, database, etc.) will be stored in Azure Key Vault, and the Function retrieves them securely at runtime.

- **Secure Coding Practices:**  
  The code for the Azure Function and any web app will be developed following secure coding standards. This includes input validation (even though PDFs are the input, the file type and size are checked to prevent exploits), error handling that does not expose sensitive information, and logging of actions for audit. Azure's built-in services like Azure Monitor and Application Insights will be utilised for logging and alerting. For example, if an unusually formatted file causes the OCR or model to crash, it will be logged and DevOps can be alerted to investigate – this could also indicate a potentially malicious file, so monitoring is key.

- **Compliance:**  
  Since this is for a public register, all data is non-confidential, but compliance with relevant regulations (e.g. keeping data within required regions, meeting accessibility standards for government services, etc.) will be ensured. An audit log of all classification decisions and user overrides will be maintained to have a traceable record of how each document was handled, which is important for transparency.

- **Data Privacy:**  
  If any personal data appears in financial statements (names of officials, etc.), the pipeline's handling of data is minimal and secure (data stays within our controlled storage and databases). The content is not exposed to any external services beyond Azure's environment, and no classified or personal data is used to train external models without proper governance.

## Conclusion
This Azure-based solution will automate the intake and validation of financial statements with AI. By leveraging Azure Functions, Cognitive Services, and Machine Learning, it can classify documents and check for critical features like auditor signatures in a scalable, cost-effective manner. The system is designed to learn continuously – starting with a mix of synthetic and real data and improving via officer feedback (a form of reinforcement learning). The recommended architecture uses managed Azure services to streamline development: Blob Storage and Event Grid for ingestion, Azure AI for text extraction, custom ML models for classification, and Cosmos DB for storing results. All components are tied together with an emphasis on security so that the solution is robust and trustworthy.

Finally, integrating the results into Power BI provides real-time visibility into the process, enabling oversight and helping stakeholders trust the AI. This approach will significantly improve the validity of financial statements on a public register, and provide a foundation that can be expanded with more advanced document checks over time.
