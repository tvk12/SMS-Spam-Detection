from transformers import BertForSequenceClassification, BertTokenizer
import torch

# Loading the saved model and tokenizer from the previous code
model = BertForSequenceClassification.from_pretrained('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/models/bert_spam_model_weighted')
tokenizer = BertTokenizer.from_pretrained('/Users/vinaykumar/Desktop/My Projects/SMS spam detection/models/bert_spam_model')

# Here we write the sample SMS for prediction
sample_sms = "Hi, Vinay how are you?"

# Preprocess the SMS for BERT
inputs = tokenizer.encode_plus(
    sample_sms,
    add_special_tokens=True,
    max_length=128,
    pad_to_max_length=True,
    return_attention_mask=True,
    truncation=True,
    return_tensors="pt"
)

# If the GPU is available in the system thenuse that 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
inputs = {key: val.to(device) for key, val in inputs.items()}

# predicting
model.eval()
with torch.no_grad():
    outputs = model(**inputs)

logits = outputs.logits # gets you the pred
prediction = torch.argmax(logits, dim=1).item()

if prediction == 1:
    print("Prediction: Spam")
else:
    print("Prediction: Ham")
