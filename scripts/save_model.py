import torch
from transformers import BertForSequenceClassification, BertTokenizer

model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Saving the trained model and tokenizer
model.save_pretrained('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/models/bert_spam_model')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
tokenizer.save_pretrained('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/models/bert_spam_model')

print("Model and tokenizer saved successfully.")
