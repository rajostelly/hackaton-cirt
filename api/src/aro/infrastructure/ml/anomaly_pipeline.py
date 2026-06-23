from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # backend non interactif (serveur sans écran)

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import IsolationForest  # noqa: E402
from sklearn.metrics import confusion_matrix  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

FEATURES = ["packets", "distinct_dst_ports", "distinct_dst_ips", "bytes", "syn_count"]
# Seuil heuristique (ports distincts) servant de vérité-terrain pour la matrice
# de confusion : au-delà, le flux est un scan connu.
PORT_SCAN_LABEL_THRESHOLD = 20


def _severity(distinct_ports: int) -> str:
    if distinct_ports >= 100:
        return "critical"
    if distinct_ports >= 20:
        return "high"
    if distinct_ports >= 5:
        return "medium"
    return "low"


class AnomalyPipeline:
    """Pipeline d'anomalies réseau : pandas → numpy → sklearn (Isolation Forest)."""

    def __init__(self, contamination: float = 0.1, random_state: int = 42) -> None:
        self.contamination = contamination
        self.random_state = random_state

    # 1. collecte (pandas)
    def build_dataframe(self, flows: list[dict]) -> pd.DataFrame:
        return pd.DataFrame(flows)

    # 2. nettoyage (suppression des doublons)
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates().reset_index(drop=True)

    # 3. transformation (normalisation/standardisation + valeurs nulles)
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        numeric = df.reindex(columns=FEATURES).apply(pd.to_numeric, errors="coerce").fillna(0.0)
        return StandardScaler().fit_transform(numeric.to_numpy(dtype=float))

    def run(self, flows: list[dict], plot_path: str) -> dict[str, Any]:
        df = self.clean(self.build_dataframe(flows))
        if len(df) < 2:
            return {"trained": False, "samples": int(len(df)), "anomalies": []}

        features = self.transform(df)
        # 4. entraînement (Isolation Forest)
        model = IsolationForest(contamination=self.contamination, random_state=self.random_state)
        predictions = model.fit_predict(features)  # -1 = anomalie, 1 = normal
        scores = model.score_samples(features)

        # 5. évaluation (matrice de confusion vs vérité-terrain heuristique)
        ports = df["distinct_dst_ports"].astype(float).to_numpy()
        labels = np.where(ports >= PORT_SCAN_LABEL_THRESHOLD, -1, 1)
        matrix = confusion_matrix(labels, predictions, labels=[1, -1])
        tn, fp = int(matrix[0, 0]), int(matrix[0, 1])
        fn, tp = int(matrix[1, 0]), int(matrix[1, 1])
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        accuracy = (tp + tn) / len(df) if len(df) else 0.0

        self._plot(scores, predictions, plot_path)

        # 6. résultats : anomalies classées par sévérité + détection de nouveaux types
        anomalies: list[dict[str, Any]] = []
        for i, pred in enumerate(predictions):
            if pred != -1:
                continue
            distinct_ports = int(ports[i])
            is_scan = distinct_ports >= PORT_SCAN_LABEL_THRESHOLD
            anomalies.append(
                {
                    "source_ip": str(df.iloc[i].get("source_ip", "?")),
                    "distinct_dst_ports": distinct_ports,
                    "packets": int(float(df.iloc[i].get("packets", 0))),
                    "score": round(float(scores[i]), 4),
                    "severity": _severity(distinct_ports),
                    "is_novel": not is_scan,  # anomalie hors-pattern scan = type inédit
                }
            )
        anomalies.sort(key=lambda a: float(a["score"]))

        return {
            "trained": True,
            "samples": int(len(df)),
            "anomalies_count": len(anomalies),
            "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
            "metrics": {
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "accuracy": round(accuracy, 3),
            },
            "anomalies": anomalies,
        }

    def _plot(self, scores: np.ndarray, predictions: np.ndarray, plot_path: str) -> None:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(scores[predictions == 1], bins=20, alpha=0.75, label="Normal", color="#ffbd59")
        ax.hist(scores[predictions == -1], bins=20, alpha=0.85, label="Anomalie", color="#e85c30")
        ax.set_title("Distribution des scores d'anomalie (Isolation Forest)")
        ax.set_xlabel("Score (plus bas = plus anormal)")
        ax.set_ylabel("Nombre de flux")
        ax.legend()
        fig.tight_layout()
        Path(plot_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(plot_path, dpi=100)
        plt.close(fig)
