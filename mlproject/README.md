# 🌸 Iris Classifier API

A minimal **ML deployment application** that trains a Random Forest classifier on the Iris dataset and serves predictions through a **FastAPI** web service.

---

## 📂 Project Structure
```
.
├── app.py            # FastAPI app with /predict endpoint
├── train_model.py    # Script to train & save model.pkl
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container build config
└── README.md         # (this file)
```

---

## 🚀 Run with Docker

### 1. Build the image
```bash
sudo docker build -t iris-api .
```

### 2. Train the model (inside the container)
This ensures the `model.pkl` is created with the **same scikit-learn version** as the runtime, avoiding version mismatch errors.

```bash
sudo docker run --rm -v "$PWD":/app iris-api python train_model.py
```

You should now see a `model.pkl` file in your project folder.

### 3. Run the API
Mount the trained model into the container and expose port 8000:

```bash
sudo docker run --rm -p 8000:8000 -v "$PWD/model.pkl":/app/model.pkl iris-api
```

### 4. Test the API

You can access the web API by going to ```http://127.0.0.1:8000/docs``` in your browser.

**Health check**
```bash
curl http://127.0.0.1:8000/healthz
# -> {"status":"ok","model_loaded":true}
```

**Prediction**
```bash
curl -X POST http://127.0.0.1:8000/predict   -H "Content-Type: application/json"   -d '{"features":[5.1,3.5,1.4,0.2]}'
```

Expected response:
```json
{
  "class_index": 0,
  "class_label": "setosa",
  "class_probabilities": [1.0, 0.0, 0.0]
}
```

---

## 🛠️ Potential issues

- **Model not loaded error** → Make sure you ran step 2 to generate `model.pkl` before running the API.
- **Version mismatch / monotonic_cst error** → Always retrain `model.pkl` inside the container so versions match.
- **Permission denied when writing model.pkl** → Ensure your project folder allows writes from Docker, or run with `sudo`.

---
