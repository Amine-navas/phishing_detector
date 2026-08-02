# 🛡️ Phishing Email Detector

![Cybersecurity](https://img.shields.io/badge/Cybersecurity-Project-red?style=for-the-badge&logo=hackaday)
![C](https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask)
![Naive Bayes](https://img.shields.io/badge/Machine%20Learning-Naive%20Bayes-success?style=for-the-badge)

A complete **phishing email detection system** built using a **multi-language architecture**.

The project combines:

- **C** for high-performance text processing
- **C++** for the Naive Bayes machine learning engine
- **Python** for orchestration, evaluation and REST API
- **Flask** for the web backend
- **HTML/CSS/JavaScript** for the user interface

Rather than implementing the same algorithm three times, the project follows a **single execution pipeline**, where every language has a dedicated responsibility.

---

# 🌐 Live Demo

The static interface is available here:

**https://amine-navas.github.io/phishing_detector/**

> ⚠️ GitHub Pages only hosts the frontend.
> Real-time predictions require the Flask backend running locally.

---

# 📷 Screenshots

## Interface , prediction et tout

[!Prediction](img/WhatsApp%20Video%202026-08-02%20at%2021.32.56.mp4)

# 🏗️ Global Architecture

```
             HTML / CSS / JavaScript
                     │
                 HTTP (JSON)
                     │
                     ▼
               Flask REST API
                     │
                     ▼
          Python (ctypes bindings)
                     │
                     ▼
       C++ Naive Bayes implementation
                     │
                     ▼
      C tokenizer + hash table engine
```

---

# 📖 Why this architecture?

| Layer          | Responsibility                                      |
| -------------- | --------------------------------------------------- |
| **C**          | Tokenization, hash table, word counting             |
| **C++**        | Naive Bayes model, probabilities, prediction        |
| **Python**     | Dataset loading, training, evaluation, REST API     |
| **Flask**      | Communication between browser and prediction engine |
| **JavaScript** | Interactive user interface                          |

The heavy computations are executed only once inside native code (C/C++).
Python simply orchestrates the workflow using **ctypes**.

---

# 📂 Project Structure

```text
phishing_detector/
│
├── build/
│
├── c/
│   ├── textutils.c
│   └── textutils.h
│
├── cpp/
│   ├── naive_bayes.cpp
│   └── naive_bayes.h
│
├── python/
│   ├── phishing_detector.py
│   └── server.py
│
├── web/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── emails.csv
├── build.sh
└── README.md
```

---

# ⚙️ Installation

## Build the native library

```bash
./build.sh
```

This compiles

- C source code
- C++ source code
- links both into

```
build/libphishing.so
```

---

## Install Python dependencies

```bash
pip install flask pandas scikit-learn
```

---

## Launch the web server

```bash
cd python
python server.py
```

Open

```
http://localhost:5000
```

---

# 🧠 Machine Learning Pipeline

Training:

```
Dataset
    │
    ▼
Tokenizer (C)
    │
    ▼
Word Frequencies
    │
    ▼
Naive Bayes (C++)
    │
    ▼
Probability Model
```

Prediction:

```
Email
   │
   ▼
Tokenizer
   │
   ▼
Word Counts
   │
   ▼
Naive Bayes
   │
   ▼
Legitimate / Phishing
```

---

# 🔌 Native API

```cpp
void* nb_create();

void nb_add_example(
    void* model,
    const char* text,
    int label
);

void nb_finalize(
    void* model
);

int nb_predict(
    void* model,
    const char* text,
    double* phishing_score,
    double* legit_score
);

int nb_vocab_size(void* model);

void nb_free(void* model);
```

The API is exported with

```cpp
extern "C"
```

allowing Python to access the compiled library through **ctypes**.

---

# 🌐 Web Interface

The browser communicates with Flask using a REST API.

```
Browser
      │
 POST /api/predict
      │
      ▼
 Flask
      │
      ▼
Python Engine
      │
      ▼
Native C++ Library
```

Features include:

- Real-time phishing detection
- Interactive gauge
- Confidence score
- Training statistics
- Session history

---

# 📊 Dataset

The project uses a balanced dataset of

- 90 phishing emails
- 90 legitimate emails

stored in

```
emails.csv
```

The format is

```
label|email_text
```

It can easily be replaced with a larger public phishing dataset.

---

# 🚀 Future Improvements

- Model persistence (save/load)
- TF-IDF features
- URL analysis
- Header analysis
- Logistic Regression implementation
- pybind11 bindings
- Docker deployment
- User authentication
- Email attachment analysis

---

# 👨‍💻 Author

**Amine Aymen Senbati**

Software Engineering Student

Cybersecurity • Machine Learning • Systems Programming
