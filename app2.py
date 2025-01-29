import streamlit as st
import pandas as pd

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

selection_method = st.sidebar.radio("Select by", ["News Link", "News Excerpt Text"])

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

# Sidebar slider for similarity threshold
similarity_threshold = st.sidebar.slider("Minimum Similarity Score", 0.0, 1.0, 0.5)

# Filter the appropriate dataframe
filtered_df = fuzzy_df if view_option == "Fuzzy Matching" else bert_df
filtered_df = filtered_df[filtered_df["news_Link"] == news_link]
filtered_df_sorted = filtered_df.sort_values(by='content_similarity', ascending=False)

# Apply category and similarity threshold filtering
if category_option != "All":
    filtered_df_sorted = filtered_df_sorted[filtered_df_sorted['wikileaks_Category'] == category_option]
filtered_df_sorted = filtered_df_sorted[filtered_df_sorted['content_similarity'] >= similarity_threshold]

# Get the top 5 most relevant Wikileaks documents
filtered_df_sorted = filtered_df_sorted.head(5)

# Display results for the selected news article
if not filtered_df_sorted.empty:
    st.subheader("Selected News Article")
    st.write(filtered_df_sorted.iloc[0]["news_Text"])
    st.write(f"**Entities:** {filtered_df_sorted.iloc[0]['news_entities']}")
    st.write(f"**Relationships:** {filtered_df_sorted.iloc[0]['news_relationships']}")
    st.write(f"**Categories:** {filtered_df_sorted.iloc[0]['news_Category_x']} / {filtered_df_sorted.iloc[0]['news_Category_y']}")
    st.write(f"**Source:** {news_link}")
    
    st.subheader("Top 5 Most Similar Wikileaks Documents")
    def color_similarity(val):
        if val > 0.8:
            return "background-color: #85e085"  # Green
        elif val > 0.6:
            return "background-color: #ffff99"  # Yellow
        else:
            return "background-color: #ff9999"  # Red
    
    st.dataframe(filtered_df_sorted.style.applymap(color_similarity, subset=['content_similarity']))
    
else:
    st.warning("No matching results found for the selected news article.")
