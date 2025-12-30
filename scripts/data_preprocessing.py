import pandas as pd
import re
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer

data_path = '/Users/vinaykumar/Desktop/My Projects/SMS spam detection/data/raw/spam.csv'  
df = pd.read_csv(data_path, encoding='latin-1')

# Renaming the columns and selecting relevant ones
df.columns = ['label', 'message', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4']
df = df[['label', 'message']]

# Mapping 'ham' to 0 and 'spam' to 1
df['label'] = df['label'].map({'ham': 0, 'spam': 1})

# Text cleaning function
def clean_text(text):
    text = re.sub(r'\W', ' ', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = text.lower()  # Convert text to lowercase
    return text

# Applying the cleaning function to all messages
df['message'] = df['message'].apply(clean_text)

# Initializing the BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Tokenizing the messages
def tokenize_text(text):
    return tokenizer.encode_plus(
        text,
        add_special_tokens=True,  # Add [CLS] and [SEP]
        max_length=128,           # Max length based on dataset analysis
        pad_to_max_length=True,   # Pad to max length
        return_attention_mask=True,
        truncation=True           # Truncate to max length
    )

# Tokenizing the dataset
df['tokenized'] = df['message'].apply(lambda x: tokenize_text(x)['input_ids'])
df['attention_mask'] = df['message'].apply(lambda x: tokenize_text(x)['attention_mask'])

# Splitting the data into training and test sets
X = df[['tokenized', 'attention_mask']]
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Saving processed data
train_data = pd.concat([X_train, y_train], axis=1)
test_data = pd.concat([X_test, y_test], axis=1)

train_data.to_csv('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/data/processed/train_data.csv', index=False)
test_data.to_csv('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/data/processed/test_data.csv', index=False)

print("Data preprocessing complete. Processed data saved to the 'processed' folder.")
