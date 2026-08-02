"""
Serveur web pour l'interface du détecteur de phishing.
=========================================================
IMPORTANT : ce fichier n'ajoute aucune logique de classification et ne
modifie AUCUNE des fonctions déjà écrites. Il se contente d'importer
`PhishingEngine` et `load_data` depuis phishing_detector.py (inchangé)
et de les exposer via une petite API HTTP (Flask), consommée par
l'interface HTML dans ../web/.

Chaîne complète, inchangée :
    web/index.html (JS)  -->  server.py (Flask, ce fichier)
        -->  PhishingEngine (phishing_detector.py, inchangé)
            -->  libphishing.so (C++ naive_bayes.cpp, inchangé)
                -->  textutils.c (C, inchangé)

Lancement :
    ./build.sh                     # si pas déjà fait (compile libphishing.so)
    cd python && python3 server.py
    -> ouvrir http://localhost:5000 dans un navigateur
"""

import os

try:
    from flask import Flask, jsonify, request, send_from_directory
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
except ImportError as exc:
    missing = getattr(exc, "name", None) or str(exc).split("'")[1]
    raise ImportError(
        f"Missing Python dependency: {missing}.\n"
        "Install required packages with:\n"
        "  pip install -r requirements.txt\n"
        "from the phishing_detecteur directory."
    ) from exc

if __package__ in {None, ""}:
    from phishing_detector import PhishingEngine, load_data
else:
    from .phishing_detector import PhishingEngine, load_data

HERE = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(HERE, "..", "web")

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")


def _bootstrap():
    """Charge les données et entraîne le moteur natif une seule fois,
    au démarrage du serveur, en utilisant exclusivement l'API déjà fournie
    par phishing_detector.py (load_data, PhishingEngine.fit/predict_batch)."""
    print("Chargement des données et entraînement du moteur natif (C++/C)...")
    df = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
    )

    engine = PhishingEngine()
    engine.fit(X_train.tolist(), y_train.tolist())

    y_pred = engine.predict_batch(X_test.tolist())
    stats = {
        "vocab_size": engine.vocab_size(),
        "dataset_size": int(len(df)),
        "phishing_count": int(df["label"].sum()),
        "legit_count": int((df["label"] == 0).sum()),
        "test_set_size": int(len(X_test)),
        "test_accuracy": round(float(accuracy_score(y_test, y_pred)), 3),
        "test_precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 3),
        "test_recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 3),
        "test_f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 3),
    }
    print(f"Moteur prêt : {stats}")
    return engine, stats


try:
    engine, STATS = _bootstrap()
except Exception as exc:
    engine = None
    STATS = {"error": str(exc)}
    print(f"Initialisation du moteur impossible : {exc}")


@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/api/stats")
def stats():
    return jsonify(STATS)


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Le texte de l'email est vide."}), 400
    if len(text) > 5000:
        return jsonify({"error": "Texte trop long (5000 caractères max)."}), 400

    if engine is None:
        return jsonify({"error": "Le moteur n'est pas initialisé. Vérifiez la bibliothèque native et le dataset.(lance le serveur d'abord)"}), 500

    label, confidence = engine.predict(text)  # méthode déjà fournie, non modifiée
    return jsonify({
        "label": int(label),
        "verdict": "phishing" if label == 1 else "legit",
        "confidence": round(float(confidence), 4),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Interface disponible sur http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
