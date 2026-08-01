#ifndef naive_bayes_h
#define naive_bayes_h

#include <string>

/*
 * Moteur de classification (C++), couche intermédiaire du pipeline.
 * -------------------------------------------------------------------
 * S'appuie sur le tokenizer et la table de hachage fournis par le module C
 * (c/textutils.c) pour implémenter un classifieur Naive Bayes bag-of-words,
 * avec lissage de Laplace et log-probabilités.
 *
 * Cette classe est ensuite exposée à Python via une API C (extern "C"),
 * compilée en bibliothèque partagée (libphishing.so) et chargée avec ctypes.
 */

struct HashTable; // type opaque défini dans textutils.c

class NaiveBayesModel
{
public:
    NaiveBayesModel();
    ~NaiveBayesModel();

    // Ajoute un exemple d'entraînement (label : 1 = phishing, 0 = légitime)
    void addExample(const std::string &text, int label);

    // Calcule les probabilités a priori une fois tous les exemples ajoutés
    void finalize();

    // Prédit la classe d'un texte. Remplit *scorePhishing / *scoreLegit
    // avec les log-scores (utiles pour estimer une confiance côté Python).
    // Retourne 1 (phishing) ou 0 (légitime).
    int predict(const std::string &text, double *scorePhishing, double *scoreLegit) const;

    // Nombre de mots distincts appris par le modèle (délégué à la table de hachage C).
    int vocabSize() const;

private:
    HashTable *table_;
    long totalWords_[2];
    int classCount_[2];
    double logPrior_[2];
    bool finalized_;
};

#endif // naive_bayes_h