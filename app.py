import streamlit as st
import pandas as pd
import requests
from urllib.parse import urlparse
import ast  # For converting string representations of lists to actual lists

# Load the preprocessed data files
fuzzy_file = "./data/cited_judgments_with_news_articles.xlsx"
bert_file = "./data/sentencebert_results.xlsx"

fuzzy_df = pd.read_excel(fuzzy_file)
bert_df = pd.read_excel(bert_file)

# Drop duplicate news excerpts
fuzzy_df_unique = fuzzy_df.drop_duplicates(subset="news_Link")
bert_df_unique = bert_df.drop_duplicates(subset="news_Link")

# Streamlit app
st.title("Wikileaks and News Excerpt Similarity Analysis")

# Sidebar for user input
st.sidebar.header("Input Options")
view_option = st.sidebar.selectbox("Choose Similarity Method", ["Fuzzy Matching", "Sentence-BERT"])

# Allow selection by news link or news text
selection_method = st.sidebar.radio("Select by", ["News Link", "News Excerpt Text"])

# Display options based on the selection method
if selection_method == "News Link":
    st.sidebar.subheader("Available News Links")
    available_links = (
        fuzzy_df_unique["news_Link"].unique()
        if view_option == "Fuzzy Matching"
        else bert_df_unique["news_Link"].unique()
    )
    selected_news = st.sidebar.selectbox("Select a News Link", available_links)
    filtered_df_unique = (
        fuzzy_df_unique if view_option == "Fuzzy Matching" else bert_df_unique
    )
    news_link = selected_news
else:
    st.sidebar.subheader("Available News Excerpts")
    available_texts = (
        fuzzy_df_unique["news_Text"].unique()
        if view_option == "Fuzzy Matching"
        else bert_df_unique["news_Text"].unique()
    )
    selected_text = st.sidebar.selectbox("Select a News Excerpt", available_texts)
    filtered_df_unique = (
        fuzzy_df_unique if view_option == "Fuzzy Matching" else bert_df_unique
    )
    news_link = filtered_df_unique[filtered_df_unique["news_Text"] == selected_text].iloc[0]["news_Link"]

# Sidebar for category selection
category_option = st.sidebar.selectbox("Select Category", ["All"] + list(filtered_df_unique['wikileaks_Category'].unique()))

# Filter the appropriate dataframe
if view_option == "Fuzzy Matching":
    filtered_df = fuzzy_df[fuzzy_df["news_Link"] == news_link]
else:
    filtered_df = bert_df[bert_df["news_Link"] == news_link]

# Sort by similarity score in descending order and filter by category if selected
filtered_df_sorted = filtered_df.sort_values(by='content_similarity', ascending=False)

# If category is selected, filter by the chosen category
if category_option != "All":
    filtered_df_sorted = filtered_df_sorted[filtered_df_sorted['wikileaks_Category'] == category_option]

# Get the top 5 most relevant Wikileaks documents
filtered_df_sorted = filtered_df_sorted.head(5)

# Display results for the selected news article
if not filtered_df_sorted.empty:
    st.subheader("Selected News Article")
    st.write(filtered_df_sorted.iloc[0]["news_Text"])
    st.write(f"**Entities:** {filtered_df_sorted.iloc[0]['news_entities']}")
    st.write(f"**Relationships:** {filtered_df_sorted.iloc[0]['news_relationships']}")
    st.write(f"**Categories:** {filtered_df_sorted.iloc[0]['news_Category_x']} / {filtered_df_sorted.iloc[0]['news_Category_y']}")

    # Display News Link
    st.write(f"**Source:** {news_link}")

    st.subheader("Top 5 Most Similar Wikileaks Documents")
    for _, row in filtered_df_sorted.iterrows():
        st.write(f"**Wikileaks Text:** {row['wikileaks_Text']}")
        st.write(f"**Similarity Score:** {row['content_similarity']:.2f}%")
        st.write(f"**Category Match:** {row['wikileaks_Category']}")
        st.markdown("---")
else:
    st.warning("No matching results found for the selected news article.")

# Footer analysis
st.sidebar.header("Analysis")
if view_option == "Fuzzy Matching":
    st.sidebar.subheader("Top 15 Most Common Entities")
    
    # Ensure the 'common_entities' column is correctly processed (converting string to list)
    fuzzy_df['common_entities'] = fuzzy_df['common_entities'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    # Explode the 'common_entities' column and count the occurrences
    filtered_fuzzy_df = fuzzy_df[fuzzy_df['common_entities'].notnull()]
    entity_counts = filtered_fuzzy_df['common_entities'].explode().value_counts().head(15).reset_index()
    entity_counts.columns = ["Entity", "Count"]
    
    # Display in table format
    st.sidebar.table(entity_counts)
else:
    st.sidebar.subheader("Top 15 Most Common Entities")
    
    # Exploding and counting for Sentence-BERT entities
    exploded_entities = bert_df['news_entities'].dropna().explode().value_counts().head(15)
    
    # Display the most common entities for Sentence-BERT
    st.sidebar.write(exploded_entities)
