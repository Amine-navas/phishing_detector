#!/usr/bin/env bash
# Compile le module C (textutils) et le module C++ (naive_bayes) ensemble
# en une seule bibliothèque partagée compatible avec ctypes.
# Sur Linux/macOS cela produit build/libphishing.so ; sur Windows/MinGW cela
# produit aussi build/libphishing.dll pour éviter les erreurs de chargement.
set -e
cd "$(dirname "$0")"

mkdir -p build

echo "[1/3] Compilation du module C (textutils.c)..."
gcc -O2 -fPIC -std=c11 -Wall -c c/textutils.c -o build/textutils.o

echo "[2/3] Compilation du module C++ (naive_bayes.cpp)..."
g++ -O2 -fPIC -std=c++17 -Wall -Ic -c cpp/naive_bayes.cpp -o build/naive_bayes.o

echo "[3/3] Édition de liens -> build/libphishing.so et build/libphishing.dll"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OS" == "Windows_NT" ]]; then
  g++ -shared -o build/libphishing.dll build/textutils.o build/naive_bayes.o
else
  g++ -shared -o build/libphishing.so build/textutils.o build/naive_bayes.o
fi

echo "Build terminé : build/libphishing.so (et build/libphishing.dll si disponible)"