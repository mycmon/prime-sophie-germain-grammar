Grammatical Analysis of Sophie Germain Primes

Internal G1/G2/G3 model, 348° angle, safe prime generation and reproducible Python laboratory

Summary

This repository introduces a completely new approach to studying Sophie Germain primes (SG) and their associated safe primes. It is based on deep empirical analysis, modular structure (348° angle), and a three‑level internal grammar (G1, G2, G3) that reproduces the real dynamics of SG gaps.

The project includes:
    • a complete Python laboratory (Tkinter)
    • a grammar‑based SG generator
    • a random comparison model
    • a safe prime generator
    • visualizations (histograms, comparative analysis)
    • automatic LaTeX export
    • a detailed scientific report
    • an accessible mathematical explanation

This work provides an open, reproducible, and rigorous framework for exploring the internal structure of prime numbers.

1. Mathematical Background

A number is a Sophie Germain prime if:

				p  prime      and     q = 2p + 1     prime 

Real SG primes concentrate almost exclusively in the residue:

			p = 29 (mod 30), referred to here as the 348° angle.

            This observation forms the basis of internal grammar.

2. Internal Grammar G1 / G2 / G3

    G1 — Skeleton
        Frequent and regular gaps, dominant structure.
    G2 — Internal Motifs
        Preferred transitions between gaps, recurrent patterns.
    G3 — Anomalies
        Rare but real sequences, essential for reproducing real SG behavior.

    This grammar generates synthetic SG primes whose density and structure closely match real SG primes.

3. Grammatical Model vs Random Model

The repository includes a systematic comparison between:
    • the grammatical model (G1/G2/G3)
    • a random model (uniform selection in the 348° angle)

Findings:
    • small and stable gap values in the grammar
    • very large gaps in the random model
    • internal density incompatible with randomness
    • reproducible structural motifs

4. Safe Primes

Each SG produces a candidate:
					q = 2p + 1

    The safe‑prime generator applies additional filtering to select the that produce a prime in the 348° angle.
    The repository includes:
        • generated safe primes
        • associated SG primes
        • grammatical SG without safe primes
        • safe primes originating from SG outside the main chain

5. Repository Contents
    • Full Python code (Tkinter)
    • Grammatical SG generator
    • Random model
    • Safe prime generator
    • Histograms and plots
    • Automatic LaTeX export
    • Scientific report
    • Detailed mathematical explanation
    • Reproducible data

6. Purpose of the Project

This work aims to:
    • introduce a new empirical approach to number theory
    • provide a reproducible laboratory for SG analysis
    • highlight internal structures often overlooked
    • support open and independent research
    • offer a foundation for future work (cryptography, heuristics, modeling)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18408778.svg)](https://doi.org/10.5281/zenodo.18408778)


