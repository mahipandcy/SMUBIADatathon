import pandas as pd
import ast
import re
import pycountry

# Extended threat keywords for different levels.
HIGH_THREAT_KEYWORDS = [
    "terrorism", "cyberattack", "nuclear", "espionage", "assassination",
    "bombing", "massacre", "extremism", "radicalism", "hostage"
]
MEDIUM_THREAT_KEYWORDS = [
    "hacking", "surveillance", "fraud", "extortion", "incursion",
    "unrest", "riot", "protest", "sabotage", "infiltration"
]
LOW_THREAT_KEYWORDS = [
    "scam", "phishing", "misinformation", "fake news", "deception",
    "hoax", "rumor", "manipulation", "propaganda", "misreporting"
]

# Compile regex patterns for each threat level. The patterns use word boundaries
# to ensure we match whole words (case insensitive).
def compile_patterns(keywords):
    return [re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE) for keyword in keywords]

high_patterns = compile_patterns(HIGH_THREAT_KEYWORDS)
medium_patterns = compile_patterns(MEDIUM_THREAT_KEYWORDS)
low_patterns = compile_patterns(LOW_THREAT_KEYWORDS)

def determine_threat_level(text):
    """
    Scans the text using extended keywords and returns the threat level (High, Medium, Low)
    as soon as a match is found. If no threat keywords are found, returns None.
    """
    # Check high threat keywords first.
    for pattern in high_patterns:
        if pattern.search(text):
            return "High"
    for pattern in medium_patterns:
        if pattern.search(text):
            return "Medium"
    for pattern in low_patterns:
        if pattern.search(text):
            return "Low"
    return None

def is_country(name):
    """Return True if the given name is recognized as a country using pycountry."""
    try:
        pycountry.countries.lookup(name)
        return True
    except LookupError:
        return False

# Load the Excel file.
df = pd.read_excel("data/processed_news_excerpts_parsed_with_category.xlsx")

# Initialize a dictionary to store threat counts by country.
country_threat_counts = {}

# Loop over each row in the DataFrame.
for idx, row in df.iterrows():
    text = row["Text"]
    threat_level = determine_threat_level(text)
    
    # Only proceed if a threat keyword was detected.
    if threat_level is not None:
        # Get the 'entities' column; if it's a string, convert it to a Python list.
        entities = row.get("entities", [])
        if isinstance(entities, str):
            try:
                entities = ast.literal_eval(entities)
            except Exception as e:
                print(f"Error parsing entities on row {idx}: {e}")
                continue
        
        # Look for any entity with a GPE tag and check if it's a valid country.
        for entity in entities:
            # Each entity is expected to be a tuple: (name, entity_type)
            if isinstance(entity, (list, tuple)) and len(entity) >= 2 and entity[1] == "GPE":
                entity_name = entity[0]
                if is_country(entity_name):
                    if entity_name not in country_threat_counts:
                        country_threat_counts[entity_name] = {"High": 0, "Medium": 0, "Low": 0}
                    country_threat_counts[entity_name][threat_level] += 1

# Print out the results.
print("Threat counts by country:")
for country, counts in country_threat_counts.items():
    print(f"\nCountry: {country}")
    for level in ["High", "Medium", "Low"]:
        print(f"  {level} Threats: {counts[level]}")
