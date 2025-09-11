import joblib
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def train_and_save(path: str = 'model.pkl'):
    X, y = load_iris(return_X_y=True, as_frame=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = Pipeline(steps=[
        ('scale', StandardScaler()),
        ('clf', RandomForestClassifier(n_estimators=200, random_state=42))
    ])
    pipe.fit(X_train, y_train)

    acc = accuracy_score(y_test, pipe.predict(X_test))
    print(f'Test accuracy: {acc:.3f}')

    joblib.dump({
        'pipeline': pipe,
        'target_names': load_iris().target_names,
        'feature_names': load_iris().feature_names,
    }, path)
    print(f'Saved model pipeline to {path}')

    
if __name__ == '__main__':
    train_and_save()
