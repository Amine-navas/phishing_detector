#include "naive_bayes.h"
#include "textutils.h"
#include <cmath>
using namespace std;
NaiveBayesModel::NaiveBayesModel() : finalized_(false)
{
    table_ = ht_create();
    totalWords_[0] = totalWords_[1] = 0;
    classCount_[0] = classCount_[1] = 0;
    logPrior_[0] = logPrior_[1] = 0.0;
}

NaiveBayesModel::~NaiveBayesModel()
{
    ht_free(table_);
}

void NaiveBayesModel::addExample(const string &text, int label)
{
    char tokens[MAX_TOKENS][MAX_WORD];
    int n = tokenize(text.c_str(), tokens, MAX_TOKENS);

    classCount_[label]++;
    for (int i = 0; i < n; i++)
    {
        ht_increment(table_, tokens[i], label); // délégué au module C
        totalWords_[label]++;
    }
}

void NaiveBayesModel::finalize()
{
    int total = classCount_[0] + classCount_[1];
    logPrior_[0] = log(static_cast<double>(classCount_[0]) / total);
    logPrior_[1] = log(static_cast<double>(classCount_[1]) / total);
    finalized_ = true;
}

int NaiveBayesModel::predict(const string &text, double *scorePhishing, double *scoreLegit) const
{
    char tokens[MAX_TOKENS][MAX_WORD];
    int n = tokenize(text.c_str(), tokens, MAX_TOKENS); // délégué au module C
    int vocab = ht_vocab_size(table_);

    double logScore[2] = {logPrior_[0], logPrior_[1]};

    for (int i = 0; i < n; i++)
    {
        if (!ht_contains(table_, tokens[i]))
            continue; // mot inconnu -> ignoré
        for (int c = 0; c < 2; c++)
        {
            int count = ht_get(table_, tokens[i], c); // délégué au module C
            logScore[c] += log(static_cast<double>(count + 1) / (totalWords_[c] + vocab));
        }
    }

    if (scoreLegit)
        *scoreLegit = logScore[0];
    if (scorePhishing)
        *scorePhishing = logScore[1];
    return (logScore[1] > logScore[0]) ? 1 : 0;
}

int NaiveBayesModel::vocabSize() const
{
    return ht_vocab_size(table_);
}

/* =====================================================================
 * API C exposée pour Python (ctypes).
 * Les noms ne sont pas "manglés" grâce à extern "C", ce qui permet à
 * ctypes.CDLL de les appeler directement depuis Python.
 * ===================================================================== */
extern "C"
{

    void *nb_create()
    {
        return new NaiveBayesModel();
    }

    void nb_free(void *model)
    {
        delete static_cast<NaiveBayesModel *>(model);
    }

    void nb_add_example(void *model, const char *text, int label)
    {
        static_cast<NaiveBayesModel *>(model)->addExample(text, label);
    }

    void nb_finalize(void *model)
    {
        static_cast<NaiveBayesModel *>(model)->finalize();
    }

    int nb_predict(void *model, const char *text, double *score_phishing, double *score_legit)
    {
        return static_cast<NaiveBayesModel *>(model)->predict(text, score_phishing, score_legit);
    }

    int nb_vocab_size(void *model)
    {
        return static_cast<NaiveBayesModel *>(model)->vocabSize();
    }

} // extern "C"
