import pandas as pd
from tqdm import tqdm

# Enable progress_apply for pandas using tqdm
tqdm.pandas()

# ----- Step 1: Load the Mapping File -----
# Update the file path to use the wikileaks file, since it has the correct columns.
mapping_file = r"data\processed_wikileaks_parsed_with_category.xlsx"
df_mapping = pd.read_excel(mapping_file)

# Print column names for verification (optional)
print("Mapping file columns:", df_mapping.columns.tolist())

# Check that the necessary columns exist
if 'Text' not in df_mapping.columns or 'key' not in df_mapping.columns:
    raise ValueError("The mapping file must contain 'Text' and 'key' columns.")

# Create a mapping from the 'Text' column to the 'key'
text_to_key = dict(zip(df_mapping['Text'], df_mapping['key']))

# ----- Step 2: Load the SentenceBERT Results File -----
sentencebert_file = r"data\sentencebert_results.xlsx"
df_sentencebert = pd.read_excel(sentencebert_file)

# Verify that the required column exists
if 'wikileaks_Text' not in df_sentencebert.columns:
    raise ValueError("The sentencebert results file must contain the 'wikileaks_Text' column.")

# ----- Step 3: Replace Matching Text with Corresponding Key -----
def substitute_with_key(cell_value):
    # Return the corresponding key if the cell value matches; otherwise, return the original value.
    return text_to_key.get(cell_value, cell_value)

# Apply the substitution with a progress bar
df_sentencebert['wikileaks_Text'] = df_sentencebert['wikileaks_Text'].progress_apply(substitute_with_key)

# ----- Step 4: Save the Updated DataFrame -----
df_sentencebert.to_excel(sentencebert_file, index=False)

print("Substitution completed successfully!")
