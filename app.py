import streamlit as st
import pandas as pd
import ast  # For converting string representations of lists to actual lists

# Cache data loading
@st.cache_data
def load_data():
    fuzzy_df = pd.read_excel("./data/cited_judgments_with_news_articles.xlsx")
    bert_df = pd.read_excel("./data/sentencebert_results.xlsx")
    return fuzzy_df, bert_df

fuzzy_df, bert_df = load_data()

# Cache unique links extraction
@st.cache_data
def get_unique_links(df):
    return df.drop_duplicates(subset="news_Link")["news_Link"].unique()

fuzzy_unique_links = get_unique_links(fuzzy_df)
bert_unique_links = get_unique_links(bert_df)

# Cache entity preprocessing
@st.cache_data
def preprocess_entities(df):
    df = df.copy()
    if "common_entities" in df.columns:
        df["common_entities"] = df["common_entities"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    return df

fuzzy_df = preprocess_entities(fuzzy_df)

# Streamlit app
st.title("Wikileaks and News Excerpt Similarity Analysis")

# Sidebar for user input
st.sidebar.header("Input Options")
view_option = st.sidebar.selectbox("Choose Similarity Method", ["Fuzzy Matching", "Sentence-BERT"])

# Allow selection by news link or news text
selection_method = st.sidebar.radio("Select by", ["News Link", "News Excerpt Text"])

# Display options based on the selection method
if view_option == "Fuzzy Matching":
    available_links = fuzzy_unique_links
    filtered_df_unique = fuzzy_df
else:
    available_links = bert_unique_links
    filtered_df_unique = bert_df

if selection_method == "News Link":
    st.sidebar.subheader("Available News Links")
    selected_news = st.sidebar.selectbox("Select a News Link", available_links)
    news_link = selected_news
else:
    st.sidebar.subheader("Available News Excerpts")
    available_texts = filtered_df_unique["news_Text"].dropna().unique()
    selected_text = st.sidebar.selectbox("Select a News Excerpt", available_texts)
    news_link = filtered_df_unique[filtered_df_unique["news_Text"] == selected_text].iloc[0]["news_Link"]

# Sidebar for category selection
@st.cache_data
def get_categories(df):
    # Ensure no NaN values are included in the unique categories
    return df['wikileaks_Category'].dropna().unique()

categories = get_categories(fuzzy_df if view_option == "Fuzzy Matching" else bert_df)

# Add "All" category as the default option to select all categories
category_option = st.sidebar.selectbox("Select Category", ["All"] + list(categories))

# Cache filtering
@st.cache_data
def get_filtered_df(df, news_link, category_option):
    filtered = df[df["news_Link"] == news_link].sort_values(by="content_similarity", ascending=False)
    if category_option != "All":
        filtered = filtered[filtered["wikileaks_Category"] == category_option]
    return filtered.head(5)

filtered_df_sorted = get_filtered_df(fuzzy_df if view_option == "Fuzzy Matching" else bert_df, news_link, category_option)

# Display results for the selected news article
if not filtered_df_sorted.empty:
    st.subheader("Selected News Article")
    st.write(filtered_df_sorted.iloc[0]["news_Text"])
    st.write(f"**Entities:** {filtered_df_sorted.iloc[0]['news_entities']}")
    st.write(f"**Relationships:** {filtered_df_sorted.iloc[0]['news_relationships']}")
    st.write(f"**Categories:** {filtered_df_sorted.iloc[0]['news_Category_x']} / {filtered_df_sorted.iloc[0]['news_Category_y']}")
    st.write(f"**Source:** {news_link}")

    st.subheader("Top 5 Most Similar Wikileaks Documents")
    for _, row in filtered_df_sorted.iterrows():
        st.write(f"**Wikileaks Text:** {row['wikileaks_Text']}")
        st.write(f"**Similarity Score:** {row['content_similarity']:.2f}%")
        st.write(f"**Category Match:** {row['wikileaks_Category']}")
        st.markdown("---")
else:
    st.warning("No matching results found for the selected news article.")

# Sidebar Analysis
st.sidebar.header("Analysis")
st.sidebar.subheader("Top 15 Most Common Entities")

@st.cache_data
def get_top_entities(df, column):
    if column in df.columns:
        return pd.Series([entity for sublist in df[column].dropna() for entity in sublist]).value_counts().head(15)

if view_option == "Fuzzy Matching":
    top_entities = get_top_entities(fuzzy_df, "common_entities")
else:
    top_entities = get_top_entities(bert_df, "news_entities")

if top_entities is not None:
    st.sidebar.write(top_entities)
