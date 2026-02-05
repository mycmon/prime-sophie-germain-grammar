import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from collections import Counter
import os
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AppG3:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorateur de Structure G3 - Analyse Markovienne & Rythmique")
        self.root.geometry("1400x900")
        
        self.chemin_fichier = "donnees_g3.csv"
        self.df = None
        self.familles = [132, 276, 348]
        
        self.setup_ui()
        self.charger_donnees()

    def setup_ui(self):
        # Panneau de gauche : Contrôles
        control_panel = ttk.Frame(self.root, padding="10")
        control_panel.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control_panel, text="TESTS D'HYPOTHÈSES", font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        self.test1_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_panel, text="Test 1 : Symétrie des motifs inversés", variable=self.test1_var).pack(anchor=tk.W, pady=5)
        
        self.test2_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_panel, text="Test 2 : Corrélation Motif × Δ moyen", variable=self.test2_var).pack(anchor=tk.W, pady=5)
        
        self.test3_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_panel, text="Test 3 : Analyse des Rangs (1, 2, 3)", variable=self.test3_var).pack(anchor=tk.W, pady=5)

        ttk.Button(control_panel, text="Lancer l'Analyse", command=self.mettre_a_jour_graphique).pack(pady=20, fill=tk.X)

        # Zone de texte pour les résultats des tests
        ttk.Label(control_panel, text="RÉSULTATS DES TESTS :", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W)
        self.result_text = tk.Text(control_panel, width=45, height=35, font=('Consolas', 9))
        self.result_text.pack(pady=5, fill=tk.BOTH, expand=True)

        # Panneau de droite : Graphiques
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def charger_donnees(self):
        if not os.path.exists(self.chemin_fichier):
            messagebox.showerror("Erreur", f"Le fichier {self.chemin_fichier} est introuvable.")
            return
        
        self.df = pd.read_csv(self.chemin_fichier, sep=None, engine='python')
        self.df.columns = [c.strip() for c in self.df.columns]
        self.mettre_a_jour_graphique()

    def analyser_signatures(self):
        deltas = self.df['delta'].tolist()
        fams_p = self.df['fam_p'].tolist()
        fams_q = self.df['fam_q'].tolist()
        
        signatures = {(p, q): Counter() for p in self.familles for q in self.familles}
        deltas_par_trans = {(p, q): [] for p in self.familles for q in self.familles}
        
        for i in range(len(self.df) - 1):
            p, q = fams_p[i], fams_q[i]
            motif = (deltas[i], deltas[i+1])
            signatures[(p, q)][motif] += 1
            deltas_par_trans[(p, q)].append(deltas[i])
            
        return signatures, deltas_par_trans

    def executer_tests_logiques(self, signatures, deltas_par_trans):
        self.result_text.delete('1.0', tk.END)
        log = ""

        if self.test1_var.get():
            log += "=== TEST 1 : SYMÉTRIE INVERSE ===\n"
            paires = [(132, 276), (276, 348), (348, 132)]
            for p, q in paires:
                m_pq = signatures[(p, q)].most_common(1)[0][0]
                m_qp = signatures[(q, p)].most_common(1)[0][0]
                inv_qp = (m_qp[1], m_qp[0])
                status = "✓ MATCH" if m_pq == inv_qp else "× DIFF"
                log += f"{p}↔{q}: {m_pq} vs {m_qp} | {status}\n"
            log += "\n"

        if self.test2_var.get():
            log += "=== TEST 2 : Δ MOYEN vs MOTIF ===\n"
            for p in self.familles:
                for q in self.familles:
                    if signatures[(p, q)]:
                        avg_d = np.mean(deltas_par_trans[(p, q)])
                        top_m = signatures[(p, q)].most_common(1)[0][0]
                        log += f"{p}→{q}: Δm={avg_d:.1f} | Top:{top_m}\n"
            log += "\n"

        if self.test3_var.get():
            log += "=== TEST 3 : HIÉRARCHIE (RANGS) ===\n"
            for p, q in [(132, 276), (276, 348), (348, 132)]:
                log += f"Transition {p}→{q} :\n"
                ranks = signatures[(p, q)].most_common(3)
                for i, (m, c) in enumerate(ranks):
                    log += f" R{i+1}: {m} ({c} occ.)\n"
            log += "\n"

        self.result_text.insert(tk.END, log)

    def mettre_a_jour_graphique(self):
        if self.df is None: return
        
        signatures, deltas_par_trans = self.analyser_signatures()
        self.executer_tests_logiques(signatures, deltas_par_trans)

        # Nettoyage du graphique précédent
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        fig = plt.figure(figsize=(12, 10))
        grid = plt.GridSpec(2, 2, wspace=0.3, hspace=0.4)

        # 1. Matrice des Signatures
        ax_mat = fig.add_subplot(grid[0, 0])
        matrix_counts = [[sum(signatures[(p, q)].values()) for q in self.familles] for p in self.familles]
        ax_mat.imshow(matrix_counts, cmap='YlGnBu')
        ax_mat.set_xticks([0,1,2]); ax_mat.set_yticks([0,1,2])
        ax_mat.set_xticklabels(self.familles); ax_mat.set_yticklabels(self.familles)
        ax_mat.set_title("Signatures Rythmiques (Top Motif)")
        
        for i, p in enumerate(self.familles):
            for j, q in enumerate(self.familles):
                top_m = signatures[(p, q)].most_common(1)[0][0]
                ax_mat.text(j, i, f"{top_m}", ha="center", va="center", fontweight='bold', fontsize=8)

        # 2. Roue des Transitions
        ax_graph = fig.add_subplot(grid[0, 1])
        G = nx.DiGraph()
        pos = {132: (0, 1), 276: (0.86, -0.5), 348: (-0.86, -0.5)}
        for u in self.familles:
            for v in self.familles:
                if u != v: G.add_edge(u, v, weight=sum(signatures[(u, v)].values()))
        
        nx.draw_networkx_nodes(G, pos, node_size=2500, node_color='lightblue', node_shape='s', ax=ax_graph)
        nx.draw_networkx_labels(G, pos, {n: f"F.{n}" for n in self.familles}, font_weight='bold', ax=ax_graph)
        for u, v, d in G.edges(data=True):
            nx.draw_networkx_edges(G, pos, edgelist=[(u,v)], width=d['weight']/2000, arrowsize=20, 
                                   connectionstyle='arc3,rad=0.2', ax=ax_graph)
        ax_graph.axis('off')
        ax_graph.set_title("Dynamique de Rotation G3")

        # 3. Distribution des Deltas par Famille
        ax_dist = fig.add_subplot(grid[1, :])
        data_to_plot = [self.df[self.df['fam_p'] == f]['delta'] for f in self.familles]
        ax_dist.boxplot(data_to_plot, labels=self.familles, vert=False, patch_artist=True)
        ax_dist.set_title("Dispersion des Deltas par Famille de départ")
        ax_dist.set_xlabel("Valeur du Delta")

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppG3(root)
    root.mainloop()
