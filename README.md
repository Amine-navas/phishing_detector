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
- **Flask** for the backend
- **HTML / CSS / JavaScript** for the user interface

Instead of implementing the algorithm multiple times, this project follows a **single execution pipeline**, where every language has a dedicated responsibility.

---

# 📑 Table of Contents

- [🌐 Live Demo](#-live-demo)
- [🎥 Video Demo](#-video-demo)
- [📷 Screenshots](#-screenshots)
- [🏗️ Global Architecture](#️-global-architecture)
- [📖 Why this architecture?](#-why-this-architecture)
- [🛠️ Technologies](#️-technologies)
- [📂 Project Structure](#-project-structure)
- [⚙️ Installation](#️-installation)
- [🧠 Machine Learning Pipeline](#-machine-learning-pipeline)
- [🔌 Native API](#-native-api)
- [🌐 Web Interface](#-web-interface)
- [📊 Dataset](#-dataset)
- [🚀 Future Improvements](#-future-improvements)
- [👨‍💻 Author](#-author)

---

# 🌐 Live Demo

The static interface is available here:

**https://amine-navas.github.io/phishing_detector/**

> ⚠️ GitHub Pages hosts only the frontend.
> Real-time predictions require the Flask backend (Python + C/C++) running locally.

---

# 🎥 Video Demo

Watch the application in action:

▶ **[Demo Video](img/test.mp4)**

> GitHub does not embed MP4 videos directly inside README files. Click the link above to watch or download the demonstration.

---

# 📷 Screenshots

## Main Interface

![Interface](img/interface.png)

---

## Legitimate Email Detection

![Legitimate](img/legitime.png)

---

## Phishing Email Detection

![Phishing](img/phishing.png)

---

## Training

![Training](img/training.png)

---

# 🏗️ Global Architecture

```text
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

| Layer          | Responsibility                                            |
| -------------- | --------------------------------------------------------- |
| **C**          | Tokenization, hash table, word counting                   |
| **C++**        | Naive Bayes model, probability computation and prediction |
| **Python**     | Dataset loading, training, evaluation and REST API        |
| **Flask**      | Communication between browser and prediction engine       |
| **JavaScript** | Interactive frontend                                      |

The computationally intensive operations are executed once inside native C/C++ code.

Python acts as the orchestration layer using **ctypes**, avoiding any algorithm reimplementation.

---

# 🛠️ Technologies

- C11
- C++17
- Python 3
- Flask
- HTML5
- CSS3
- JavaScript (ES6)
- ctypes
- scikit-learn
- Git
- GitHub Pages

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
├── img/
│   ├── interface.png
│   ├── legitime.png
│   ├── phishing.png
│   ├── training.png
│   └── test.mp4
│
├── emails.csv
├── build.sh
└── README.md
```

---

# ⚙️ Installation

## 1. Build the native library

```bash
./build.sh
```

This script:

- Compiles the C source code
- Compiles the C++ source code
- Links both into

```text
build/libphishing.so
```

---

## 2. Install dependencies

```bash
pip install flask pandas scikit-learn
```

---

## 3. Launch the backend

```bash
cd python
python server.py
```

Open:

```text
http://localhost:5000
```

---

# 🧠 Machine Learning Pipeline

## Training

```text
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

## Prediction

```text
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

allowing Python to communicate directly with the compiled library through **ctypes**.

---

# 🌐 Web Interface

The browser communicates with Flask through a REST API.

```text
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

### Features

- Real-time phishing detection
- Animated gauge
- Confidence score
- Training statistics
- Session history
- Responsive interface

---

# 📊 Dataset

The project uses a balanced dataset containing:

- 90 phishing emails
- 90 legitimate emails

stored in

```text
emails.csv
```

Format:

```text
label|email_text
```

The dataset can easily be replaced with a larger public phishing dataset.

---

# 🚀 Future Improvements

- Save/load trained models
- TF-IDF support
- URL feature extraction
- Email header analysis
- Logistic Regression implementation
- pybind11 bindings
- Docker deployment
- Authentication system
- Attachment analysis
- Deep learning models

---

# 👨‍💻 Author

**Amine Aymen Senbati**

Software Engineering Student

**Interests**

- Cybersecurity
- Machine Learning
- Systems Programming
- Software Engineering
