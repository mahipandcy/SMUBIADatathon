import streamlit as st
import pandas as pd
import ast
import altair as alt
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import itertools
from collections import defaultdict, Counter
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
import time
import os

#############################################
# Helper: Data Loading (Modularized & Cached)
#############################################

@st.cache_data(show_spinner=False)
def load_pickle_data(filepath: str) -> pd.DataFrame:
    """Loads a preprocessed pickle file and returns a DataFrame."""
    if os.path.exists(filepath):
        return pd.read_pickle(filepath)
    else:
        st.error(f"File {filepath} not found. Please create the pickle file first.")
        raise FileNotFoundError(f"{filepath} does not exist.")

def load_similarity_data() -> dict:
    """
    Loads preprocessed similarity analysis data from pickle files.
    Ensure that you have created these pickle files offline.
    """
    # Update these paths to your pickle file locations
    fuzzy_df = load_pickle_data("./data/fuzzy_clean.pkl")
    bert_df = load_pickle_data("./data/bert_clean.pkl")
    parsed_news_df = load_pickle_data("./data/parsed_news_clean.pkl")
    wikileaks_mapping_df = load_pickle_data("./data/wikileaks_mapping_clean.pkl")
    
    # Build a mapping from key to Wikileaks document text.
    key_to_text = pd.Series(wikileaks_mapping_df["Text"].values, index=wikileaks_mapping_df["key"]).to_dict()

    def get_unique_links(df):
        return df.drop_duplicates(subset="news_Link")["news_Link"].unique()
    
    fuzzy_unique_links = get_unique_links(fuzzy_df)
    bert_unique_links = get_unique_links(bert_df)
    
    # Preprocess entity columns if needed
    if "common_entities" in fuzzy_df.columns:
        fuzzy_df["common_entities"] = fuzzy_df["common_entities"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
    
    return {
        "fuzzy_df": fuzzy_df,
        "bert_df": bert_df,
        "parsed_news_df": parsed_news_df,
        "key_to_text": key_to_text,
        "fuzzy_unique_links": fuzzy_unique_links,
        "bert_unique_links": bert_unique_links
    }

@st.cache_data(show_spinner=False)
def load_threat_data() -> pd.DataFrame:
    """
    Loads preprocessed threat analysis data from pickle files.
    Ensure that you have preprocessed and saved the data offline.
    """
    # Update these paths to your pickle file locations
    sentencebert_df = load_pickle_data("./data/sentencebert_clean.pkl")
    news_excerpts_df = load_pickle_data("./data/news_excerpts_clean.pkl")
    
    sentencebert_df = sentencebert_df.merge(
        news_excerpts_df[['Link', 'Text']],
        how='left',
        left_on='news_Link',
        right_on='Link'
    )
    sentencebert_df.rename(columns={'Text': 'news_content'}, inplace=True)
    return sentencebert_df

#############################################
# GEOLOCATION: For Heatmap
#############################################

# Initialize geolocator with a proper user agent
geolocator = Nominatim(user_agent="your_app_name_here")

@st.cache_data(show_spinner=False)
def get_cached_lat_lon(country: str):
    """
    Returns the latitude and longitude for a given country.
    The result is cached so that subsequent calls with the same country name do not trigger a new API request.
    """
    try:
        time.sleep(1)  # Avoid rate limiting
        location = geolocator.geocode(country)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        st.write(f"Error geocoding {country}: {e}")
        return None, None

#############################################
# GLOBAL SIDEBAR (Restored, without Top 15 Entities)
#############################################

# Load similarity data once for sidebar use.
sim_data = load_similarity_data()

st.sidebar.title("Article Selection")

# Article selection options
view_option = st.sidebar.selectbox("Choose Method", ["Fuzzy Matching", "Sentence-BERT"])
selection_method = st.sidebar.radio("Select by", ["News Link", "News Excerpt Text"])

if selection_method == "News Link":
    st.sidebar.subheader("News Links")
    if view_option == "Fuzzy Matching":
        available_links = sim_data["fuzzy_unique_links"]
    else:
        available_links = sim_data["bert_unique_links"]
    selected_news = st.sidebar.selectbox("Select a News Link", available_links)
    selected_news_link = selected_news
else:
    st.sidebar.subheader("News Excerpts")
    available_texts = sim_data["parsed_news_df"]["Text"].dropna().unique()
    selected_text = st.sidebar.selectbox("Select a News Excerpt", available_texts)
    selected_news_link = sim_data["parsed_news_df"][sim_data["parsed_news_df"]["Text"] == selected_text].iloc[0]["Link"]

# Additional similarity settings (restored from your original sidebar)
if view_option == "Fuzzy Matching":
    data_for_categories = sim_data["fuzzy_df"]
else:
    data_for_categories = sim_data["bert_df"]

def get_categories(df):
    return df['wikileaks_Category'].dropna().unique()

categories = get_categories(data_for_categories)
st.sidebar.header("Category Filter")
category_option = st.sidebar.selectbox("Select Category", ["All"] + list(categories))

#############################################
# TAB 1: Wikileaks Similarity Analysis
#############################################

def similarity_analysis(selected_news_link, view_option, category_option, sim_data):
    st.header("Wikileaks and News Excerpt Similarity Analysis")
    parsed_news_df = sim_data["parsed_news_df"]
    key_to_text = sim_data["key_to_text"]

    if view_option == "Fuzzy Matching":
        data_df = sim_data["fuzzy_df"]
    else:
        data_df = sim_data["bert_df"]

    # Modified filtering function that takes a parameter for number of rows
    @st.cache_data(show_spinner=False)
    def get_filtered_df(df, news_link, cat_option, n):
        filtered = df[df["news_Link"] == news_link].sort_values(by="content_similarity", ascending=False)
        if cat_option != "All":
            filtered = filtered[filtered["wikileaks_Category"] == cat_option]
        return filtered.head(n)
    
    # Use one filtered DataFrame for the top 3 display and one for the scatter plot (top 30)
    filtered_df_top = get_filtered_df(data_df, selected_news_link, category_option, 3)
    filtered_df_scatter = get_filtered_df(data_df, selected_news_link, category_option, 30)

    def get_news_text(link):
        result = parsed_news_df[parsed_news_df["Link"] == link]
        if not result.empty:
            return result.iloc[0]["Text"]
        return "Text not found."

    st.markdown("## Selected News Article")
    if not filtered_df_top.empty:
        article_text = get_news_text(selected_news_link)
        st.write(article_text)
        st.markdown("### Entities:")
        st.write(filtered_df_top.iloc[0].get('news_entities', "N/A"))
        st.markdown("### Relationships:")
        st.write(filtered_df_top.iloc[0].get('news_relationships', "N/A"))
        # Display as Topic / Sector.
        st.markdown("### Categories (Topic / Sector):")
        topic = filtered_df_top.iloc[0].get('news_Category_x', "N/A")
        sector = filtered_df_top.iloc[0].get('news_Category_y', "N/A")
        st.write(f"{topic} / {sector}")
        st.markdown("### Source:")
        st.write(selected_news_link)
    else:
        st.warning("No matching results found for the selected news article.")

    st.markdown("---")
    st.markdown("## Top 3 Most Similar Wikileaks Documents")
    if not filtered_df_top.empty:
        cols = st.columns([1, 0.05, 1, 0.05, 1])
        with cols[1]:
            st.markdown("<div style='border-left: 2px solid grey; height: 100%;'></div>", unsafe_allow_html=True)
        with cols[3]:
            st.markdown("<div style='border-left: 2px solid grey; height: 100%;'></div>", unsafe_allow_html=True)
        for i, col in enumerate([cols[0], cols[2], cols[4]]):
            with col:
                st.markdown(f"### Similarity Score: {filtered_df_top.iloc[i]['content_similarity']:.2f}%")
                st.markdown("### Wikileaks Document")
                if view_option == "Sentence-BERT":
                    doc_key = filtered_df_top.iloc[i]['wikileaks_Text']
                    doc_text = key_to_text.get(doc_key, f"Document not found for key: {doc_key}")
                    st.write(doc_text)
                else:
                    st.write(filtered_df_top.iloc[i]['wikileaks_Text'])
                st.markdown(f"**Category Match:** {filtered_df_top.iloc[i]['wikileaks_Category']}")
    else:
        st.info("No similar Wikileaks documents to display.")

    st.markdown("## Additional Visualizations")
    # Word Cloud
    st.markdown("### News Article Word Cloud")
    article_text_for_wc = get_news_text(selected_news_link)
    if article_text_for_wc:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(article_text_for_wc)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(plt)
    else:
        st.info("No news text available for word cloud visualization.")
    
    # Entity–Relationship Graph using Pyvis
    st.markdown("### Entity–Relationship Graph for Selected Article")
    if not filtered_df_top.empty:
        news_relationships = filtered_df_top.iloc[0].get("news_relationships", [])
        if isinstance(news_relationships, str):
            news_relationships = ast.literal_eval(news_relationships)
        groups = defaultdict(list)
        for rel in news_relationships:
            groups[rel[2]].append(rel)
        def build_entity_relationship_graph(rel_groups):
            G = nx.Graph()
            for key, group in rel_groups.items():
                if len(group) == 2:
                    subj_tuple, obj_tuple = group[0], group[1]
                    subject = subj_tuple[0]
                    relation = subj_tuple[1]
                    obj = obj_tuple[0]
                    G.add_node(subject, label=subject, type="entity")
                    G.add_node(obj, label=obj, type="entity")
                    rel_node_id = f"rel_{key}"
                    G.add_node(rel_node_id, label=relation, shape="box", type="relation")
                    G.add_edge(subject, rel_node_id)
                    G.add_edge(rel_node_id, obj)
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
    
    # Entity Co-occurrence Heatmap
    st.markdown("### Entity Co-occurrence Heatmap")
    if not filtered_df_top.empty:
        entities = filtered_df_top.iloc[0].get("news_entities", [])
        if isinstance(entities, str):
            entities = ast.literal_eval(entities)
        def get_entity_name(ent):
            if isinstance(ent, (list, tuple)):
                return ent[0]
            return ent
        entities = [get_entity_name(e) for e in entities]
        if entities and isinstance(entities, list):
            unique_entities = sorted(set(entities))
            co_occurrence = pd.DataFrame(0, index=unique_entities, columns=unique_entities)
            for pair in itertools.combinations(entities, 2):
                co_occurrence.loc[pair[0], pair[1]] += 1
                co_occurrence.loc[pair[1], pair[0]] += 1
            for entity in unique_entities:
                co_occurrence.loc[entity, entity] = entities.count(entity)
            plt.figure(figsize=(10, 8))
            sns.heatmap(co_occurrence, annot=True, cmap="YlGnBu", fmt="d")
            st.pyplot(plt)
        else:
            st.info("No entities available for the co-occurrence heatmap.")
    else:
        st.info("No data available to generate the co-occurrence heatmap.")
    
    # Sankey Diagram for Entity Relationships
    st.markdown("### Sankey Diagram for Entity Relationships")
    if not filtered_df_top.empty:
        news_relationships = filtered_df_top.iloc[0].get("news_relationships", [])
        if isinstance(news_relationships, str):
            news_relationships = ast.literal_eval(news_relationships)
        groups = defaultdict(list)
        for rel in news_relationships:
            groups[rel[2]].append(rel)
        nodes = []
        node_to_index = {}
        source_indices = []
        target_indices = []
        values = []
        def add_node(label):
            if label not in node_to_index:
                node_to_index[label] = len(nodes)
                nodes.append(label)
            return node_to_index[label]
        for key, group in groups.items():
            if len(group) == 2:
                subj = group[0][0]
                relation = group[0][1]
                obj = group[1][0]
                subj_idx = add_node(subj)
                rel_idx = add_node(relation)
                obj_idx = add_node(obj)
                source_indices.append(subj_idx)
                target_indices.append(rel_idx)
                values.append(1)
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

    # Additional Visualization: Altair Scatter Plot using Top 30 Similarity Entries
    st.markdown("## Additional Visualization: Similarity vs. Category")
    if not filtered_df_scatter.empty:
        alt_chart = alt.Chart(filtered_df_scatter).mark_circle(size=100).encode(
            x=alt.X("content_similarity:Q", title="Content Similarity (%)"),
            y=alt.Y("wikileaks_Category:N", title="Wikileaks Category"),
            color="wikileaks_Category:N",
            # Tooltip now includes news_Link so that each dot shows its news link
            tooltip=["content_similarity", "wikileaks_Category", "news_Link"]
        ).properties(
            width=600,
            height=300,
            title="Scatter Plot of Similarity Score vs. Category (Top 30)"
        )
        st.altair_chart(alt_chart, use_container_width=True)
    else:
        st.info("No data available for the scatter plot.")

#############################################
# TAB 2: Analysis Dashboard (Static Data + Category Analysis)
#############################################

def threat_analysis(selected_news_link, sim_data):
    st.header("Analysis Dashboard")
    
    # ----- Existing Threat Analysis Visualizations -----
    static_threat_data = {
        "Country": [
            "Denmark", "Portugal", "Hong Kong", "China", "Vietnam", "Singapore",
            "Ukraine", "South Korea", "Japan", "North Korea", "India", "Pakistan",
            "Canada", "SINGAPORE", "Afghanistan", "Indonesia", "US", "Philippines",
            "Nigeria", "Norway", "Türkiye", "Kenya", "Uganda", "Ethiopia", "Somalia",
            "Yemen", "Israel", "Italy", "Malaysia", "France", "Niger", "HONG KONG",
            "Slovakia", "Australia", "New Zealand", "Ireland", "Iraq", "Germany",
            "Hungary", "Papua New Guinea", "Taiwan", "Belarus"
        ],
        "High Threats": [
            0, 1, 1, 24, 0, 3, 10, 4, 7, 12, 5, 1, 0, 1, 2, 1, 6, 1, 1, 1,
            2, 0, 0, 1, 3, 1, 11, 0, 4, 6, 1, 1, 1, 3, 0, 1, 0, 1, 2, 0, 2, 1
        ],
        "Medium Threats": [
            1, 0, 2, 8, 1, 2, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 2, 0, 0, 1,
            1, 2, 1, 0, 0, 1, 2, 1, 1, 0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 1, 0, 0
        ],
        "Low Threats": [
            0, 0, 0, 0, 0, 4, 2, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0
        ]
    }
    threat_df = pd.DataFrame(static_threat_data)
    threat_df["Total Threats"] = (threat_df["High Threats"] +
                                  threat_df["Medium Threats"] +
                                  threat_df["Low Threats"])
    
    threat_df = threat_df.sort_values("Total Threats", ascending=False).reset_index(drop=True)
    
    st.subheader("Threat Counts by Country")
    st.dataframe(threat_df)
    
    bar_fig = px.bar(
        threat_df,
        x="Country",
        y=["High Threats", "Medium Threats", "Low Threats"],
        barmode="group",
        title="Threat Levels by Country",
        labels={"value": "Count", "variable": "Threat Level"},
        category_orders={"Country": threat_df["Country"].tolist()}
    )
    st.plotly_chart(bar_fig, use_container_width=True)
    
    threat_df["Threat Score"] = (threat_df["High Threats"] * 3 +
                                 threat_df["Medium Threats"] * 2 +
                                 threat_df["Low Threats"] * 1)
    scatter_fig = px.scatter(
        threat_df,
        x="Country",
        y="Threat Score",
        size="Threat Score",
        title="Overall Threat Score by Country",
        labels={"Threat Score": "Threat Score (High=3, Medium=2, Low=1)"},
        category_orders={"Country": threat_df["Country"].tolist()}
    )
    st.plotly_chart(scatter_fig, use_container_width=True)
    
    # ----- New Category Analysis Section -----
    st.markdown("## Category Analysis from Similarity Data")
    similarity_df = sim_data["fuzzy_df"]  # using fuzzy matching data; adjust if needed
    selected_rows = similarity_df[similarity_df["news_Link"] == selected_news_link]
    if not selected_rows.empty:
        selected_row = selected_rows.iloc[0]
        topic = selected_row.get("news_Category_x", "N/A")
        sector = selected_row.get("news_Category_y", "N/A")
    else:
        topic, sector = "N/A", "N/A"
    st.write(f"**Selected article belongs to:**")
    st.write(f"- **Topic:** {topic}")
    st.write(f"- **Sector:** {sector}")

    dist_topic = similarity_df["news_Category_x"].value_counts().reset_index()
    dist_topic.columns = ["Topic", "Count"]
    dist_topic["Selected"] = dist_topic["Topic"] == topic

    fig_topic = px.bar(dist_topic, x="Topic", y="Count",
                   title="Topic Distribution",
                   color="Selected",
                   color_discrete_map={True: "red", False: "blue"})
    st.plotly_chart(fig_topic, use_container_width=True)

    dist_sector = similarity_df["news_Category_y"].value_counts().reset_index()
    dist_sector.columns = ["Sector", "Count"]
    dist_sector["Selected"] = dist_sector["Sector"] == sector

    fig_sector = px.bar(dist_sector, x="Sector", y="Count",
                   title="Sector Distribution",
                   color="Selected",
                   color_discrete_map={True: "red", False: "blue"})
    st.plotly_chart(fig_sector, use_container_width=True)

#############################################
# TAB 3: Threat Heatmap & Global Visualizations
#############################################

def geographical_heatmap():
    st.header("Threat Heatmap")
    st.markdown("This heatmap visualizes the total threat count by country using Folium.")
    
    static_threat_data = {
        "Country": [
            "Denmark", "Portugal", "Hong Kong", "China", "Vietnam", "Singapore",
            "Ukraine", "South Korea", "Japan", "North Korea", "India", "Pakistan",
            "Canada", "SINGAPORE", "Afghanistan", "Indonesia", "US", "Philippines",
            "Nigeria", "Norway", "Türkiye", "Kenya", "Uganda", "Ethiopia", "Somalia",
            "Yemen", "Israel", "Italy", "Malaysia", "France", "Niger", "HONG KONG",
            "Slovakia", "Australia", "AI", "New Zealand", "Ireland", "Iraq", "Germany",
            "Hungary", "Papua New Guinea", "Taiwan", "Belarus"
        ],
        "High Threats": [
            0, 1, 1, 24, 0, 3, 10, 4, 7, 12, 5, 1, 0, 1, 2, 1, 6, 1, 1, 1,
            2, 0, 0, 1, 3, 1, 11, 0, 4, 6, 1, 1, 1, 3, 0, 0, 1, 0, 1, 2, 0, 2, 1
        ],
        "Medium Threats": [
            1, 0, 2, 8, 1, 2, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 2, 0, 0, 1,
            1, 2, 1, 0, 0, 1, 2, 1, 1, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 1, 0, 0
        ],
        "Low Threats": [
            0, 0, 0, 0, 0, 4, 2, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 0
        ]
    }
    threat_df = pd.DataFrame(static_threat_data)
    threat_df["Total Threats"] = threat_df["High Threats"] + threat_df["Medium Threats"] + threat_df["Low Threats"]
    
    country_counts = threat_df.set_index("Country")["Total Threats"].to_dict()
    
    m = folium.Map(location=[20, 0], zoom_start=2)
    heat_data = []
    for country, count in country_counts.items():
        lat_lon = get_cached_lat_lon(country)
        if lat_lon and lat_lon[0] is not None and lat_lon[1] is not None:
            heat_data.append([lat_lon[0], lat_lon[1], count])
    if heat_data:
        HeatMap(heat_data).add_to(m)
    else:
        st.info("No valid latitude/longitude data found for heatmap.")
    
    m.save('threats_map.html')
    st.markdown("Map saved as 'threats_map.html'")
    components.html(m._repr_html_(), height=500)
    
    st.markdown("## Global Visualization: Total Threats by Country")
    bar_fig = px.bar(threat_df, x="Country", y="Total Threats",
                     title="Total Threats by Country",
                     labels={"Total Threats": "Total Threat Count"})
    st.plotly_chart(bar_fig, use_container_width=True)
    
    st.markdown("## Global Visualization: Threat Distribution (Pie Chart)")
    total = threat_df["Total Threats"].sum()
    threat_df["percent"] = threat_df["Total Threats"] / total * 100
    threat_df["display_text"] = threat_df["percent"].apply(lambda x: f"{x:.1f}%" if x >= 2 else "")
    
    pie_fig = px.pie(
        threat_df,
        names="Country",
        values="Total Threats",
        title="Threat Distribution by Country"
    )
    pie_fig.update_traces(text=threat_df["display_text"], textposition='inside', textinfo='text')
    
    st.plotly_chart(pie_fig, use_container_width=True)

#############################################
# MAIN APP: Multi-Tab Layout
#############################################

st.title("Combined Analysis Dashboard")
tabs = st.tabs(["Wikileaks Similarity Analysis", "Analysis Dashboard", "Threat Heatmap"])

with tabs[0]:
    similarity_analysis(selected_news_link, view_option, category_option, sim_data)

with tabs[1]:
    threat_analysis(selected_news_link, sim_data)

with tabs[2]:
    geographical_heatmap()
