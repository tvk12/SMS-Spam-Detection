import torch
from transformers import BertForSequenceClassification, BertTokenizer
import os

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "bert_spam_model_weighted")

def load_model():
    """Loads the model and tokenizer."""
    print(f"Loading model from {MODEL_PATH}...")
    try:
        model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
        tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
        
        # Move to device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        
        print("Model loaded successfully.")
        return model, tokenizer, device
    except Exception as e:
        print(f"Error loading model: {e}")
        raise e

def predict_sms(model, tokenizer, device, sms_text):
    """Predicts if an SMS is Spam or Ham."""
    inputs = tokenizer.encode_plus(
        sms_text,
        add_special_tokens=True,
        max_length=128,
        pad_to_max_length=True,
        return_attention_mask=True,
        truncation=True,
        return_tensors="pt"
    )
    
    # Move inputs to device
    inputs = {key: val.to(device) for key, val in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()
    
    return "Spam" if prediction == 1 else "Ham"
