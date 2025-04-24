# Sizing estimator

Please review the [Sizing Estimator](https://azure.com/e/8dabebdeac3443399f1eedc97383f4da) to help find the potential operating costs.

## Assumptions
The following outlines the assumptions you should be aware of in the Sizing Estimator. Adjust them in Microsoft's calculator as required.

### Azure AI Computer Vision
- **Transactions:** 1000  
    This refers to the number of API calls made to the Azure AI Computer Vision service.

- **Training:** 10 hours  
    This refers to the time spent training custom models using the Azure AI Computer Vision service.

---

### Azure Cosmos DB
- **Request Units (RU/s):** 500
- **Average utilisation:** 80%
- **Hours:** 730
- **Backup copies:** 2

    To estimate the Request Units (RU/s) for simple table rows being written, consider the following:

    - **Base RU Consumption:** Writing a single 1 KB item typically consumes 5 RU/s.
    - **Item Size:** If the item size exceeds 1 KB, RU consumption increases proportionally. For example, a 2 KB item would consume approximately 10 RU/s.
    - **Indexing:** By default, Azure Cosmos DB indexes all properties. If you disable or customise indexing, RU consumption may decrease.
    - **Consistency Level:** Stronger consistency levels (e.g., Strong or Bounded Staleness) may increase RU consumption compared to Session or Eventual consistency.
    - **Partition Key Design:** Efficient partition key design ensures even distribution of data and avoids hot partitions, optimizing RU usage.

    Use the [Azure Cosmos DB Capacity Calculator](https://cosmos.azure.com/capacitycalculator/) to refine your estimate based on your specific workload.
---

### Azure Function
- **Memory Size:**
- **Execution time:**
- **Executions per month:**

---

### Azure AI Search

...

---

### Azure OpenAI Service

- **Embeddings Model:**
- **Chat Completion Model:**

...

---
