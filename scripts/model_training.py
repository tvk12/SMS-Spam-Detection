import torch
from transformers import BertForSequenceClassification, AdamW, BertTokenizer
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import pandas as pd
import numpy as np

# Loading the dataset taken from the kaggle
data_path = '/Users/vinaykumar/Desktop/My Projects/SMS spam detection/data/processed/train_data.csv'
df = pd.read_csv(data_path)

# Preparig all the inputs and labels from the above dataset 
X_train = np.array([eval(i) for i in df['tokenized'].values])
attention_masks_train = np.array([eval(i) for i in df['attention_mask'].values])
y_train = df['label'].values

# Converting the data to tensors
train_inputs = torch.tensor(X_train)
train_labels = torch.tensor(y_train)
train_masks = torch.tensor(attention_masks_train)

# Creating a dataloader
batch_size = 16
train_data = TensorDataset(train_inputs, train_masks, train_labels)
train_dataloader = DataLoader(train_data, shuffle=True, batch_size=batch_size)

# Calculating the class weights based on the label distribution
class_weights = compute_class_weight('balanced', classes=[0, 1], y=y_train)
class_weights = torch.tensor(class_weights, dtype=torch.float)

# Initializing the model and the ptimizer
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
optimizer = AdamW(model.parameters(), lr=2e-5)

# Cchoosing the device (GPU/CPU) we want to work on
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Loss function along with the class weights
loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights.to(device))

# Training loop
epochs = 3
for epoch in range(epochs):
    model.train()
    total_loss = 0
    
    for step, batch in enumerate(train_dataloader):
        batch_input_ids = batch[0].to(device)
        batch_input_mask = batch[1].to(device)
        batch_labels = batch[2].to(device)
        
        model.zero_grad()
        
        outputs = model(batch_input_ids, token_type_ids=None, attention_mask=batch_input_mask)
        logits = outputs.logits
        loss = loss_fn(logits, batch_labels)
        total_loss += loss.item()
        
        loss.backward()
        optimizer.step()
    
    print(f'Epoch {epoch + 1} Loss: {total_loss / len(train_dataloader)}')

# Saving the model and tokenizer
model.save_pretrained('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/models/bert_spam_model_weighted')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
tokenizer.save_pretrained('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/models/bert_spam_model_weighted')

print("Model and tokenizer saved successfully.")
