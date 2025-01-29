import streamlit as st
import pandas as pd

# Load the preprocessed data files
fuzzy_file = "cited_judgments_with_news_articles.xlsx"
bert_file = "sentencebert_results.xlsx"

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

# Filter the appropriate dataframe
if view_option == "Fuzzy Matching":
    filtered_df = fuzzy_df[fuzzy_df["news_Link"] == news_link]
else:
    filtered_df = bert_df[bert_df["news_Link"] == news_link]

# Display results for the selected news article
if not filtered_df.empty:
    st.subheader("Selected News Article")
    st.write(filtered_df.iloc[0]["news_Text"])
    st.write(f"**Entities:** {filtered_df.iloc[0]['news_entities']}")
    st.write(f"**Relationships:** {filtered_df.iloc[0]['news_relationships']}")
    st.write(f"**Categories:** {filtered_df.iloc[0]['news_Category_x']} / {filtered_df.iloc[0]['news_Category_y']}")

    st.subheader("Most Similar Wikileaks Documents")
    for _, row in filtered_df.iterrows():
        st.write(f"**Wikileaks Text:** {row['wikileaks_Text']}")
        st.write(f"**Similarity Score:** {row['content_similarity']:.2f}%")

        if view_option == "Fuzzy Matching":
            st.write(f"**Common Entities:** {row['common_entities']}")
            st.write(f"**Common Relationships:** {row['common_relationships']}")
        st.write(f"**Category Match:** {row['wikileaks_Category']}")

        st.markdown("---")
else:
    st.warning("No matching results found for the selected news article.")

# Footer analysis
st.sidebar.header("Analysis")
if view_option == "Fuzzy Matching":
    st.sidebar.subheader("Top 10 Most Common Entities")
    most_common_entities = fuzzy_df['common_entities'].explode().value_counts().head(10)
    st.sidebar.write(most_common_entities)
else:
    st.sidebar.subheader("Top 10 Most Common Entities")
    most_common_entities = bert_df['news_entities'].explode().value_counts().head(10)
    st.sidebar.write(most_common_entities)
