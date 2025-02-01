
# **Wikileaks and News Excerpt Similarity Analysis**

This Streamlit app analyzes the similarity between news excerpts and Wikileaks documents using two methods: Fuzzy Matching and Sentence-BERT. Users can select a news excerpt or link, and the app displays the most similar Wikileaks documents, along with relevant entities, relationships, and categories.

---

## **Features**
- Choose between **Fuzzy Matching** and **Sentence-BERT** methods for similarity analysis.
- Select a news article via its **link** or **excerpt text**.
- View top 5 most similar Wikileaks documents ranked by similarity scores.
- Filter results by **categories**.
- Display the most common entities across news excerpts in the sidebar.
- Insights into entities, relationships, and categories related to the selected news article.

---

## **Setup and Installation**

### **Prerequisites**
- Python 3.8 or later
- Streamlit
- Necessary Python libraries (see below)

### **Installation Steps**
1. Clone or download the repository:
   ```bash
   git clone https://github.com/your-username/wikileaks-news-similarity.git
   cd wikileaks-news-similarity
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Place the necessary data files in the `./data/` folder:
   - `cited_judgments_with_news_articles.xlsx` (Fuzzy Matching data)
   - `sentencebert_results.xlsx` (Sentence-BERT data)

4. Run the app:
   ```bash
   streamlit run app.py
   ```

---

## **Usage**

1. Start the app using the command:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501` or the URL shown in your terminal.

3. **Sidebar Configuration:**
   - Select the similarity method: **Fuzzy Matching** or **Sentence-BERT**.
   - Choose the selection method: **News Link** or **News Excerpt Text**.
   - Filter results by category (or view all categories).

4. **Main View:**
   - View the selected news article's details, including its entities, relationships, and categories.
   - Explore the top 5 most similar Wikileaks documents with similarity scores and category matches.

5. **Entity Analysis:**
   - View the top 15 most common entities from the dataset in the sidebar.

---

## **Dependencies**

The following Python libraries are required:
- `streamlit`
- `pandas`
- `openpyxl`
- `requests`
- `ast` (Standard library)

You can install these dependencies with:
```bash
pip install -r requirements.txt
```

**Sample `requirements.txt`:**
```plaintext
streamlit
pandas
openpyxl
requests
```

---

## **File Structure**
```plaintext
.
├── app.py                         # Main Streamlit app
├── data/
│   ├── cited_judgments_with_news_articles.xlsx  # Fuzzy Matching dataset
│   └── sentencebert_results.xlsx               # Sentence-BERT dataset
├── README.md                      # Documentation
└── requirements.txt               # Dependency list
```

---

## **References**
- **Sentence-BERT**: Reimers, Nils, and Iryna Gurevych. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." (2019). [Link](https://arxiv.org/abs/1908.10084)
- **Streamlit Documentation**: [Streamlit Docs](https://docs.streamlit.io/)

