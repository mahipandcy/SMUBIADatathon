# **Wikileaks and News Excerpt Similarity Analysis**

[![Demo Video](https://img.shields.io/badge/Watch-Demo-red)](https://youtu.be/mWDrDqYwcYo)

This Streamlit app enables users to analyze the similarity between news excerpts and Wikileaks documents using two methodologies: **Fuzzy Matching** and **Sentence-BERT**. Users can explore the relationships between journalistic articles and leaked government documents, gaining insights into entity connections, potential biases, and content alignment.

---

## **Features**
- **Choose between Fuzzy Matching and Sentence-BERT** for document similarity analysis.
- **Select a news article** via its **link** or **excerpt text** for comparison.
- **View the top 3 most similar Wikileaks documents**, ranked by similarity scores.
- **Filter results by categories** for more focused analysis.
- **Analyze named entities and relationships** extracted from the text.
- **Visualize data** with word clouds, heatmaps, network graphs, and Sankey diagrams.

---

## **Setup and Installation**

### **Prerequisites**
- Python 3.8 or later
- Streamlit
- Necessary Python libraries (see below)

### **Installation Steps**
1. **Clone or download the repository:**
   ```bash
   git clone https://github.com/mahipandcy/SMUBIADatathon.git
   cd SMUBIADatathon
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure the necessary data files are placed in the ./data/ directory:**
   - cited_judgments_with_news_articles.xlsx (Fuzzy Matching data)
   - sentencebert_results.xlsx (Sentence-BERT data)
   - processed_news_excerpts_parsed_with_category.xlsx (Parsed news excerpts with categories)
   - processed_wikileaks_parsed_with_category.xlsx (Wikileaks documents with categories)

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## **Usage**

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

2. **Navigate to the Streamlit UI:**
   - Open a browser and go to http://localhost:8501 (or the URL displayed in the terminal).

3. **Sidebar Configuration:**
   - Select the similarity method: **Fuzzy Matching** or **Sentence-BERT**.
   - Choose the selection method: **News Link** or **News Excerpt Text**.
   - Filter results by **category** or view all categories.

4. **Main Interface:**
   - View the selected news article, including its entities, relationships, and categories.
   - Explore the **top 3 most similar Wikileaks documents**, ranked by similarity scores.
   - Analyze **common entities and relationships** between news excerpts and Wikileaks documents.
   - Visualize entity networks, similarity distributions, and content trends.

---

## **Visualization Techniques**

- **Word Clouds**: Displays the most frequently occurring terms in news excerpts and Wikileaks documents.
  - ![Figure 6.4 - Word Cloud of News Entities](./images/figure6_4.png)
  - ![Figure 6.5 - Word Cloud of Wikileaks Entities](./images/figure6_5.png)

- **Entity Co-occurrence Heatmaps**: Highlights the relationships between frequently mentioned entities.
  - ![Figure 6.6 - Heatmap of Content Similarity Across Categories](./images/figure6_6.png)
  - ![Figure 3.5 - Row Similarity Heatmap - News Excerpt](./images/figure3_5.png)
  - ![Figure 4.5 - Row Similarity Heatmap - WikiLeaks](./images/figure4_5.png)

- **Network Graphs**: Uses Pyvis to visualize entity relationships.
  - ![Figure 2 - Filtered Network Graph of Top Connections](./images/figure2.png)

- **Sankey Diagrams**: Illustrates the flow from subjects to relationships to objects.
  - ![Figure 6.3 - Content Similarity by News Categories](./images/figure6_3.png)

- **Similarity Score Distribution Charts**: Shows how similarity scores are distributed across datasets.
  - ![Figure 5.1 - Distribution of Sentence Similarity Scores - SentenceBERT](./images/figure5_1.png)
  - ![Figure 5.2 - Distribution of Fuzzy Similarity Scores - Fuzzy Method](./images/figure5_2.png)

- **Entity Distribution and Trends**:
  - ![Figure 3.1 - Top 10 Entities - News Excerpt](./images/figure3_1.png)
  - ![Figure 3.2 - Top 10 Relationships - News Excerpt](./images/figure3_2.png)
  - ![Figure 4.1 - Top 10 Entities - WikiLeaks](./images/figure4_1.png)
  - ![Figure 4.2 - Top 10 Relationships - WikiLeaks](./images/figure4_2.png)

- **Content Length and Sentiment Analysis**:
  - ![Figure 3.3 - Sentiment Distribution - News Excerpt](./images/figure3_3.png)
  - ![Figure 3.4 - Content Length Distribution - News Excerpt](./images/figure3_4.png)
  - ![Figure 4.3 - Sentiment Distribution - WikiLeaks](./images/figure4_3.png)
  - ![Figure 4.4 - Content Length Distribution - WikiLeaks](./images/figure4_4.png)

- **Time-Series Analysis**:
  - ![Figure 7 - Yearly Counts from Datasets](./images/figure7.png)

---

## **User Interface**

1. **News Display, Entity, and Relationship Extraction**  
   This interface displays the selected news article, extracted entities, and relationships.  
   ![News Display](./images/UI1.png)

2. **Top Three Similar Wikileaks Matches**  
   View the top three most similar Wikileaks documents ranked by similarity scores and categories.  
   ![Top Three Wikileaks Matches](./images/UI2.png)

3. **Entity Graph and Word Cloud**  
   Visualizes the entity-relationship graph and key terms from the selected news article.  
   ![Entity Graph and Word Cloud](./images/UI3.png)

4. **Threat Distribution Heatmap**  
   Displays the global distribution of threats on a world map.  
   ![Threat Heatmap](./images/heatmap.png)

---

## **Solution Impact & Insights**
- **Validate credibility**: Compare news articles against Wikileaks documents to verify authenticity.
- **Detect potential biases**: Identify discrepancies in media narratives.
- **Highlight emerging topics**: Track recurring themes across news articles and leaked documents.
- **Facilitate investigative journalism**: Enable journalists, researchers, and policymakers to explore news-document relationships.

---

## **References**
- **Sentence-BERT**: Reimers, Nils, and Iryna Gurevych. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." (2019). [Link](https://arxiv.org/abs/1908.10084)
- **FuzzyWuzzy**: [PyPI](https://pypi.org/project/fuzzywuzzy/)
- **Streamlit Documentation**: [Streamlit Docs](https://docs.streamlit.io/)