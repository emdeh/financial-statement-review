#### [Back Home](/README.md)

# Sizing Estimator

To evaluate the potential operating costs for the solution, please use the [Sizing Estimator](https://azure.com/e/8dabebdeac3443399f1eedc97383f4da). Below are clearly explained assumptions and parameters you can input into the estimator to tailor cost projections to your specific scenario.

---

## Assumptions and Parameters

### Azure AI Computer Vision

- **Transactions per month:** 1,000  
  Represents the total monthly volume of documents processed by Azure's Computer Vision service.

- **Training hours per month:** 10 hours  
  Time dedicated monthly for training or improving custom vision models.

---

### Azure Cosmos DB

- **Request Units (RU/s):** 500  
  Measures the throughput capacity of Cosmos DB. A Request Unit (RU) quantifies the resources required to perform database operations (reads, writes, queries).

- **Average Utilisation:** 80%  
  Represents the expected average utilisation of provisioned RU/s.

- **Hours per month:** 730  
  Total hours Cosmos DB service will be active monthly.

- **Backup Copies:** 2  
  Number of copies of data maintained for redundancy.

**Factors influencing RU consumption:**
- **Data Size:** A 1 KB data record typically consumes around 5 RU/s. Larger items proportionally consume more RUs.
- **Indexing:** Default indexing increases RU usage. Custom indexing reduces consumption.
- **Consistency Level:** Higher consistency (e.g., Strong) may consume more resources compared to lower levels (e.g., Eventual).
- **Partition Key Design:** Effective design evenly distributes data and optimises RU usage.

To refine estimates, use the [Azure Cosmos DB Capacity Calculator](https://cosmos.azure.com/capacitycalculator/).

---

### Azure Functions

- **Memory Size (GB):** Specify the amount of memory allocated per function execution.
- **Execution Time (Seconds):** Average time each function runs per execution.
- **Executions per month:** Expected monthly frequency of function triggers.

---

### Azure AI Search (with Vector Index)

- **Number of Documents Indexed:** Total documents stored in AI Search.
- **Average Size per Document:** Average document size to determine storage and indexing costs.
- **Queries per month:** Estimated monthly search requests to retrieve information from the indexed documents.

---

### Azure OpenAI Service

- **Embeddings Model:**  
  - **Number of Embeddings Requests per month:** How frequently document chunks are converted into embeddings.
  - **Average Tokens per Embedding:** The average length of text processed for embeddings.

- **Chat Completion Model:**  
  - **Chat Completion Requests per month:** Monthly queries made to the model for information extraction or validation.
  - **Average Tokens per Request:** Length of text per request, including both query and response from the model.

---

These clearly defined assumptions will help you accurately project costs based on your expected usage and easily adjust your scenarios as required.

---
#### [Back Home](/README.md)