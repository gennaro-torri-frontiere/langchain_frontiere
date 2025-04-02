# Trice_Demo

## Panoramica
Trice_Demo è un progetto che dimostra l'integrazione di un chatbot e un grounder per la definizione di un LLM-RAG come Q&A per Intera, un azienda di costruzione.

## Chatbot
Il chatbot è progettato per interagire con gli utenti, fornendo risposte basate su regole predefinite o algoritmi di intelligenza artificiale. Può gestire vari tipi di query e fornire informazioni o assistenza pertinenti.

## Grounder
Il grounder è responsabile di garantire che le risposte del chatbot siano accurate e contestualmente appropriate. Il suo funzionamento si basa sulla fase iniziale di un sistema LLM-RAG (Retrieval-Augmented Generation), che comprende:
- Caricamento dei documenti
- Divisione in chunk tramite uno splitter
- Creazione di una funzione di embedding
- Creazione del vector store utilizzando i chunk e la funzione di embedding

Il codice del grounder è strutturato secondo due pattern:
- **Strategy Pattern**: per definire quale classe di grounder utilizzare.
- **Factory Pattern**: per istanziare le risorse necessarie per il grounder.

Le classi principali coinvolte sono:
- **GrounderStrategy**: definisce la strategia di grounding da adottare.
- **Loader**: gestisce il caricamento dei documenti.
- **Splitter**: suddivide i documenti in chunk.
- **Embedder**: genera le rappresentazioni vettoriali dei chunk.
- **VectorStore**: archivia e gestisce i chunk vettorializzati.

## Caratteristiche
- Chatbot interattivo
- Grounding contestuale delle risposte
- Informazioni accurate e affidabili

## Utilizzo
Per utilizzare Trice_Demo, segui questi passaggi:
1. Clona il repository.
2. Installa le dipendenze necessarie.
3. Esegui l'applicazione.

