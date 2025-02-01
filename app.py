import streamlit as st
import pandas as pd
import ast  # For converting string representations of lists to actual lists
import altair as alt
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# -----------------------------------------------
# Data Loading and Caching Functions
# -----------------------------------------------
@st.cache_data
def load_data():
    fuzzy_df = pd.read_excel("./data/cited_judgments_with_news_articles.xlsx")
    bert_df = pd.read_excel("./data/sentencebert_results.xlsx")
    return fuzzy_df, bert_df

fuzzy_df, bert_df = load_data()

@st.cache_data
def get_unique_links(df):
    return df.drop_duplicates(subset="news_Link")["news_Link"].unique()

fuzzy_unique_links = get_unique_links(fuzzy_df)
bert_unique_links = get_unique_links(bert_df)

@st.cache_data
def preprocess_entities(df):
    df = df.copy()
    if "common_entities" in df.columns:
        df["common_entities"] = df["common_entities"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
    return df

fuzzy_df = preprocess_entities(fuzzy_df)

# -----------------------------------------------
# Sidebar: Input Options and Analysis
# -----------------------------------------------
st.sidebar.title("Settings & Analysis")

# Similarity method selection
st.sidebar.header("Similarity Method")
view_option = st.sidebar.selectbox("Choose Method", ["Fuzzy Matching", "Sentence-BERT"])

# News selection method
st.sidebar.header("News Selection")
selection_method = st.sidebar.radio("Select by", ["News Link", "News Excerpt Text"])

# Depending on the similarity method, choose the appropriate dataset and links
if view_option == "Fuzzy Matching":
    available_links = fuzzy_unique_links
    filtered_df_unique = fuzzy_df
else:
    available_links = bert_unique_links
    filtered_df_unique = bert_df

# Choose by news link or excerpt
if selection_method == "News Link":
    st.sidebar.subheader("News Links")
    selected_news = st.sidebar.selectbox("Select a News Link", available_links)
    news_link = selected_news
else:
    st.sidebar.subheader("News Excerpts")
    available_texts = filtered_df_unique["news_Text"].dropna().unique()
    selected_text = st.sidebar.selectbox("Select a News Excerpt", available_texts)
    news_link = filtered_df_unique[filtered_df_unique["news_Text"] == selected_text].iloc[0]["news_Link"]

# Category filter
@st.cache_data
def get_categories(df):
    return df['wikileaks_Category'].dropna().unique()

categories = get_categories(fuzzy_df if view_option == "Fuzzy Matching" else bert_df)
st.sidebar.header("Category Filter")
category_option = st.sidebar.selectbox("Select Category", ["All"] + list(categories))

# -----------------------------------------------
# Sidebar: Additional Analysis Section
# -----------------------------------------------
st.sidebar.markdown("---")
st.sidebar.header("Additional Analysis")
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

# -----------------------------------------------
# Main Content: Results Display
# -----------------------------------------------
st.title("Wikileaks and News Excerpt Similarity Analysis")
st.markdown("Explore how closely news articles match with Wikileaks documents. Below you can view article details, similar Wikileaks documents, and additional visualizations.")

@st.cache_data
def get_filtered_df(df, news_link, category_option):
    filtered = df[df["news_Link"] == news_link].sort_values(by="content_similarity", ascending=False)
    if category_option != "All":
        filtered = filtered[filtered["wikileaks_Category"] == category_option]
    return filtered.head(5)

filtered_df_sorted = get_filtered_df(fuzzy_df if view_option == "Fuzzy Matching" else bert_df, news_link, category_option)

# Segment: Selected News Article Details
st.markdown("## Selected News Article")
if not filtered_df_sorted.empty:
    with st.container():
        st.write(filtered_df_sorted.iloc[0]["news_Text"])
        st.markdown(f"**Entities:** {filtered_df_sorted.iloc[0]['news_entities']}")
        st.markdown(f"**Relationships:** {filtered_df_sorted.iloc[0]['news_relationships']}")
        st.markdown(f"**Categories:** {filtered_df_sorted.iloc[0]['news_Category_x']} / {filtered_df_sorted.iloc[0]['news_Category_y']}")
        st.markdown(f"**Source:** {news_link}")
else:
    st.warning("No matching results found for the selected news article.")

st.markdown("---")

# Segment: Top Similar Wikileaks Documents
st.markdown("## Top 5 Most Similar Wikileaks Documents")
if not filtered_df_sorted.empty:
    for _, row in filtered_df_sorted.iterrows():
        with st.container():
            st.markdown("### Wikileaks Document")
            st.write(row['wikileaks_Text'])
            st.markdown(f"**Similarity Score:** {row['content_similarity']:.2f}%")
            st.markdown(f"**Category Match:** {row['wikileaks_Category']}")
            st.markdown("---")
else:
    st.info("No similar Wikileaks documents to display.")

# -----------------------------------------------
# Additional Visualizations
# -----------------------------------------------
st.markdown("## Additional Visualizations")

# 1. Word Cloud: News Article Text
st.markdown("### News Article Word Cloud")
news_texts = filtered_df_sorted["news_Text"].dropna().tolist()
if news_texts:
    combined_text = " ".join(news_texts)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(combined_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)
else:
    st.info("No news text available for word cloud visualization.")

# 2. Entity–Relationship Graph for Selected Article
st.markdown("### Entity–Relationship Graph for Selected Article")
if not filtered_df_sorted.empty:
    # Get the selected article's relationship data.
    news_relationships = filtered_df_sorted.iloc[0]["news_relationships"]
    if isinstance(news_relationships, str):
        news_relationships = ast.literal_eval(news_relationships)

    # Group relationships by the third element so that pairs (subject, relation, object) can be formed.
    from collections import defaultdict
    groups = defaultdict(list)
    for rel in news_relationships:
        groups[rel[2]].append(rel)

    import networkx as nx
    from pyvis.network import Network
    import streamlit.components.v1 as components

    def build_entity_relationship_graph(rel_groups):
        """
        Build a graph where for each complete relationship (groups with 2 tuples),
        an intermediate relationship node is created. Two edges are added:
        subject -> relationship node and relationship node -> object.
        """
        G = nx.Graph()
        for key, group in rel_groups.items():
            if len(group) == 2:
                # Assume the two tuples form a complete relationship.
                subj_tuple, obj_tuple = group[0], group[1]
                subject = subj_tuple[0]
                relation = subj_tuple[1]  # Assuming both tuples have the same verb.
                obj = obj_tuple[0]
                # Add nodes for the entities.
                G.add_node(subject, label=subject, type="entity")
                G.add_node(obj, label=obj, type="entity")
                # Create a unique relationship node.
                rel_node_id = f"rel_{key}"
                G.add_node(rel_node_id, label=relation, shape="box", type="relation")
                # Connect subject -> relationship and relationship -> object.
                G.add_edge(subject, rel_node_id)
                G.add_edge(rel_node_id, obj)
            else:
                # Optionally, you could handle incomplete relationships here.
                continue
        return G

    def draw_pyvis_graph(G):
        net = Network(height="500px", width="100%", notebook=False)
        net.from_nx(G)
        # Optionally adjust physics for better layout.
        net.repulsion(node_distance=200, central_gravity=0.3)
        net.save_graph("entity_relationship_graph.html")
        with open("entity_relationship_graph.html", "r", encoding="utf-8") as html_file:
            source_code = html_file.read()
        return source_code

    G = build_entity_relationship_graph(groups)
    graph_html = draw_pyvis_graph(G)
    components.html(graph_html, height=550, scrolling=True)
else:
    st.info("No selected article available to generate an entity–relationship graph.")
