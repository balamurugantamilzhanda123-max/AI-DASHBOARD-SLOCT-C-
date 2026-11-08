"""
AI Prediction and Anomaly Detection Engine
Implements scikit-learn Random Forest Classifier and Isolation Forest Anomaly Detector.
Features real model training on synthetic physical telemetry distributions,
holdout validation, genuine confusion matrix computation, and real-time live inference.
Clearly distinguishes simulated-data model evaluation from real hardware inference.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from typing import Dict, Any, Tuple, List
import random


class SignalAIEngine:
    FEATURE_NAMES = [
        "latency_ms",
        "jitter_ns",
        "snr_db",
        "ber",
        "packet_loss_pct",
        "eye_opening_pct"
    ]

    CLASSES = [
        "NORMAL",
        "BIT_CORRUPTION",
        "TRANSMISSION_DELAY",
        "BURST_ERROR",
        "PACKET_LOSS"
    ]

    def __init__(self):
        self.rf_model: RandomForestClassifier = None
        self.iso_model: IsolationForest = None
        self.evaluation_results: Dict[str, Any] = {}
        self.is_trained: bool = False
        self.dataset_info: Dict[str, Any] = {}

    def generate_benchmark_dataset(self, n_samples_per_class: int = 350) -> Tuple[np.ndarray, np.ndarray]:
        """
        Synthesizes a realistic physical dataset based on digital communications metrics.
        Returns features X and labels y.
        """
        np.random.seed(42)
        X_list = []
        y_list = []

        for label in self.CLASSES:
            if label == "NORMAL":
                latency = np.random.normal(12.0, 3.5, n_samples_per_class)
                jitter = np.random.normal(26.0, 8.0, n_samples_per_class)
                snr = np.random.normal(31.0, 3.5, n_samples_per_class)
                ber = np.random.uniform(1e-6, 4e-5, n_samples_per_class)
                loss = np.random.uniform(0.0, 1.2, n_samples_per_class)
                eye = np.random.normal(93.0, 4.0, n_samples_per_class)

            elif label == "BIT_CORRUPTION":
                latency = np.random.normal(17.0, 5.0, n_samples_per_class)
                jitter = np.random.normal(82.0, 22.0, n_samples_per_class)
                snr = np.random.normal(19.0, 4.5, n_samples_per_class)
                ber = np.random.uniform(9e-4, 5.0e-3, n_samples_per_class)
                loss = np.random.uniform(0.0, 2.5, n_samples_per_class)
                eye = np.random.normal(66.0, 10.0, n_samples_per_class)

            elif label == "TRANSMISSION_DELAY":
                latency = np.random.normal(135.0, 28.0, n_samples_per_class)
                jitter = np.random.normal(175.0, 35.0, n_samples_per_class)
                snr = np.random.normal(23.0, 4.0, n_samples_per_class)
                ber = np.random.uniform(1e-5, 9e-5, n_samples_per_class)
                loss = np.random.uniform(0.0, 1.5, n_samples_per_class)
                eye = np.random.normal(81.0, 6.0, n_samples_per_class)

            elif label == "BURST_ERROR":
                latency = np.random.normal(52.0, 16.0, n_samples_per_class)
                jitter = np.random.normal(155.0, 38.0, n_samples_per_class)
                snr = np.random.normal(13.0, 4.0, n_samples_per_class)
                ber = np.random.uniform(5.0e-3, 2.8e-2, n_samples_per_class)
                loss = np.random.uniform(3.5, 14.0, n_samples_per_class)
                eye = np.random.normal(44.0, 12.0, n_samples_per_class)

            elif label == "PACKET_LOSS":
                latency = np.random.normal(38.0, 12.0, n_samples_per_class)
                jitter = np.random.normal(310.0, 55.0, n_samples_per_class)
                snr = np.random.normal(6.5, 3.0, n_samples_per_class)
                ber = np.random.uniform(6e-4, 3.5e-3, n_samples_per_class)
                loss = np.random.uniform(18.0, 45.0, n_samples_per_class)
                eye = np.random.normal(14.0, 8.0, n_samples_per_class)

            # Clamp boundaries
            latency = np.clip(latency, 1.0, 500.0)
            jitter = np.clip(jitter, 0.0, 1000.0)
            snr = np.clip(snr, 0.0, 50.0)
            ber = np.clip(ber, 0.0, 1.0)
            loss = np.clip(loss, 0.0, 100.0)
            eye = np.clip(eye, 0.0, 100.0)

            samples = np.column_stack([latency, jitter, snr, ber, loss, eye])
            X_list.append(samples)
            y_list.extend([label] * n_samples_per_class)

        X = np.vstack(X_list)
        y = np.array(y_list)
        return X, y

    def train_and_evaluate(self) -> Dict[str, Any]:
        """
        Trains Random Forest and Isolation Forest on generated benchmark dataset.
        Computes genuine evaluation metrics from the holdout test partition.
        """
        X, y = self.generate_benchmark_dataset(n_samples_per_class=350)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        # 1. Train Random Forest Classifier
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)

        # 2. Evaluate Random Forest on Test Set
        y_pred = self.rf_model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted")
        rec = recall_score(y_test, y_pred, average="weighted")
        f1 = f1_score(y_test, y_pred, average="weighted")
        cm = confusion_matrix(y_test, y_pred, labels=self.CLASSES)
        report = classification_report(y_test, y_pred, target_names=self.CLASSES, output_dict=True)

        # Feature importances
        importances = dict(zip(self.FEATURE_NAMES, self.rf_model.feature_importances_))

        # 3. Train Isolation Forest Anomaly Detector
        self.iso_model = IsolationForest(
            n_estimators=100,
            contamination=0.20,
            random_state=42
        )
        self.iso_model.fit(X_train)

        self.is_trained = True
        self.dataset_info = {
            "total_samples": len(X),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "num_features": len(self.FEATURE_NAMES),
            "classes": self.CLASSES
        }

        self.evaluation_results = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "confusion_matrix": cm.tolist(),
            "classification_report": report,
            "feature_importances": importances,
            "classes": self.CLASSES,
            "trained_timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return self.evaluation_results

    def predict_realtime(self, telemetry: Dict[str, Any], waveform_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs real-time inference on live telemetry and waveform metrics.
        Returns predicted class, probabilities, anomaly score, and severity.
        Guarantees zero fabricated predictions if hardware channel is offline or waiting.
        """
        if not self.is_trained:
            self.train_and_evaluate()

        # Check for uninitialized / offline hardware states
        status = telemetry.get("status", "")
        if status in ["DISCONNECTED", "WAITING FOR HARDWARE DATA"] or telemetry.get("has_hardware_data") is False:
            return {
                "predicted_fault": "NO SIGNAL (OFFLINE / WAITING)",
                "confidence": 0.0,
                "probabilities": {c: 0.0 for c in self.CLASSES},
                "anomaly_score": 0.0,
                "is_anomaly": False,
                "severity": "INFO",
                "model_status": f"STANDBY ({status})",
                "inference_source": "HARDWARE (IDLE / NO DATA)",
                "features_evaluated": {f: 0.0 for f in self.FEATURE_NAMES}
            }

        # Construct input feature vector
        feat_vector = np.array([[
            float(telemetry.get("latency_ms", 12.0)),
            float(waveform_metrics.get("jitter_ns", 25.0)),
            float(waveform_metrics.get("snr_db", 32.0)),
            float(telemetry.get("ber", 1e-5)),
            float(telemetry.get("packet_loss_pct", 0.0)),
            float(waveform_metrics.get("eye_opening_pct", 95.0))
        ]])

        # Random Forest Prediction
        predicted_class = self.rf_model.predict(feat_vector)[0]
        probabilities = self.rf_model.predict_proba(feat_vector)[0]
        prob_dict = {cls_name: round(float(p), 4) for cls_name, p in zip(self.rf_model.classes_, probabilities)}
        confidence = float(prob_dict[predicted_class])

        # Isolation Forest Anomaly Scoring
        iso_score = float(self.iso_model.decision_function(feat_vector)[0])
        is_anomaly = bool(self.iso_model.predict(feat_vector)[0] == -1)

        severities = {
            "NORMAL": "INFO",
            "BIT_CORRUPTION": "WARNING",
            "TRANSMISSION_DELAY": "WARNING",
            "BURST_ERROR": "CRITICAL",
            "PACKET_LOSS": "CRITICAL"
        }
        severity = severities.get(predicted_class, "INFO")

        source_label = "REAL HARDWARE INFERENCE" if "HARDWARE" in telemetry.get("session_id", "") else "SIMULATED TELEMETRY INFERENCE"

        return {
            "predicted_fault": predicted_class,
            "confidence": confidence,
            "probabilities": prob_dict,
            "anomaly_score": round(iso_score, 4),
            "is_anomaly": is_anomaly,
            "severity": severity,
            "model_status": "ONLINE (RANDOM FOREST + ISOLATION FOREST)",
            "inference_source": source_label,
            "features_evaluated": dict(zip(self.FEATURE_NAMES, feat_vector[0].tolist()))
        }


# Global Singleton instance
ai_engine = SignalAIEngine()
ai_engine.train_and_evaluate()
