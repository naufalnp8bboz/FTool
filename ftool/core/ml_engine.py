import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, mean_squared_error, r2_score, mean_absolute_error
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_iris, load_wine, load_diabetes

class MLEngine:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.trained_model: Any = None
        self.scaler: Optional[StandardScaler] = None
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.target_encoder: Optional[LabelEncoder] = None
        self.feature_names: List[str] = []
        self.target_name: str = ""
        self.task_type: str = "classification" # "classification" or "regression"
        self.last_metrics: Dict[str, Any] = {}
        self.classes_: List[str] = []

    def load_sample_dataset(self, name: str) -> pd.DataFrame:
        """Loads a built-in beginner-friendly dataset."""
        if name.lower() == "iris":
            data = load_iris(as_frame=True)
            df = data.frame
            df["target"] = df["target"].map({0: "setosa", 1: "versicolor", 2: "virginica"})
            self.df = df
            self.target_name = "target"
            self.task_type = "classification"
        elif name.lower() == "wine":
            data = load_wine(as_frame=True)
            df = data.frame
            df["target"] = df["target"].map({0: "Class 0", 1: "Class 1", 2: "Class 2"})
            self.df = df
            self.target_name = "target"
            self.task_type = "classification"
        elif name.lower() == "diabetes":
            data = load_diabetes(as_frame=True)
            self.df = data.frame
            self.target_name = "target"
            self.task_type = "regression"
        elif name.lower() == "customer_churn":
            # Synthetic realistic customer dataset
            np.random.seed(42)
            n = 300
            ages = np.random.randint(18, 70, size=n)
            usage_hours = np.random.exponential(scale=15, size=n).round(1)
            support_calls = np.random.poisson(lam=2, size=n)
            monthly_bill = np.random.uniform(20.0, 120.0, size=n).round(2)
            churn_prob = 1 / (1 + np.exp(-(0.03 * ages - 0.05 * usage_hours + 0.5 * support_calls + 0.02 * monthly_bill - 2)))
            churned = (np.random.rand(n) < churn_prob).astype(int)
            self.df = pd.DataFrame({
                "Age": ages,
                "MonthlyUsageHours": usage_hours,
                "SupportCalls": support_calls,
                "MonthlyBillUSD": monthly_bill,
                "Churned": ["Yes" if c == 1 else "No" for c in churned]
            })
            self.target_name = "Churned"
            self.task_type = "classification"
        else:
            raise ValueError(f"Unknown sample dataset: {name}")
        return self.df

    def load_file(self, filepath: str) -> pd.DataFrame:
        """Loads custom CSV or JSON dataset."""
        if filepath.endswith(".csv"):
            self.df = pd.read_csv(filepath)
        elif filepath.endswith(".json"):
            self.df = pd.read_json(filepath)
        elif filepath.endswith((".xlsx", ".xls")):
            self.df = pd.read_excel(filepath)
        else:
            raise ValueError("Unsupported file format. Please upload CSV, JSON, or Excel.")
        return self.df

    def get_auto_eda(self) -> Dict[str, Any]:
        """Generates statistical overview, missing values, datatypes."""
        if self.df is None:
            return {}
        
        info = {
            "rows": int(self.df.shape[0]),
            "columns": int(self.df.shape[1]),
            "column_names": list(self.df.columns),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "missing_values": {col: int(cnt) for col, cnt in self.df.isnull().sum().items()},
            "summary_stats": self.df.describe(include="all").fillna("").to_dict(),
            "preview_head": self.df.head(10).to_dict(orient="records"),
        }

        # Numeric correlation
        numeric_df = self.df.select_dtypes(include=[np.number])
        if not numeric_df.empty and numeric_df.shape[1] > 1:
            info["correlations"] = numeric_df.corr().round(3).to_dict()
        else:
            info["correlations"] = {}

        return info

    def train(
        self,
        target_col: str,
        features: Optional[List[str]] = None,
        model_name: str = "Random Forest",
        task_type: str = "classification",
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """Trains chosen model and returns metrics."""
        if self.df is None:
            raise ValueError("No dataset loaded.")
        
        self.target_name = target_col
        self.task_type = task_type
        
        if features is None or len(features) == 0:
            features = [col for col in self.df.columns if col != target_col]
        self.feature_names = features

        # Preprocessing
        clean_df = self.df[features + [target_col]].dropna().copy()
        if len(clean_df) < 10:
            raise ValueError("Dataset has too few rows after dropping missing values.")

        X = clean_df[features].copy()
        y = clean_df[target_col].copy()

        # Encode categorical features
        self.label_encoders = {}
        for col in X.select_dtypes(include=["object", "category"]).columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.label_encoders[col] = le

        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Encode target if classification
        self.target_encoder = None
        if self.task_type == "classification":
            if y.dtype == "object" or isinstance(y.iloc[0], str) or len(np.unique(y)) > 2:
                self.target_encoder = LabelEncoder()
                y = self.target_encoder.fit_transform(y)
                self.classes_ = [str(c) for c in self.target_encoder.classes_]
            else:
                self.classes_ = [str(c) for c in np.unique(y)]

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=random_state
        )

        # Select model algorithm
        if self.task_type == "classification":
            if model_name == "Random Forest":
                model = RandomForestClassifier(n_estimators=100, random_state=random_state)
            elif model_name == "Logistic Regression":
                model = LogisticRegression(max_iter=500, random_state=random_state)
            elif model_name == "SVM":
                model = SVC(probability=True, random_state=random_state)
            elif model_name == "KNN":
                model = KNeighborsClassifier(n_neighbors=5)
            elif model_name == "Gradient Boosting":
                model = GradientBoostingClassifier(random_state=random_state)
            else:
                model = RandomForestClassifier(random_state=random_state)
        else: # Regression
            if model_name == "Random Forest":
                model = RandomForestRegressor(n_estimators=100, random_state=random_state)
            elif model_name == "Linear Regression":
                model = LinearRegression()
            elif model_name == "SVR":
                model = SVR()
            elif model_name == "Gradient Boosting":
                model = GradientBoostingRegressor(random_state=random_state)
            else:
                model = RandomForestRegressor(random_state=random_state)

        model.fit(X_train, y_train)
        self.trained_model = model

        # Evaluation
        y_pred = model.predict(X_test)

        if self.task_type == "classification":
            acc = float(accuracy_score(y_test, y_pred))
            prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
            rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
            f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
            cm = confusion_matrix(y_test, y_pred).tolist()

            feature_importances = {}
            if hasattr(model, "feature_importances_"):
                for name, imp in zip(features, model.feature_importances_):
                    feature_importances[name] = round(float(imp), 4)

            self.last_metrics = {
                "task": "classification",
                "model": model_name,
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "confusion_matrix": cm,
                "classes": self.classes_,
                "feature_importances": feature_importances,
            }
        else:
            r2 = float(r2_score(y_test, y_pred))
            mse = float(mean_squared_error(y_test, y_pred))
            mae = float(mean_absolute_error(y_test, y_pred))

            feature_importances = {}
            if hasattr(model, "feature_importances_"):
                for name, imp in zip(features, model.feature_importances_):
                    feature_importances[name] = round(float(imp), 4)

            self.last_metrics = {
                "task": "regression",
                "model": model_name,
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "r2_score": round(r2, 4),
                "mse": round(mse, 4),
                "mae": round(mae, 4),
                "feature_importances": feature_importances,
            }

        return self.last_metrics

    def predict_single(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Runs single-instance inference."""
        if self.trained_model is None or self.scaler is None:
            raise ValueError("No trained model available.")

        # Create row
        row = pd.DataFrame([input_dict])
        for col in self.feature_names:
            if col not in row.columns:
                row[col] = 0

        row = row[self.feature_names].copy()

        # Apply encoders
        for col, le in self.label_encoders.items():
            if col in row:
                val = str(row[col].iloc[0])
                if val in le.classes_:
                    row[col] = le.transform([val])[0]
                else:
                    row[col] = 0

        X_scaled = self.scaler.transform(row)
        pred = self.trained_model.predict(X_scaled)[0]

        res = {}
        if self.task_type == "classification":
            if self.target_encoder:
                label = self.target_encoder.inverse_transform([int(pred)])[0]
            else:
                label = str(pred)
            res["prediction"] = label
            if hasattr(self.trained_model, "predict_proba"):
                probs = self.trained_model.predict_proba(X_scaled)[0]
                res["probabilities"] = {self.classes_[i]: round(float(probs[i]), 4) for i in range(len(self.classes_))}
        else:
            res["prediction"] = round(float(pred), 4)

        return res

    def export_model(self, filepath: str):
        """Saves model bundle (.joblib)."""
        bundle = {
            "model": self.trained_model,
            "scaler": self.scaler,
            "label_encoders": self.label_encoders,
            "target_encoder": self.target_encoder,
            "feature_names": self.feature_names,
            "target_name": self.target_name,
            "task_type": self.task_type,
            "classes": self.classes_,
        }
        joblib.dump(bundle, filepath)

    def generate_python_code(self) -> str:
        """Generates ready-to-run Python code for beginners."""
        features_repr = json.dumps(self.feature_names, indent=4)
        return f'''# Auto-generated by FTool Machine Learning Studio
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import {self.trained_model.__class__.__name__}

# 1. Load your dataset
df = pd.read_csv("your_data.csv")

# 2. Select Features and Target
features = {features_repr}
target = "{self.target_name}"

X = df[features]
y = df[target]

# 3. Train / Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. Initialize and Train Model
model = {self.trained_model.__class__.__name__}()
model.fit(X_train_scaled, y_train)

# 6. Predict and Evaluate
score = model.score(X_test_scaled, y_test)
print(f"Model Score: {{score:.4f}}")
'''
