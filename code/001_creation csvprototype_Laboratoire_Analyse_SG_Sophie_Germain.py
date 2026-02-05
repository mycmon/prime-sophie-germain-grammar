import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

# =============================================================================
# 1. COUCHE SCIENTIFIQUE SG (BACKEND)
# =============================================================================

def est_premier(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

def est_sg(p):
    """Un nombre de Sophie Germain p tel que 2p + 1 est premier."""
    return est_premier(p) and est_premier(2 * p + 1)

def generate_sg(limit_n):
    return [p for p in range(11, limit_n + 1) if est_sg(p)]

def get_famille(p):
    r = p % 30
    if r == 29: return "348"
    if r == 23: return "276"
    if r == 11: return "132"
    return "?"

# =============================================================================
# 2. COUCHE GRAMMAIRE G1 / G2 / G3
# =============================================================================

def classifier_delta(delta):
    """
    G1: Alphabet fondamental {6,12,18,24}
    G2: Briques stables {6,12}
    G3: Anomalies (hors G1)
    """
    g1 = 1 if delta in [6, 12, 18, 24] else 0
    g2 = 1 if delta in [6, 12] else 0
    g3 = 1 if delta not in [6, 12, 18, 24] else 0
    return g1, g2, g3

def detecter_motifs_g2(deltas, taille=2):
    freq = {}
    for i in range(len(deltas) - taille + 1):
        motif = tuple(deltas[i:i+taille])
        freq[motif] = freq.get(motif, 0) + 1
    return freq

# =============================================================================
# 4. INTERFACE GUI (TKINTER)
# =============================================================================

class SGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laboratoire d'Analyse SG - Sophie Germain")
        self.root.geometry("900x750")
        
        # Variables de stockage
        self.sg_list = []
        self.tableau_data = []
        
        self.setup_ui()

    def setup_ui(self):
        # --- BLOC 1 : PARAMÈTRES ---
        frame1 = ttk.LabelFrame(self.root, text=" 1. Paramètres SG ", padding=10)
        frame1.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame1, text="Limite N:").pack(side="left")
        self.ent_n = ttk.Entry(frame1, width=15)
        self.ent_n.insert(0, "10000")
        self.ent_n.pack(side="left", padx=5)
        
        ttk.Button(frame1, text="Générer SG", command=self.action_generer).pack(side="left", padx=5)
        self.lbl_count = ttk.Label(frame1, text="SG trouvés : 0", font=('Helvetica', 9, 'bold'))
        self.lbl_count.pack(side="left", padx=20)

        # --- BLOC 2 & 3 : ANALYSE ---
        mid_frame = ttk.Frame(self.root)
        mid_frame.pack(fill="x", padx=10, pady=5)
        
        frame2 = ttk.LabelFrame(mid_frame, text=" 2. Traitement & Classification ", padding=10)
        frame2.pack(side="left", fill="both", expand=True)
        
        ttk.Button(frame2, text="Tout Calculer", command=self.action_tout_calculer).pack(fill="x", pady=2)
        ttk.Button(frame2, text="Analyser Motifs G2", command=self.action_motifs).pack(fill="x", pady=2)
        
        frame3 = ttk.LabelFrame(mid_frame, text=" 3. Export & CSV ", padding=10)
        frame3.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        ttk.Button(frame3, text="Exporter vers CSV", command=self.action_export).pack(fill="x", pady=2)
        ttk.Button(frame3, text="Effacer Console", command=self.clear_console).pack(fill="x", pady=2)

        # --- BLOC 5 : CONSOLE ---
        frame5 = ttk.LabelFrame(self.root, text=" 5. Console de résultats ", padding=10)
        frame5.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.console = tk.Text(frame5, height=20, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.console.pack(fill="both", expand=True)
        
        scroll = ttk.Scrollbar(self.console, command=self.console.yview)
        self.console.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    # --- LOGIQUE INTERNE ---

    def log(self, message):
        self.console.insert(tk.END, f"> {message}\n")
        self.console.see(tk.END)

    def clear_console(self):
        self.console.delete("1.0", tk.END)

    def action_generer(self):
        try:
            n = int(self.ent_n.get())
            self.sg_list = generate_sg(n)
            self.lbl_count.config(text=f"SG trouvés : {len(self.sg_list)}")
            self.log(f"Génération terminée jusqu'à {n}. {len(self.sg_list)} SG identifiés.")
            if self.sg_list:
                self.log(f"Premier SG : {self.sg_list[0]} | Dernier : {self.sg_list[-1]}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre entier valide.")

    def action_tout_calculer(self):
        if not self.sg_list:
            self.action_generer()
        
        self.tableau_data = []
        g1_count, g2_count, g3_count = 0, 0, 0
        
        for i in range(len(self.sg_list) - 1):
            p = self.sg_list[i]
            q = self.sg_list[i+1]
            delta = q - p
            fam_p = get_famille(p)
            fam_q = get_famille(q)
            g1, g2, g3 = classifier_delta(delta)
            
            g1_count += g1
            g2_count += g2
            g3_count += g3
            
            self.tableau_data.append({
                "n": i, "p": p, "fam_p": fam_p, "q": q, 
                "fam_q": fam_q, "delta": delta, "G1": g1, "G2": g2, "G3": g3
            })
            
            if g3 == 1:
                self.log(f"[ANOMALIE G3] n={i}: {p}({fam_p}) -> {q}({fam_q}) Δ={delta}")
                print(f"[ANOMALIE G3] n={i}: {p}({fam_p}) -> {q}({fam_q}) Δ={delta}")


        self.log("--- Synthèse de la classification ---")
        self.log(f"G1 (Fondamentaux) : {g1_count}")
        self.log(f"G2 (Stables 6/12) : {g2_count}")
        self.log(f"G3 (Anomalies)    : {g3_count}")
        self.log("Tableau structuré construit avec succès.")


    def action_motifs(self):
        if not self.tableau_data:
            self.log("Veuillez d'abord cliquer sur 'Tout Calculer'.")
            return
        
        deltas = [d['delta'] for d in self.tableau_data]
        motifs = detecter_motifs_g2(deltas, 2)
        
        # Tri par fréquence
        sorted_motifs = sorted(motifs.items(), key=lambda x: x[1], reverse=True)
        
        self.log("--- Analyse des motifs G2 (Taille 2) ---")
        for m, f in sorted_motifs[:10]: # Top 10
            self.log(f"Motif {m} : {f} occurrences")

    def action_export(self):
        if not self.tableau_data:
            messagebox.showwarning("Attention", "Aucune donnée à exporter. Calculez d'abord.")
            return
        
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            keys = self.tableau_data[0].keys()
            try:
                with open(filepath, 'w', newline='') as f:
                    dict_writer = csv.DictWriter(f, fieldnames=keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(self.tableau_data)
                self.log(f"Exportation réussie : {os.path.basename(filepath)}")
                messagebox.showinfo("Succès", f"Fichier sauvegardé :\n{filepath}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de l'export : {str(e)}")

# =============================================================================
# LANCEMENT
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SGApp(root)
    root.mainloop()
