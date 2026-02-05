import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import os

def analyser_G3(chemin_fichier):
    """
    Analyse approfondie des anomalies G3 à partir d'un fichier CSV structuré.
    Colonnes attendues : n, p, fam_p, q, fam_q, delta, G1, G2, G3
    """
    
    if not os.path.exists(chemin_fichier):
        print(f"Erreur : Le fichier '{chemin_fichier}' est introuvable.")
        print("Assurez-vous que le fichier est dans le même dossier que ce script.")
        return

    # --- 1. LECTURE DES DONNÉES AVEC PANDAS ---
    try:
        # Détection automatique du séparateur (virgule, tabulation ou espace)
        df = pd.read_csv(chemin_fichier, sep=None, engine='python')
        
        # Nettoyage des noms de colonnes
        df.columns = [c.strip() for c in df.columns]
        
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return

    total = len(df)
    if total == 0:
        print("Erreur : Le fichier est vide.")
        return

    # --- 2. CALCULS STATISTIQUES ---
    deltas = df['delta'].tolist()
    fam_departs = df['fam_p'].tolist()
    
    # Création des transitions (ex: 276->348)
    transitions = [f"{row['fam_p']}->{row['fam_q']}" for _, row in df.iterrows()]
    
    # Motifs de taille 2 et 3 sur les deltas
    motifs2 = [(deltas[i], deltas[i+1]) for i in range(len(deltas)-1)]
    motifs3 = [(deltas[i], deltas[i+1], deltas[i+2]) for i in range(len(deltas)-2)]

    # --- 3. AFFICHAGE DU RÉSUMÉ DÉTAILLÉ ---
    print("="*60)
    print(f"RAPPORT D'ANALYSE AVANCÉ - {total} LIGNES TRAITÉES")
    print("="*60)
    
    print(f"\n[1] RÉPARTITION DES FAMILLES (MOD 30)")
    c_dep = Counter(fam_departs).most_common()
    for fam, count in c_dep:
        print(f"  Position {fam:3} : {count:4} occurrences ({ (count/total)*100:5.1f}%)")

    print(f"\n[2] TOP 10 DES TRANSITIONS")
    # Analyse de la circulation entre les colonnes
    for trans, count in Counter(transitions).most_common(10):
        print(f"  {trans:9} : {count:4} fois ({ (count/total)*100:5.1f}%)")

    print(f"\n[3] ANALYSE DES DELTAS (Δ)")
    moyenne = sum(deltas)/len(deltas)
    print(f"  Δ Min : {min(deltas)} | Δ Max : {max(deltas)} | Δ Moyen : {moyenne:.2f}")
    top_deltas = Counter(deltas).most_common(10)
    for d, c in top_deltas:
        print(f"  Δ {d:4} : {c:4} fois")

    print(f"\n[4] ANALYSE DES MOTIFS SÉQUENTIELS (Cycles de Deltas)")
    print(f"  Top 5 Séquences de 2 Δ : {Counter(motifs2).most_common(5)}")
    print(f"  Top 5 Séquences de 3 Δ : {Counter(motifs3).most_common(5)}")
    
    # --- 4. GÉNÉRATION DES GRAPHIQUES ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Graphique 1 : Distribution des Deltas (Histogramme)
    # Utilisation d'un pas de 6 pour la granularité du crible
    ax1.hist(deltas, bins=range(int(min(deltas)), int(max(deltas)) + 12, 6), color='#5DADE2', edgecolor='black', alpha=0.8)
    ax1.set_title(f"Distribution des Deltas (n={total})", fontsize=14)
    ax1.set_xlabel("Valeur de Δ", fontsize=12)
    ax1.set_ylabel("Nombre d'occurrences", fontsize=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Ligne de la moyenne
    ax1.axvline(moyenne, color='red', linestyle='dashed', linewidth=1, label=f'Moyenne: {moyenne:.1f}')
    ax1.legend()

    # Graphique 2 : Camembert des Familles de Départ
    counts_dep = Counter(fam_departs)
    # Tri pour assurer la correspondance des couleurs si besoin
    labels = [f"Pos {k}" for k in counts_dep.keys()]
    colors = ['#FF9999','#66B3FF','#99FF99']
    ax2.pie(counts_dep.values(), labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, shadow=True, explode=(0.05, 0.05, 0.05))
    ax2.set_title("Équilibre des Familles de Départ", fontsize=14)

    plt.tight_layout()
    plt.show()

# --- CONFIGURATION ---
if __name__ == "__main__":
    # Nom du fichier à analyser (assurez-vous qu'il est dans le répertoire)
    NOM_FICHIER = "donnees_g3.csv" 
    
    try:
        import pandas
        analyser_G3(NOM_FICHIER)
    except ImportError:
        print("Erreur : Les bibliothèques 'pandas' et 'matplotlib' sont requises.")
        print("Installez-les avec : pip install pandas matplotlib")
