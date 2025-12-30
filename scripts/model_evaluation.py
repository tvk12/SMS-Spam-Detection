from transformers import BertForSequenceClassification, BertTokenizer
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np

# Loading the test data
test_data = pd.read_csv('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/data/processed/test_data.csv')

# Prepareing the test inputs
X_test = np.array([eval(i) for i in test_data['tokenized'].values])
attention_masks_test = np.array([eval(i) for i in test_data['attention_mask'].values])
y_test = test_data['label'].values

# Converting to the tensors
test_inputs = torch.tensor(X_test)
test_labels = torch.tensor(y_test)
test_masks = torch.tensor(attention_masks_test)

# Creating the test dataloader
batch_size = 16
test_data = TensorDataset(test_inputs, test_masks, test_labels)
test_dataloader = DataLoader(test_data, shuffle=False, batch_size=batch_size)

# Loading the new model and the tokenizer from bert_spam_model_weighted
model = BertForSequenceClassification.from_pretrained('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/models/bert_spam_model_weighted')
tokenizer = BertTokenizer.from_pretrained('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/models/bert_spam_model_weighted')

# Seting the device as (GPU/CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Evaluation
model.eval()
predictions, true_labels = [], []

for batch in test_dataloader:
    batch = tuple(t.to(device) for t in batch)
    inputs, masks, labels = batch
    
    with torch.no_grad():
        outputs = model(inputs, token_type_ids=None, attention_mask=masks)
    
    logits = outputs.logits
    logits = logits.detach().cpu().numpy()
    label_ids = labels.to('cpu').numpy()
    
    predictions.append(np.argmax(logits, axis=1))
    true_labels.append(label_ids)

# Flattening the predictions and the true labels
predictions = np.concatenate(predictions, axis=0)
true_labels = np.concatenate(true_labels, axis=0)

# Generating the classification report
report = classification_report(true_labels, predictions, target_names=['Ham', 'Spam'])
print(report)
