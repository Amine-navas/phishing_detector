#ifndef textutils_h
#define textutils_h

/*
 * Couche bas niveau (C) du détecteur de phishing.
 * ---------------------------------------------------
 * Fournit deux briques réutilisées par le moteur C++ :
 *   1. Un tokenizer rapide (pas d'allocations dynamiques par mot)
 *   2. Une table de hachage generique "mot -> (compte classe 0, compte classe 1)"
 *
 * Ce module ne connaît rien au machine learning : c'est une bibliothèque
 * d'outils texte bas niveau, sur laquelle le moteur C++ (naive_bayes.cpp)
 * construit la logique du modèle.
 */

#ifdef __cplusplus
extern "C"
{
#endif

#define MAX_WORD 64
#define MAX_TOKENS 128

    /* Découpe `text` en tokens alphanumériques, en minuscules, de longueur > 2.
     * Écrit jusqu'à `max_tokens` tokens dans `tokens` (buffer MAX_WORD par mot).
     * Retourne le nombre de tokens écrits. */
    int tokenize(const char *text, char tokens[][MAX_WORD], int max_tokens);

    /* Table de hachage : mot -> {compte pour la classe 0, compte pour la classe 1}.
     * Implémentée avec chaînage (hash djb2). Type opaque pour le C++. */
    typedef struct HashTable HashTable;

    HashTable *ht_create(void);
    void ht_free(HashTable *ht);

    /* Incrémente le compteur de `key` pour la classe `class_id` (0 ou 1).
     * Crée l'entrée si elle n'existe pas encore. */
    void ht_increment(HashTable *ht, const char *key, int class_id);

    /* Retourne le compte de `key` pour la classe donnée (0 si le mot est absent). */
    int ht_get(const HashTable *ht, const char *key, int class_id);

    /* Retourne 1 si `key` a déjà été vu au moins une fois, 0 sinon. */
    int ht_contains(const HashTable *ht, const char *key);

    /* Nombre de mots distincts stockés dans la table. */
    int ht_vocab_size(const HashTable *ht);

#ifdef __cplusplus
}
#endif
#endif
