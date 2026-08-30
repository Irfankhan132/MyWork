# Link Prediction in Knowledge Graphs: A Survey and Experimental Analysis of State-of-the-Art Methods

This repository contains the thesis, experimental results, figures, and supporting materials from my MSc research on **Link Prediction in Knowledge Graphs (KGs)**.

The main goal of this research was to study and experimentally compare different **Knowledge Graph Embedding (KGE)** approaches for predicting missing relationships between entities. The work also investigates how dataset structure influences model performance and discusses practical challenges related to the reproducibility of KGE experiments.

## 🎯 Research Objectives

The main objectives of this thesis were to:

- Study different approaches for **Knowledge Graph Embedding and Link Prediction**.
- Compare models representing different embedding architectures and mathematical approaches.
- Evaluate how dataset characteristics influence link prediction performance.
- Investigate model generalization using both standard and filtered benchmark datasets.
- Examine practical challenges associated with reproducing KGE experiments.
- Provide insights into model selection for different knowledge graph scenarios.

## 🧠 Models Studied

Six Knowledge Graph Embedding models were investigated:

| Model | Main Idea |
|---|---|
| **TransE** | Represents relations as translations between entity embeddings |
| **ComplEx-N3** | Uses complex-valued embeddings with N3 regularization |
| **TuckER** | Uses Tucker tensor decomposition to model entity-relation interactions |
| **SimplE** | Bilinear embedding approach based on canonical polyadic decomposition |
| **CrossE** | Learns relation-specific entity-relation interactions |
| **TorusE** | Performs translational embedding on a torus space |

These models were selected to cover different KGE design philosophies, including
**translational, tensor-factorization, complex-valued, interaction-based, and geometric approaches**.

## 📊 Datasets

The experimental analysis considered four widely used Knowledge Graph benchmark datasets:

- **FB15K**
- **FB15K-237**
- **WN18**
- **WN18RR**

FB15K-237 and WN18RR are particularly important because they reduce inverse-relation leakage found in FB15K and WN18, providing a more challenging evaluation of model generalization.

## 📏 Evaluation Metrics

The models were evaluated using standard ranking-based Link Prediction metrics:

- **Mean Reciprocal Rank (MRR)**
- **Hits@1**
- **Hits@3**
- **Hits@10**

MRR evaluates how highly the correct entity is ranked on average, while Hits@K measures how frequently the correct entity appears among the top K predictions.

## 🔬 Experimental Analysis

The study compares model behavior across datasets with different structural characteristics.

The analysis focuses on:

- Predictive performance
- Generalization across datasets
- Influence of inverse relations
- Architectural strengths and limitations
- Differences between filtered and less restrictive benchmark settings
- Reproducibility of KGE experiments
- Model-selection considerations

The experiments demonstrate that model performance depends strongly on both the **embedding architecture** and the **structure of the underlying knowledge graph**. Therefore, no single modeling approach should be assumed to be optimal for every link prediction scenario.

## 🔁 Reproducibility

An important part of this thesis concerns reproducibility in Knowledge Graph Embedding research.

The work highlights the importance of:

- Standardized end-to-end training and evaluation procedures
- Clearly documented hyperparameters
- Consistent dataset preprocessing
- Explicit filtered evaluation protocols
- Reproducible software environments
- Transparent reporting of experimental configurations

These practices can make comparisons between KGE approaches more reliable and easier to reproduce.

## 🛠️ Technologies and Tools

The experimental work involved technologies and tools including:

- Python
- PyTorch
- TensorFlow
- AmpliGraph
- NumPy
- Pandas
- Matplotlib
- Seaborn
- Conda / Python virtual environments

## 📈 Key Takeaway

A central finding of this research is that **the effectiveness of a Knowledge Graph Embedding model is closely related to the characteristics of the dataset and the relational patterns it needs to represent**.

More expressive models can capture complex relational structures, while simpler embedding approaches can remain useful because of their computational efficiency and interpretability.

The results therefore emphasize the importance of selecting a Link Prediction model according to the structure, complexity, and requirements of the target Knowledge Graph.

## 📂 Repository Contents

This repository primarily provides the **completed MSc thesis and associated experimental results/figures**.

> **Note:** The complete implementation source code used across the individual model experiments is not currently included in this repository. The repository is intended primarily as a record of the thesis, methodology, experimental analysis, and results.

## 🎓 Thesis Information

**Title:**  
*Link Prediction in Knowledge Graphs: A Survey and Experimental Analysis of State-of-the-Art Methods*

**Research Area:**  
Machine Learning · Knowledge Graphs · Link Prediction · Representation Learning · Graph Machine Learning

**Supervisor:**  
Stefano Marchesin

## 🔑 Keywords

`Knowledge Graphs` · `Link Prediction` · `Knowledge Graph Embeddings` · `Representation Learning` · `Graph Machine Learning` · `Reproducibility` · `Machine Learning`

## 📬 Contact

**Irfan Khan**

For questions, research discussions, or collaboration opportunities, feel free to contact me through my GitHub profile.

---

⭐ If you find this research useful or interesting, feel free to star the repository.
