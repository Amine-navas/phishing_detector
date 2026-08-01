"""
Phishing Email Detector - Couche Python (orchestration)
=========================================================
Python ne réimplémente PAS l'algorithme de classification : il charge
la bibliothèque compilée build/libphishing.so (module C++ naive_bayes.cpp,
lui-même construit sur le module C textutils.c) via ctypes, et se charge de :

  - lire/préparer les données (pandas)
  - découper train/test (scikit-learn)
  - piloter l'entraînement et les prédictions via l'API C (ctypes)
  - calculer les métriques d'évaluation (scikit-learn.metrics)
  - offrir une interface en ligne de commande

Le calcul lourd (tokenisation, comptage de mots, log-probabilités) tourne
entièrement en code natif (C/C++) ; Python est la couche "data science / UX".

Usage:
    python3 phishing_detector.py
    python3 phishing_detector.py --predict "Click here to verify your account now!"
"""

import argparse
import ctypes
import math
import os

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

HERE = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(HERE, "..", "build", "libphishing.so")
DATA_PATH = os.path.join(HERE, "..", "data", "emails.csv")
ALTERNATE_DATA_PATHS = [
    DATA_PATH,
    os.path.join(HERE, "data", "emails.csv"),
    os.path.join(HERE, "..", "..", "email_phishing", "data", "emails.csv"),
    os.path.join(HERE, "..", "..", "email_phishing.worktrees", "fix-the-code", "data", "emails.csv"),
]


def _resolve_data_path(path: str | None = None) -> str:
    if path:
        return path
    for candidate in ALTERNATE_DATA_PATHS:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "Dataset not found. Searched for emails.csv in the following locations:\n"
        + "\n".join(ALTERNATE_DATA_PATHS)
        + "\nPlace emails.csv in a data/ folder or pass its path with load_data(path=...)."
    )


class PhishingEngine:
    """Wrapper Python autour du moteur natif C++/C (libphishing.so).

    Expose une interface façon scikit-learn (fit / predict) mais délègue
    tout le calcul à la bibliothèque compilée.
    """

    def __init__(self, lib_path: str = LIB_PATH):
        if not os.path.exists(lib_path):
            raise FileNotFoundError(
                f"Bibliothèque introuvable : {lib_path}\n"
                f"Compile-la d'abord avec : ./build.sh"
            )
        self.lib = ctypes.CDLL(lib_path)
        self._configure_signatures()
        self._model = self.lib.nb_create()

    def _configure_signatures(self):
        self.lib.nb_create.restype = ctypes.c_void_p

        self.lib.nb_free.argtypes = [ctypes.c_void_p]

        self.lib.nb_add_example.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]

        self.lib.nb_finalize.argtypes = [ctypes.c_void_p]

        self.lib.nb_predict.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
        ]
        self.lib.nb_predict.restype = ctypes.c_int

        self.lib.nb_vocab_size.argtypes = [ctypes.c_void_p]
        self.lib.nb_vocab_size.restype = ctypes.c_int

    def fit(self, texts, labels):
        """Envoie chaque exemple au moteur natif (nb_add_example),
        puis demande le calcul des probabilités a priori (nb_finalize)."""
        for text, label in zip(texts, labels):
            self.lib.nb_add_example(self._model, text.encode("utf-8"), int(label))
        self.lib.nb_finalize(self._model)

    def predict(self, text: str):
        """Retourne (label_prédit, confiance) pour un email."""
        score_phishing = ctypes.c_double()
        score_legit = ctypes.c_double()
        label = self.lib.nb_predict(
            self._model, text.encode("utf-8"),
            ctypes.byref(score_phishing), ctypes.byref(score_legit)
        )
        confidence = self._softmax_confidence(score_phishing.value, score_legit.value, label)
        return label, confidence

    def predict_batch(self, texts):
        return [self.predict(t)[0] for t in texts]

    def vocab_size(self) -> int:
        return self.lib.nb_vocab_size(self._model)

    @staticmethod
    def _softmax_confidence(score_phishing, score_legit, predicted_label):
        # Convertit les deux log-scores natifs en une probabilité (stable numériquement)
        m = max(score_phishing, score_legit)
        p_phishing = math.exp(score_phishing - m)
        p_legit = math.exp(score_legit - m)
        total = p_phishing + p_legit
        return (p_phishing if predicted_label == 1 else p_legit) / total

    def __del__(self):
        if hasattr(self, "lib") and hasattr(self, "_model") and self._model:
            self.lib.nb_free(self._model)


def load_data(path: str | None = None) -> pd.DataFrame:
    resolved_path = _resolve_data_path(path)
    df = pd.read_csv(resolved_path, sep="|")
    return df.dropna()


def evaluate(engine: PhishingEngine, texts, labels, title="Évaluation"):
    y_pred = engine.predict_batch(texts)

    acc = accuracy_score(labels, y_pred)
    prec = precision_score(labels, y_pred, zero_division=0)
    rec = recall_score(labels, y_pred, zero_division=0)
    f1 = f1_score(labels, y_pred, zero_division=0)
    cm = confusion_matrix(labels, y_pred)

    print(f"\n{'='*60}")
    print(f" {title}  (moteur natif C++/C, {engine.vocab_size()} mots en vocabulaire)")
    print(f"{'='*60}")
    print(f"Accuracy  : {acc:.3f}")
    print(f"Precision : {prec:.3f}")
    print(f"Recall    : {rec:.3f}")
    print(f"F1-score  : {f1:.3f}")
    print("\nMatrice de confusion :")
    print("                 Prédit légitime   Prédit phishing")
    print(f"Réel légitime          {cm[0][0]:<15} {cm[0][1]}")
    print(f"Réel phishing          {cm[1][0]:<15} {cm[1][1]}")
    print("\nRapport détaillé :")
    print(classification_report(labels, y_pred, target_names=["légitime", "phishing"], zero_division=0))


def main():
    parser = argparse.ArgumentParser(description="Détecteur de phishing (Python + moteur natif C++/C)")
    parser.add_argument("--predict", type=str, help="Texte d'un email à classifier")
    parser.add_argument("--data", type=str, default=DATA_PATH, help="Chemin vers le dataset (label|text)")
    args = parser.parse_args()

    print(f"Bibliothèque native chargée depuis : {os.path.relpath(LIB_PATH)}")
    print("Chargement du dataset...")
    df = load_data(args.data)
    print(f"{len(df)} emails chargés ({df['label'].sum()} phishing, {(df['label']==0).sum()} légitimes)")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
    )

    engine = PhishingEngine()
    print("\nEntraînement (délégué au moteur C++/C via ctypes)...")
    engine.fit(X_train.tolist(), y_train.tolist())

    evaluate(engine, X_test.tolist(), y_test.tolist(), title="Résultats sur le jeu de test")

    if args.predict:
        label, confidence = engine.predict(args.predict)
        verdict = "PHISHING ⚠️" if label == 1 else "LÉGITIME ✅"
        print(f"\n{'='*60}")
        print(" Prédiction")
        print(f"{'='*60}")
        print(f"Email    : {args.predict}")
        print(f"Résultat : {verdict}  (confiance: {confidence:.1%})")
    else:
        print(f"\n{'='*60}")
        print(" Démo de prédiction sur de nouveaux emails")
        print(f"{'='*60}")
        examples = [
            "URGENT: verify your account now or it will be suspended within 24 hours!",
            "Hi, can we reschedule our meeting to Thursday afternoon instead?",
            "Congratulations, you won a free iPhone! Click here to claim it now.",
            "Attached is the report you asked for, let me know your thoughts.",
        ]
        for ex in examples:
            label, confidence = engine.predict(ex)
            verdict = "PHISHING ⚠️" if label == 1 else "LÉGITIME ✅"
            print(f"\n  \"{ex}\"")
            print(f"  -> {verdict} (confiance: {confidence:.1%})")


if __name__ == "__main__":
    main()
