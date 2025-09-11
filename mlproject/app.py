# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, conlist
import joblib
import numpy as np
import logging

logger = logging.getLogger('uvicorn.error')


class IrisFeatures(BaseModel):
    # Ordered features in cm: [sepal_len, sepal_wid, petal_len, petal_wid]
    features: conlist(float, min_length=4, max_length=4) = Field(
        ..., description='Iris measurements: [sepal_len, sepal_wid, petal_len, petal_wid]'
    )


app = FastAPI(title='Iris Model Service', version='1.1.0')


@app.on_event('startup')
def load_model():
    """Load model once when the app starts."""
    try:
        bundle = joblib.load('model.pkl')
        app.state.pipe = bundle['pipeline']
        app.state.target_names = bundle['target_names']
        logger.info('Model loaded with classes: %s', list(app.state.target_names))
    except Exception as e:
        app.state.pipe = None
        app.state.target_names = None
        logger.exception('Failed to load model.pkl: %s', e)

        
@app.get('/healthz')
def healthcheck():
    return {'status': 'ok', 'model_loaded': app.state.pipe is not None}


@app.exception_handler(Exception)
async def unhandled_exceptions(request: Request, exc: Exception):
    logger.exception('Unhandled error: %s', exc)
    return JSONResponse(status_code=500, content={'detail': 'Internal server error'})


@app.post('/predict')
def predict(payload: IrisFeatures):
    """Parse JSON -> run through the *same* preprocessing+model pipeline -> return prediction."""
    if app.state.pipe is None:
        raise HTTPException(status_code=500, detail='Model not loaded. Ensure model.pkl is present.')

    try:
        x = np.array([payload.features], dtype=float)  # type & shape safety
        y_idx = int(app.state.pipe.predict(x)[0])
        proba = getattr(app.state.pipe, 'predict_proba', None)
        resp = {
            'class_index': y_idx,
            'class_label': app.state.target_names[y_idx],
        }
        if callable(proba):
            resp['class_probabilities'] = proba(x)[0].tolist()
        return resp
    except ValueError as ve:
        # e.g., wrong numeric types, NaNs, etc.
        raise HTTPException(status_code=400, detail=f'Invalid input values: {ve}')
    except Exception as e:
        logger.exception('Prediction failed: %s', e)
        raise HTTPException(status_code=500, detail='Prediction failed')
