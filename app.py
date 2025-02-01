import streamlit as st
import pandas as pd
import ast  # For converting string representations of lists to actual lists
import altair as alt
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import itertools
from collections import defaultdict
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import plotly.graph_objects as go

# -----------------------------------------------
# Data Loading and Caching Functions
# -----------------------------------------------
@st.cache_data
def load_data():
    fuzzy_df = pd.read_excel("./data/cited_judgments_with_news_articles.xlsx")
    bert_df = pd.read_excel("./data/sentencebert_results.xlsx")
    # Load the smaller dataset with parsed news excerpts
    parsed_news_df = pd.read_excel("./data/processed_news_excerpts_parsed_with_category.xlsx")
    return fuzzy_df, bert_df, parsed_news_df

fuzzy_df, bert_df, parsed_news_df = load_data()

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

# Choose by news link or excerpt (link is the common key)
if selection_method == "News Link":
    st.sidebar.subheader("News Links")
    selected_news = st.sidebar.selectbox("Select a News Link", available_links)
    news_link = selected_news
else:
    st.sidebar.subheader("News Excerpts")
    # Use the Text from the parsed dataset for display in the selection box.
    available_texts = parsed_news_df["Text"].dropna().unique()
    selected_text = st.sidebar.selectbox("Select a News Excerpt", available_texts)
    # Look up the corresponding link in the parsed dataset.
    news_link = parsed_news_df[parsed_news_df["Text"] == selected_text].iloc[0]["Link"]

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
def get_top_entities(df, column, is_sentencebert=False):
    if column in df.columns:
        if is_sentencebert:
            #handling the Sentence-BERT 'news_entities' column
            entities = df[column].dropna().explode().unique()  
            entity_series = pd.Series(entities).value_counts().head(15)  #getting the top 15 
            return pd.DataFrame({
                "Entity": entity_series.index
            })
        else:
            # Handle the 'common_entities' column for fuzzy matching
            return pd.Series([entity for sublist in df[column].dropna() for entity in sublist]).value_counts().head(15)

# Function to apply styling (optional)
def apply_styling(entity_df):
    return entity_df.style.applymap(
        lambda x: 'background-color: yellow' if isinstance(x, str) else '', subset='Entity'
    )

# Determine which view option is selected
if view_option == "Sentence-BERT":
    top_entities = get_top_entities(bert_df, "news_entities", is_sentencebert=True)
else:
    top_entities = get_top_entities(fuzzy_df, "common_entities")

# Display the top entities
if top_entities is not None:
    if view_option == "Sentence-BERT":
        # Display the index and entity as a styled DataFrame in the sidebar
        st.sidebar.write(top_entities)
    else:
        # Display the entities directly for fuzzy matching
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
    return filtered.head(3)  # Changed to top 3

filtered_df_sorted = get_filtered_df(fuzzy_df if view_option == "Fuzzy Matching" else bert_df, news_link, category_option)

# Helper function to get the news article text from the parsed dataset using the link.
def get_news_text(link):
    # Assuming that the Link column in parsed_news_df uniquely identifies each article.
    result = parsed_news_df[parsed_news_df["Link"] == link]
    if not result.empty:
        return result.iloc[0]["Text"]
    return "Text not found."

# Segment: Selected News Article Details
st.markdown("## Selected News Article")
if not filtered_df_sorted.empty:
    with st.container():
        article_text = get_news_text(news_link)
        st.write(article_text)
        # Only enlarge the label words; the content remains normal.
        st.markdown("## Entities:")
        st.write(filtered_df_sorted.iloc[0]['news_entities'])
        st.markdown("## Relationships:")
        st.write(filtered_df_sorted.iloc[0]['news_relationships'])
        st.markdown("## Categories:")
        st.write(f"{filtered_df_sorted.iloc[0]['news_Category_x']} / {filtered_df_sorted.iloc[0]['news_Category_y']}")
        st.markdown("## Source:")
        st.write(news_link)
else:
    st.warning("No matching results found for the selected news article.")

st.markdown("---")

# Segment: Top Similar Wikileaks Documents (Top 3 in horizontal layout)
st.markdown("## Top 3 Most Similar Wikileaks Documents")
if not filtered_df_sorted.empty:
    # Create five columns to include vertical separators between the three main columns.
    cols = st.columns([1, 0.05, 1, 0.05, 1])
    
    # Add vertical separators in the separator columns using HTML.
    with cols[1]:
        st.markdown("<div style='border-left: 2px solid grey; height: 100%;'></div>", unsafe_allow_html=True)
    with cols[3]:
        st.markdown("<div style='border-left: 2px solid grey; height: 100%;'></div>", unsafe_allow_html=True)
    
    # Map the three Wikileaks documents to the three main columns.
    for i, col in enumerate([cols[0], cols[2], cols[4]]):
        with col:
            # Similarity score shown at the top
            st.markdown(f"### Similarity Score: {filtered_df_sorted.iloc[i]['content_similarity']:.2f}%")
            st.markdown("### Wikileaks Document")
            st.write(filtered_df_sorted.iloc[i]['wikileaks_Text'])
            st.markdown(f"**Category Match:** {filtered_df_sorted.iloc[i]['wikileaks_Category']}")
else:
    st.info("No similar Wikileaks documents to display.")

# -----------------------------------------------
# Additional Visualizations
# -----------------------------------------------
st.markdown("## Additional Visualizations")

# 1. Word Cloud: News Article Text (using the parsed text)
st.markdown("### News Article Word Cloud")
st.markdown("This word cloud visualizes the most frequent words found in the news article.")
article_text_for_wc = get_news_text(news_link)
if article_text_for_wc:
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(article_text_for_wc)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)
else:
    st.info("No news text available for word cloud visualization.")

# 2. Entity–Relationship Graph for Selected Article (using Pyvis)
st.markdown("### Entity–Relationship Graph for Selected Article")
st.markdown("This interactive graph displays the relationships between entities extracted from the news article.")
if not filtered_df_sorted.empty:
    # Get the selected article's relationship data.
    news_relationships = filtered_df_sorted.iloc[0]["news_relationships"]
    if isinstance(news_relationships, str):
        news_relationships = ast.literal_eval(news_relationships)

    # Group relationships by the third element so that pairs (subject, relation, object) can be formed.
    groups = defaultdict(list)
    for rel in news_relationships:
        groups[rel[2]].append(rel)

    def build_entity_relationship_graph(rel_groups):
        """
        Build a graph where for each complete relationship (groups with 2 tuples),
        an intermediate relationship node is created. Two edges are added:
        subject -> relationship node and relationship node -> object.
        """
        G = nx.Graph()
        for key, group in rel_groups.items():
            if len(group) == 2:
                subj_tuple, obj_tuple = group[0], group[1]
                subject = subj_tuple[0]
                relation = subj_tuple[1]  # Assuming both tuples have the same relation verb.
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
                continue
        return G

    def draw_pyvis_graph(G):
        net = Network(height="500px", width="100%", notebook=False)
        net.from_nx(G)
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

# 3. Entity Co-occurrence Heatmap
st.markdown("### Entity Co-occurrence Heatmap")
st.markdown("This heatmap illustrates how frequently pairs of entities occur together in the news article.")
if not filtered_df_sorted.empty:
    # Extract entities from the selected news article
    entities = filtered_df_sorted.iloc[0].get("news_entities", [])
    if isinstance(entities, str):
        entities = ast.literal_eval(entities)
    
    # Process entities: if an entity is a list (e.g., ['Meta', 'ORG']), take only the first element
    def get_entity_name(ent):
        if isinstance(ent, (list, tuple)):
            return ent[0]
        return ent

    entities = [get_entity_name(e) for e in entities]
    
    if entities and isinstance(entities, list):
        unique_entities = sorted(set(entities))
        # Initialize co-occurrence matrix
        co_occurrence = pd.DataFrame(0, index=unique_entities, columns=unique_entities)
        for pair in itertools.combinations(entities, 2):
            co_occurrence.loc[pair[0], pair[1]] += 1
            co_occurrence.loc[pair[1], pair[0]] += 1
        # Set self-occurrence counts (frequency of each entity)
        for entity in unique_entities:
            co_occurrence.loc[entity, entity] = entities.count(entity)
        plt.figure(figsize=(10, 8))
        sns.heatmap(co_occurrence, annot=True, cmap="YlGnBu", fmt="d")
        st.pyplot(plt)
    else:
        st.info("No entities available for the co-occurrence heatmap.")
else:
    st.info("No data available to generate the co-occurrence heatmap.")

# 4. Sankey Diagram for Entity Relationships
st.markdown("### Sankey Diagram for Entity Relationships")
st.markdown("This Sankey diagram visualizes the flow from subjects to relationships to objects among the extracted entities.")
if not filtered_df_sorted.empty:
    news_relationships = filtered_df_sorted.iloc[0].get("news_relationships", [])
    if isinstance(news_relationships, str):
        news_relationships = ast.literal_eval(news_relationships)
    # Group relationships (complete relationships have 2 entries)
    groups = defaultdict(list)
    for rel in news_relationships:
        groups[rel[2]].append(rel)
    nodes = []
    node_to_index = {}
    source_indices = []
    target_indices = []
    values = []
    # Helper function to add a node if not already added
    def add_node(label):
        if label not in node_to_index:
            node_to_index[label] = len(nodes)
            nodes.append(label)
        return node_to_index[label]
    # Build links from complete relationships
    for key, group in groups.items():
        if len(group) == 2:
            subj = group[0][0]
            relation = group[0][1]
            obj = group[1][0]
            subj_idx = add_node(subj)
            rel_idx = add_node(relation)
            obj_idx = add_node(obj)
            # Link from subject to relation
            source_indices.append(subj_idx)
            target_indices.append(rel_idx)
            values.append(1)
            # Link from relation to object
            source_indices.append(rel_idx)
            target_indices.append(obj_idx)
            values.append(1)
    if nodes and source_indices:
        sankey_fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color="blue"
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values
            )
        )])
        sankey_fig.update_layout(title_text="Entity-Relationship Sankey Diagram", font_size=10)
        st.plotly_chart(sankey_fig, use_container_width=True)
    else:
        st.info("Not enough relationship data to generate a Sankey diagram.")
else:
    st.info("No data available to generate the Sankey diagram.")
