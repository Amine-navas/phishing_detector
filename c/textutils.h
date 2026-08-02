#ifndef TEXTUTILS_H
#define TEXTUTILS_H

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_WORD 64
#define MAX_TOKENS 512

typedef struct HashTable HashTable;

int tokenize(const char *text, char tokens[][MAX_WORD], int max_tokens);

HashTable *ht_create(void);
void ht_free(HashTable *ht);
void ht_increment(HashTable *ht, const char *key, int class_id);
int ht_get(const HashTable *ht, const char *key, int class_id);
int ht_contains(const HashTable *ht, const char *key);
int ht_vocab_size(const HashTable *ht);

#ifdef __cplusplus
}
#endif

#endif /* TEXTUTILS_H */
