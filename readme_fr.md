Analyse grammaticale des nombres de Sophie Germain

Modèle interne G1/G2/G3, angle 348°, génération de safe primes et laboratoire Python reproductible

Résumé

Ce dépôt présente une approche entièrement nouvelle pour l’étude des nombres de Sophie Germain (SG) et des safe primes associés. Il s’appuie sur une analyse empirique approfondie, une modélisation modulaire (angle 348°), et la construction d’une grammaire interne en trois niveaux (G1, G2, G3) permettant de reproduire la dynamique réelle des écarts entre SG.

Le projet inclut :
    • un laboratoire Python complet (Tkinter)
    • un générateur de SG basé sur la grammaire
    • un modèle hasard pour comparaison
    • un générateur de safe primes
    • des visualisations (histogrammes, analyses comparatives)
    • un export LaTeX automatique
    • un rapport scientifique détaillé
    • une explication mathématique accessible

Ce travail vise à offrir une base ouverte, reproductible et rigoureuse pour l’étude des structures internes des nombres premiers.

1. Contexte mathématique

Un nombre est dit Sophie Germain si :

		p  premier      and     q = 2p + 1     premier 

Les SG réels se concentrent presque exclusivement dans le résidu :

		p = 29 (mod 30), appelé ici angle 348°.

        Cette observation constitue la base de la grammaire interne.

2. La grammaire interne G1 / G2 / G3

    G1 — Squelette
        Écarts fréquents et réguliers, structure dominante.
    G2 — Motifs internes
        Transitions privilégiées entre écarts, motifs récurrents.
    G3 — Anomalies
        Séquences rares mais réelles, indispensables pour reproduire les SG observés.

    Cette grammaire permet de générer des SG synthétiques dont la densité et la structure correspondent étroitement aux SG réels.

3. Modèle grammatical vs modèle hasard

Le dépôt inclut un comparatif systématique entre :
    • un modèle grammatical (G1/G2/G3)
    • un modèle aléatoire (sélection uniforme dans l’angle 348°)
    Résultats :
        • écarts faibles et stables dans la grammaire
        • écarts très grands dans le modèle hasard
        • densité interne incompatible avec un modèle aléatoire
        • motifs structurels reproductibles

4. Safe primes

Chaque SG génère un candidat :
					q = 2p + 1

Le générateur de safe primes applique un filtrage supplémentaire pour sélectionner les qui produisent un premier dans l’angle 348°.

Le dépôt inclut :
    • la liste des safe primes générés
    • les SG associés
    • les SG grammaticaux sans safe prime
    • les safe primes provenant de SG hors de la chaîne principale

5. Contenu du dépôt
    • Code Python complet (Tkinter)
    • Générateur SG grammatical
    • Modèle hasard
    • Générateur de safe primes
    • Histogrammes et graphiques
    • Export LaTeX automatique
    • Rapport scientifique
    • Explication mathématique détaillée
    • Données reproductibles

6. Objectif du projet

Ce travail vise à :
    • proposer une approche nouvelle de la théorie des nombres
    • mettre en lumière des structures internes souvent ignorées
    • offrir un laboratoire reproductible
    • encourager la recherche ouverte et indépendante
    • fournir une base solide pour des travaux futurs (cryptographie, heuristiques, modélisation)


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18408778.svg)](https://doi.org/10.5281/zenodo.18408778)
