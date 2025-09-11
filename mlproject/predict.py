import joblib
import numpy as np


def predict_one(sample, model_path='model.pkl'):
    bundle = joblib.load(model_path)
    pipe = bundle['pipeline']
    target_names = bundle['target_names']
    y_pred = pipe.predict(np.array([sample]))[0]
    proba = getattr(pipe, 'predict_proba', lambda X: None)(np.array([sample]))
    out = {
        'class_index': int(y_pred),
        'class_label': target_names[y_pred],
    }
    if proba is not None:
        out['class_probabilities'] = proba[0].tolist()
    return out


if __name__ == '__main__':
    example = [5.1, 3.5, 1.4, 0.2]
    print(predict_one(example))
