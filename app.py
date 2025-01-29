import streamlit as st
import pandas as pd
import requests
from urllib.parse import urlparse

# Function to check the reliability of a news source
def check_reliability(news_link):
    # Here, we can use a simple API like Media Bias/Fact Check (MBFC) or other news rating APIs.
    # For this example, we'll check if the domain is known for reliability (this is a simplified method).
    
    trusted_sources = [
    "cnn.com","channelnewsasia.com", "bbc.com", "nytimes.com", "theguardian.com", "reuters.com",
    "aljazeera.com", "wsj.com", "forbes.com", "bbc.co.uk", "ft.com",
    "cnbc.com", "abcnews.go.com", "npr.org", "usatoday.com", "washingtonpost.com",
    "businessinsider.com", "time.com", "huffpost.com", "vox.com", "newsweek.com",
    "independent.co.uk", "theverge.com", "bloomberg.com", "politico.com", "thehill.com",
    "nationalgeographic.com", "economist.com", "apnews.com", "latimes.com", "cbsnews.com",
    "nbcnews.com", "ft.com", "thelocal.se", "elpais.com", "lemonde.fr", "derstandard.at",
    "spiegel.de", "scmp.com", "thetimes.co.uk", "newyorker.com", "thedailybeast.com",
    "guardian.co.uk", "dw.com", "theconversation.com", "axios.com", "republicworld.com",
    "thecut.com", "buzzfeednews.com", "theblaze.com", "thedailycaller.com", "thedailybeast.com",
    "motherjones.com", "infowars.com", "salon.com", "slate.com", "theintercept.com",
    "axios.com", "ctvnews.ca", "news.com.au", "bbc.com", "foxnews.com",
    "thechronicle.com", "theindependent.com", "theeconomist.com", "hbr.org", "theatlantic.com",
    "usatoday.com", "thehill.com", "latimes.com", "newyorkpost.com", "newsday.com",
    "foxnews.com", "theguardian.com", "newsweek.com", "worldnewsdailyreport.com", "china.org.cn",
    "theweek.com", "inc.com", "sciencealert.com", "fortune.com", "breakingnews.com",
    "cnn.co.uk", "gizmodo.com", "businessweek.com", "mit.edu", "space.com", "scientificamerican.com",
    "newscientist.com", "mashable.com", "techcrunch.com", "wired.com", "engadget.com",
    "digitaltrends.com", "techradar.com", "arstechnica.com", "ziffdavis.com", "euobserver.com",
    "theconversation.com", "un.org", "reuters.com", "bbc.com", "foxnews.com", "bloomberg.com",
    "financialtimes.com", "thetimes.co.uk", "dailycaller.com", "techradar.com", "sfgate.com",
    "thefinancialexpress.com", "dw.com", "independent.co.uk", "thetimestv.com", "politico.eu",
    "thediplomat.com", "theguardian.co.uk", "thegurdian.com", "theblaze.com", "gulfnews.com",
    "themarysue.com", "thedailyrecord.co.uk", "thehill.com", "thesun.co.uk", "summitdaily.com",
    "sfgate.com", "expatica.com", "royalcentral.co.uk", "foreignpolicy.com", "theplaidzebra.com",
    "mic.com", "theconversation.com", "dev.to", "learn.microsoft.com", "uxdesign.cc", "greentechmedia.com",
    "thedialogue.org", "theastronauts.com", "timesofindia.indiatimes.com", "mashable.com",
    "geekwire.com", "wired.co.uk", "openai.com", "techxplore.com", "slashdot.org", "gadgets360.com",
    "airtable.com", "wipo.int", "locusplatforms.com", "harvard.edu", "charteredaccountants.com",
    "nasa.gov", "newyorker.com", "expatlife.co", "academic.oup.com", "bbcnews.com", "bbc.co.uk",
    "theroot.com", "theverge.com", "techradar.com", "cnbc.com", "cbsnews.com", "thedailybeast.com",
    "summitdaily.com", "geek.com", "singularityhub.com", "gizmodo.com", "cloud.google.com",
    "etonline.com", "space.com", "livescience.com", "nationalgeographic.com", "phys.org", "mentalfloss.com",
    "dailystar.co.uk", "examiner.com", "thedailybeast.com", "stjude.org", "ted.com", "events.kickstarter.com",
    "weather.com", "openculture.com", "sciencedaily.com", "educationweek.org", "researchgate.net"
]
  # Add trusted sources as needed
    domain = urlparse(news_link).netloc
    
    if any(trusted_source in domain for trusted_source in trusted_sources):
        return "Reliable Source"
    else:
        return "Unverified Source"

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
    # Filter out rows where common_entities is '[]'
    filtered_fuzzy_df = fuzzy_df[fuzzy_df['common_entities'] != '[]']
    
    # Explode the 'common_entities' column and count the occurrences
    most_common_entities = filtered_fuzzy_df['common_entities'].explode().value_counts().head(15)
    st.sidebar.write(most_common_entities)
else:
    st.sidebar.subheader("Top 15 Most Common Entities")
    # Check if the entities are formatted correctly
    exploded_entities = bert_df['news_entities'].explode()
    
    # Debug: display the first few entities
    st.write("First few exploded entities from Sentence-BERT:", exploded_entities.head(15))
    
    # Count the occurrences of each entity
    most_common_entities = exploded_entities.value_counts().head(15)
    st.sidebar.write(most_common_entities)
