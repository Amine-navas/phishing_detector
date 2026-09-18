#ifndef naive_bayes_h
#define naive_bayes_h

#include <string>



struct HashTable; 

class NaiveBayesModel
{
public:
    NaiveBayesModel();
    ~NaiveBayesModel();

    void addExample(const std::string &text, int label);

    void finalize();

    int predict(const std::string &text, double *scorePhishing, double *scoreLegit) const;

    int vocabSize() const;

private:
    HashTable *table_;
    long totalWords_[2];
    int classCount_[2];
    double logPrior_[2];
    bool finalized_;
};

#endif // naive_bayes_h