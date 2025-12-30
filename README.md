# SMS Spam Detection System

A modern, full-stack SMS Spam Detection system leveraging **BERT (Bidirectional Encoder Representations from Transformers)** for high-accuracy classification and a **FastAPI** backend for real-time predictions.

## 🚀 Features

- **BERT-Powered Classification**: Uses a fine-tuned BERT model (`bert-base-uncased`) for superior text understanding.
- **FastAPI Backend**: High-performance asynchronous API for processing requests.
- **Interactive UI**: Clean, responsive frontend built with vanilla HTML, CSS, and JavaScript.
- **Real-time Stats**: Dashboard to track prediction history and accuracy.
- **Feedback Loop**: Users can provide feedback on predictions to improve future model iterations.
- **API Security**: Protected endpoints using API key authentication.

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: FastAPI, Pydantic, SQLAlchemy
- **ML/NLP**: PyTorch, Hugging Face Transformers, Scikit-learn, Pandas, NumPy
- **Database**: SQLite (for logging and stats)

## 📁 Project Structure

```text
.
├── app/                    # FastAPI application
│   ├── static/             # Frontend files (HTML, CSS, JS)
│   ├── database.py         # Database models and operations
│   ├── main.py             # API routes and assembly
│   ├── model_loader.py     # BERT model loading and inference
│   └── test_api.py         # API testing suite
├── models/                 # Model storage
│   └── bert_spam_model_weighted/ # Fine-tuned BERT model weights
├── scripts/                # Utility scripts
│   ├── data_preprocessing.py # Data cleaning and tokenization
│   ├── model_training.py     # BERT training loop with class weights
│   ├── model_evaluation.py   # Performance metrics calculation
│   └── testing.py            # Local inference testing
├── data/                   # Dataset storage
├── notebooks/              # Research and experimentation
└── README.md
```

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tvk12/SMS-Spam-Detection.git
   cd SMS-Spam-Detection
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you have PyTorch and Transformers installed)*

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```
   Open `http://localhost:8000` in your browser.

## 🧠 Model Details

The system uses `bert-base-uncased` fine-tuned on an SMS Spam collection dataset. We implemented **class weighting** during training to handle the imbalance between 'Ham' and 'Spam' messages, ensuring the model remains sensitive to spam detection without sacrificing accuracy on legitimate messages.

## 📊 Evaluation

The model is evaluated using:
- **Accuracy**
- **Precision, Recall, and F1-Score** (Crucial for imbalanced data)
- **Confusion Matrix**

## 🛡️ License

This project is licensed under the MIT License - see the LICENSE file for details.
