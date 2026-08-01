#include "textutils.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define HASH_SIZE 4096

/* ---------- Tokenizer ---------- */

int tokenize(const char *text, char tokens[][MAX_WORD], int max_tokens)
{
    int n = 0;
    char current[MAX_WORD];
    int clen = 0;

    for (const char *p = text;; p++)
    {
        unsigned char c = (unsigned char)*p;
        /* Un octet >= 0x80 appartient à une séquence UTF-8 multioctet (lettres
           accentuées : é, è, à, ç...). isalnum() ne le reconnaît pas en locale
           "C" ; sans ce cas, chaque lettre accentuée casserait le mot en deux
           (ex. "vérifier" -> "rifier", "été" -> disparaît entièrement). On le
           garde donc tel quel comme caractère de mot, sans tenter de le
           mettre en minuscule (pas de repli sûr et portable sans passer par
           les wide chars). */
        if (isalnum(c) || c >= 0x80)
        {
            if (clen < MAX_WORD - 1)
                current[clen++] = (c < 0x80) ? (char)tolower(c) : (char)c;
        }
        else
        {
            if (clen > 2 && n < max_tokens)
            {
                current[clen] = '\0';
                strcpy(tokens[n++], current);
            }
            clen = 0;
            if (*p == '\0')
                break;
        }
    }
    return n;
}

/* ---------- Table de hachage ---------- */

typedef struct WordEntry
{
    char word[MAX_WORD];
    int count[2];
    struct WordEntry *next;
} WordEntry;

struct HashTable
{
    WordEntry *buckets[HASH_SIZE];
    int vocab_size;
};

static unsigned long hash_str(const char *s)
{
    unsigned long h = 5381;
    int c;
    while ((c = (unsigned char)*s++))
        h = ((h << 5) + h) + c; /* djb2 */
    return h % HASH_SIZE;
}

HashTable *ht_create(void)
{
    HashTable *ht = calloc(1, sizeof(HashTable));
    return ht;
}

void ht_free(HashTable *ht)
{
    if (!ht)
        return;
    for (int i = 0; i < HASH_SIZE; i++)
    {
        WordEntry *e = ht->buckets[i];
        while (e)
        {
            WordEntry *next = e->next;
            free(e);
            e = next;
        }
    }
    free(ht);
}

static WordEntry *find(const HashTable *ht, const char *key)
{
    unsigned long idx = hash_str(key);
    WordEntry *e = ht->buckets[idx];
    while (e)
    {
        if (strcmp(e->word, key) == 0)
            return e;
        e = e->next;
    }
    return NULL;
}

void ht_increment(HashTable *ht, const char *key, int class_id)
{
    unsigned long idx = hash_str(key);
    WordEntry *e = ht->buckets[idx];
    while (e)
    {
        if (strcmp(e->word, key) == 0)
        {
            e->count[class_id]++;
            return;
        }
        e = e->next;
    }
    WordEntry *ne = calloc(1, sizeof(WordEntry));
    strncpy(ne->word, key, MAX_WORD - 1);
    ne->count[class_id] = 1;
    ne->next = ht->buckets[idx];
    ht->buckets[idx] = ne;
    ht->vocab_size++;
}

int ht_get(const HashTable *ht, const char *key, int class_id)
{
    WordEntry *e = find(ht, key);
    return e ? e->count[class_id] : 0;
}

int ht_contains(const HashTable *ht, const char *key)
{
    return find(ht, key) != NULL;
}

int ht_vocab_size(const HashTable *ht)
{
    return ht->vocab_size;
}