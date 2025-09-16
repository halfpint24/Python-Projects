# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, conlist, field_validator
import joblib
import numpy as np
import logging

logger = logging.getLogger('uvicorn.error')


class IrisFeatures(BaseModel):
    # Ordered features in cm: [sepal_len, sepal_wid, petal_len, petal_wid]
    features: conlist(float, min_length=4, max_length=4) = Field(
        ..., description='Iris measurements: [sepal_len, sepal_wid, petal_len, petal_wid]'
    )

    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        # Ensure finite numbers and reasonable biological range (>=0, <= 10 cm)
        if len(v) != 4:
            raise ValueError('features must have length 4')
        for val in v:
            if val is None:
                raise ValueError('features cannot contain nulls')
            if not (float('-inf') < float(val) < float('inf')):
                raise ValueError('features must be finite numbers')
            if float(val) < 0 or float(val) > 10:
                # boundary-case friendly: allow 0..10cm
                raise ValueError('each feature must be between 0 and 10 centimeters')
        return v



app = FastAPI(title='Iris Model Service', version='1.2.0')

# Allow simple cross-origin usage from local tools and browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)



@app.on_event('startup')
def load_model():
    '''Load model once when the app starts.'''
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
    '''Parse JSON -> run through the *same* preprocessing+model pipeline -> return prediction.'''
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
