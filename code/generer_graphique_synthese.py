import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from collections import Counter
import os

def generer_graphique_synthese(chemin_fichier):
    """
    Génère un graphique de synthèse explicatif optimisé pour la lisibilité.
    Affiche la roue des transitions avec des nœuds carrés, la matrice et les deltas.
    """
    if not os.path.exists(chemin_fichier):
        print(f"Erreur : '{chemin_fichier}' introuvable.")
        return

    # 1. Chargement et nettoyage
    df = pd.read_csv(chemin_fichier, sep=None, engine='python')
    df.columns = [c.strip() for c in df.columns]
    
    total = len(df)
    
    # 2. Préparation des statistiques
    familles = [132, 276, 348]
    transitions = list(zip(df['fam_p'], df['fam_q']))
    counts = Counter(transitions)
    
    # Création de la figure avec un espacement amélioré
    fig = plt.figure(figsize=(16, 12))
    # Ajustement des ratios de hauteur : la zone du milieu (matrice/rotation) est agrandie
    grid = plt.GridSpec(3, 2, wspace=0.25, hspace=0.5, height_ratios=[1, 1.4, 0.3])

    # --- ZONE 1 : ANALYSE DES MOTIFS ---
    ax_motifs = fig.add_subplot(grid[0, 0])
    ax_motifs.axis('off')
    deltas_list = df['delta'].tolist()
    motifs2 = Counter([(deltas_list[i], deltas_list[i+1]) for i in range(len(deltas_list)-1)]).most_common(5)
    
    motif_text = "1. MÉMOIRE ET MOTIFS\n\n"
    motif_text += "Top Séquences (2 Deltas) :\n"
    for m, c in motifs2:
        motif_text += f" • {m} : {c} fois\n"
    motif_text += "Note : Symétrie observée. Le système compense souvent\n"
    motif_text += "un saut par son inverse."
    
    ax_motifs.text(0.1, 0.5, motif_text, fontsize=10, family='monospace', verticalalignment='center',
                   bbox=dict(facecolor='#E0F7FA', alpha=0.6, boxstyle='round,pad=0.8', edgecolor='#00ACC1'))

    # --- ZONE 2 : TOP 10 DES DELTAS ---
    ax_deltas = fig.add_subplot(grid[0, 1])
    top_10_deltas = Counter(df['delta']).most_common(10)
    d_vals, d_counts = zip(*top_10_deltas)
    
    colors = plt.cm.Blues(np.linspace(0.6, 0.3, 10))
    bars = ax_deltas.bar([str(x) for x in d_vals], d_counts, color=colors, edgecolor='black', linewidth=0.8)
    ax_deltas.set_title("2. RÉSONANCE : Fréquence des Δ", fontsize=12, fontweight='bold', pad=15)
    ax_deltas.tick_params(axis='both', which='major', labelsize=9)
    
    for bar in bars:
        height = bar.get_height()
        ax_deltas.text(bar.get_x() + bar.get_width()/2., height + 3, f'{int(height)}', ha='center', va='bottom', fontsize=8)

    # --- ZONE 3 : MATRICE DE TRANSITION ---
    ax_matrix = fig.add_subplot(grid[1, 0])
    matrix_data = []
    for f_p in familles:
        row = [counts.get((f_p, f_q), 0) for f_q in familles]
        matrix_data.append(row)
    
    im = ax_matrix.imshow(matrix_data, cmap='YlGnBu', aspect='auto')
    ax_matrix.set_xticks(np.arange(len(familles)))
    ax_matrix.set_yticks(np.arange(len(familles)))
    ax_matrix.set_xticklabels(familles, fontsize=9)
    ax_matrix.set_yticklabels(familles, fontsize=9)
    ax_matrix.set_title("3. MATRICE DE PASSAGE (%)", fontsize=12, fontweight='bold', pad=15)
    
    for i in range(len(familles)):
        for j in range(len(familles)):
            val = matrix_data[i][j]
            color = "white" if val > 850 else "black"
            ax_matrix.text(j, i, f"{val}\n({(val/total)*100:.1f}%)", 
                           ha="center", va="center", color=color, fontweight='bold', fontsize=9)
    ax_matrix.set_xlabel("Vers (q)", fontsize=10)
    ax_matrix.set_ylabel("De (p)", fontsize=10)

    # --- ZONE 4 : LA ROUE DES TRANSITIONS (Agrandie verticalement) ---
    ax_graph = fig.add_subplot(grid[1, 1])
    G = nx.DiGraph()
    
    pos = {132: (0, 1), 276: (0.86, -0.5), 348: (-0.86, -0.5)}
    labels = {132: "F. 132", 276: "F. 276", 348: "F. 348"}
    
    for u in familles:
        for v in familles:
            if u != v:
                w = counts.get((u, v), 0)
                G.add_edge(u, v, weight=w)

    nx.draw_networkx_nodes(G, pos, node_size=3200, node_color=['#FF9999','#66B3FF','#99FF99'], 
                           node_shape='s', edgecolors='black', linewidths=1.5, ax=ax_graph)
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold', ax=ax_graph)
    
    for u, v, d in G.edges(data=True):
        width = d['weight'] / 200 
        nx.draw_networkx_edges(G, pos, edgelist=[(u,v)], width=width, 
                               edge_color='#666666', arrowsize=15, 
                               connectionstyle='arc3,rad=0.12', ax=ax_graph)
        
        x = (pos[u][0] + pos[v][0]) / 2 * 1.2
        y = (pos[u][1] + pos[v][1]) / 2 * 1.2
        ax_graph.text(x, y, f"{d['weight']}", fontsize=14, color='black', ha='center')

    ax_graph.set_title("4. DYNAMIQUE DE ROTATION", fontsize=12, fontweight='bold', pad=15)
    ax_graph.axis('on')

    # --- ZONE 5 : OBSERVATIONS (Alignée sur la largeur de la matrice) ---
    # On utilise GridSpec pour que le texte occupe seulement la colonne de gauche
    ax_text = fig.add_subplot(grid[2, 0])
    ax_text.axis('off')
    
    resume_texte = (
        "OBSERVATIONS (7742 lignes)\n"
        "ROTATION : Cycles 132→276→348 dominants\n"
        "DYNAMIQUE : 62.7% de mouvements | Delta 60 pivot"
    )
    
    ax_text.text(0.5, 0.5, resume_texte, fontsize=9, fontweight='bold', ha='center', va='center',
                 bbox=dict(facecolor='#F5F5F5', edgecolor='#BDBDBD', alpha=0.9, boxstyle='round,pad=0.8'))

    plt.suptitle("SYNTHÈSE : ROUAGES DES NOMBRES DE SOPHIE GERMAIN", fontsize=16, fontweight='bold', y=0.97)
    plt.show()

if __name__ == "__main__":
    generer_graphique_synthese("donnees_g3.csv")
