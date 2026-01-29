import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import math
import csv
import time


try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    Figure = None



try:
    import pandas as pd
except ImportError:
    pd = None

# ============================
#  FILTRE ANGULAIRE
# ============================

ANGLE_348_RESIDU = 29  # résidu modulo 30 pour l’angle 348°

def is_angle_348(n):
    return n % 30 == ANGLE_348_RESIDU

def debut_corrige_348(start):
    """Plus petit entier >= start dans l’angle 348°."""
    n = start
    while not is_angle_348(n):
        n += 1
    return n

# ============================
#  CACHE DE PRIMALITÉ
# ============================

prime_cache = {}

def is_prime(n):
    if n in prime_cache:
        return prime_cache[n]
    if n < 2:
        prime_cache[n] = False
        return False
    if n % 2 == 0:
        prime_cache[n] = (n == 2)
        return prime_cache[n]
    r = int(math.isqrt(n))
    for f in range(3, r + 1, 2):
        if n % f == 0:
            prime_cache[n] = False
            return False
    prime_cache[n] = True
    return True

# ============================
#  GRAMMAIRES G1 / G2 / G3
# ============================

G1 = [1, 2, 3, 4, 5, 7, 8, 9, 12, 13, 14, 15]

G2_2uplets = [
    (1,8), (8,5), (5,1),
    (2,13), (13,2),
    (7,4), (4,7),
    (1,12), (12,1),
    (9,3), (3,8),
    (5,4), (4,9),
    (8,13), (13,7),
]

G3_A = [3, 4, 6, 9, 11, 14, 15, 16, 18, 19, 20, 21, 22]
G3_B = [24, 28, 29, 30, 31, 34, 36, 37, 42, 44]
G3_C = [
    [20,29,3], [19,30], [4,11], [15,30],
    [21,21,23,11,3,3,4,4,24,3,22],
    [15,9], [4,3,14], [9,44], [19,3,18],
    [26,15,15,3,10,16], [42,6,22], [17,3],
    [11,10], [22,9,4,14], [3,44,17],
    [20,14], [24,18,20], [27,34], [18,19,30],
    [32,10,9], [24,71,17,4], [15,19], [3,3],
    [37,18,36,22], [34,21], [4,14], [4,21,4],
    [15,4,31,11], [19,36,14,6,15],
]

# ============================
#  GÉNÉRATEUR SG GRAMMATICAL
# ============================

def generate_sg_grammar_strict(start, end, count, rng,
                               use_g1=True, use_g2=True, use_g3=True,
                               progress_callback=None, time_callback=None,
                               timeout_seconds=120):

    if not (use_g1 or use_g2 or use_g3):
        return [], []

    # Trouver un premier SG dans l’angle 348°
    p = None
    for n in range(start, end + 1):
        if is_angle_348(n) and is_prime(n) and is_prime(2*n + 1):
            p = n
            break
    if p is None:
        return [], []

    sg = [p]
    gaps = []
    last_k = None
    last_was_anomaly = False

    start_time = time.time()
    attempts = 0

    while len(sg) < count:

        if time.time() - start_time > timeout_seconds:
            break

        attempts += 1

        if progress_callback:
            progress_callback(len(sg), count)

        if time_callback and attempts % 1000 == 0:
            elapsed = time.time() - start_time
            if len(sg) > 1:
                rate = elapsed / (len(sg) - 1)
                remaining = (count - len(sg)) * rate
            else:
                remaining = float("nan")
            time_callback(elapsed, remaining)

        r = rng.random()
        k = None

        # G3 anomalies
        if use_g3 and not last_was_anomaly:
            if r < 0.001:
                seq = rng.choice(G3_C)
                for k_seq in seq:
                    candidate = p + 30*k_seq
                    if candidate <= end and is_angle_348(candidate):
                        if is_prime(candidate) and is_prime(2*candidate + 1):
                            sg.append(candidate)
                            gaps.append(k_seq)
                            p = candidate
                            last_k = k_seq
                            last_was_anomaly = True
                continue
            elif r < 0.01:
                k = rng.choice(G3_B)
                last_was_anomaly = True
            elif r < 0.03:
                k = rng.choice(G3_A)
                last_was_anomaly = True

        # G1 squelette
        if k is None:
            k = rng.choice(G1) if use_g1 else rng.randint(1, 40)
            last_was_anomaly = False

        # G2 motifs internes
        if use_g2 and last_k is not None:
            if (last_k, k) not in G2_2uplets:
                if rng.random() > 0.50:
                    continue

        candidate = p + 30*k
        if candidate > end:
            continue

        if not is_angle_348(candidate):
            continue

        if is_prime(candidate) and is_prime(2*candidate + 1):
            sg.append(candidate)
            gaps.append(k)
            p = candidate
            last_k = k

    return sg, gaps

# ============================
#  GÉNÉRATEUR SAFE PRIMES
# ============================

def generate_safe_primes_grammar(start, end, count_safe, rng,
                                 use_g1=True, use_g2=True, use_g3=True,
                                 progress_callback=None, time_callback=None,
                                 timeout_seconds=120):

    if count_safe <= 0:
        return [], []

    target_sg = max(count_safe * 5, count_safe + 10)

    sg_list, gaps = generate_sg_grammar_strict(
        start, end, target_sg, rng,
        use_g1=use_g1, use_g2=use_g2, use_g3=use_g3,
        progress_callback=progress_callback,
        time_callback=time_callback,
        timeout_seconds=timeout_seconds
    )

    safe_primes = []
    sg_used = []

    start_time = time.time()

    for p in sg_list:

        if time.time() - start_time > timeout_seconds:
            break

        if progress_callback:
            progress_callback(len(safe_primes), count_safe)

        if not is_angle_348(p):
            continue

        q = 2*p + 1

        if not is_angle_348(q):
            continue

        if is_prime(q):
            safe_primes.append(q)
            sg_used.append(p)

            if time_callback and len(safe_primes) > 0:
                elapsed = time.time() - start_time
                rate = elapsed / len(safe_primes)
                remaining = (count_safe - len(safe_primes)) * rate
                time_callback(elapsed, remaining)

            if len(safe_primes) >= count_safe:
                break

    return safe_primes, sg_used

# ============================
#  MODÈLE HASARD
# ============================

def generate_random_model(start, end, count, rng=None):
    if rng is None:
        rng = random.Random()

    sg_list = []
    trials = 0

    while len(sg_list) < count and trials < count * 200:
        n = rng.randint(start, end)
        if is_angle_348(n) and is_prime(n) and is_prime(2*n + 1):
            if n not in sg_list:
                sg_list.append(n)
        trials += 1

    sg_list.sort()
    gaps = [(sg_list[i] - sg_list[i-1]) // 30 for i in range(1, len(sg_list))]
    return sg_list, gaps

# ============================
#  RECOMMANDATION SG
# ============================

def recommend_sg_max(interval_size, use_g2, use_g3):
    base = interval_size / 2000
    if use_g2:
        base *= 0.7
    if use_g3:
        base *= 0.5
    return max(5, int(base))

# ============================
#  INTERFACE TKINTER
# ============================

class SGApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Générateur SG (grammaire) + Safe Primes + Mode TURBO")
        self.geometry("1000x850")

        self.turbo_mode = False

        # Données internes
        self.sg_grammar = []
        self.gaps_grammar = []
        self.sg_random = []
        self.gaps_random = []
        self.safe_primes = []
        self.safe_sg = []

        self.start_time = None

        self._build_widgets()

    # ------------------------------------------------------------
    #  CONSTRUCTION DE L’INTERFACE
    # ------------------------------------------------------------
    # ------------------------------------------------------------
    #  GRAPHIQUES : histogrammes des écarts
    # ------------------------------------------------------------
    def update_plots(self):
        # Si matplotlib indisponible
        if Figure is None:
            messagebox.showwarning("Graphiques", "matplotlib n'est pas installé. Graphiques indisponibles.")
            return

        # Nettoyer l'onglet
        for child in self.frm_plots.winfo_children():
            child.destroy()

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        gaps_g = self.gaps_grammar
        gaps_r = self.gaps_random

        if gaps_g:
            ax.hist(gaps_g, bins=20, alpha=0.6, label="Grammaire")
        if gaps_r:
            ax.hist(gaps_r, bins=20, alpha=0.6, label="Hasard")

        ax.set_title("Distribution des écarts k")
        ax.set_xlabel("k")
        ax.set_ylabel("Fréquence")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.frm_plots)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ------------------------------------------------------------
    #  ANALYSE COMPARATIVE SG / SAFE / HASARD
    # ------------------------------------------------------------
    def update_analysis(self):
        self.analysis_text.config(state="normal")
        self.analysis_text.delete("1.0", tk.END)

        # SG grammaticaux
        sg_g = self.sg_grammar
        gaps_g = self.gaps_grammar

        # SG hasard
        sg_r = self.sg_random
        gaps_r = self.gaps_random

        # Safe primes
        safe_q = self.safe_primes
        safe_p = self.safe_sg

        def mean(xs):
            return sum(xs) / len(xs) if xs else float("nan")

        self.analysis_text.insert(tk.END, "=== Analyse comparative ===\n\n")

        self.analysis_text.insert(tk.END, f"SG grammaticaux : {len(sg_g)}\n")
        self.analysis_text.insert(tk.END, f"SG hasard       : {len(sg_r)}\n")
        self.analysis_text.insert(tk.END, f"Safe primes     : {len(safe_q)}\n\n")

        self.analysis_text.insert(tk.END, "Moyennes des écarts k :\n")
        self.analysis_text.insert(tk.END, f"  Grammaire : {mean(gaps_g):.3f}\n")
        self.analysis_text.insert(tk.END, f"  Hasard    : {mean(gaps_r):.3f}\n\n")

        # SG grammaticaux qui ne produisent pas de safe prime
        sg_g_set = set(sg_g)
        safe_p_set = set(safe_p)
        sg_without_safe = sorted(sg_g_set - safe_p_set)

        self.analysis_text.insert(tk.END, "SG grammaticaux sans safe prime associé :\n")
        if sg_without_safe:
            self.analysis_text.insert(tk.END, f"{len(sg_without_safe)} éléments :\n")
            self.analysis_text.insert(tk.END, f"{sg_without_safe}\n\n")
        else:
            self.analysis_text.insert(tk.END, "Tous les SG grammaticaux produisent un safe prime.\n\n")

        # SG utilisés pour safe primes mais absents de la chaîne grammaticale principale
        extra_safe_p = sorted(safe_p_set - sg_g_set)
        self.analysis_text.insert(tk.END, "SG utilisés pour safe primes mais absents de la chaîne grammaticale principale :\n")
        if extra_safe_p:
            self.analysis_text.insert(tk.END, f"{len(extra_safe_p)} éléments :\n")
            self.analysis_text.insert(tk.END, f"{extra_safe_p}\n\n")
        else:
            self.analysis_text.insert(tk.END, "Tous les SG des safe primes appartiennent à la chaîne grammaticale.\n\n")

        self.analysis_text.config(state="disabled")



    def _build_widgets(self):

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        
        # Onglet 1 : laboratoire
        frm = ttk.Frame(notebook)
        notebook.add(frm, text="Laboratoire SG")
        
        # Onglet 2 : explication mathématique
        self.frm_info = ttk.Frame(notebook)
        notebook.add(self.frm_info, text="Explication mathématique")
        
        # Onglet 3 : analyse
        self.frm_analysis = ttk.Frame(notebook)
        notebook.add(self.frm_analysis, text="Analyse")
        
        # Onglet 4 : graphiques
        self.frm_plots = ttk.Frame(notebook)
        notebook.add(self.frm_plots, text="Graphiques")
    

        # (le reste de _build_widgets continue comme avant, mais en utilisant frm comme conteneur principal)

        # Barre de progression
        self.progress = ttk.Progressbar(frm, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=5)

        self.status = ttk.Label(frm, text="Prêt.")
        self.status.pack(fill="x")

        # Paramètres
        params = ttk.LabelFrame(frm, text="Paramètres")
        params.pack(fill="x", pady=5)

        # Intervalles logiques
        self.interval_choice = tk.StringVar(value="manuel")

        ttk.Radiobutton(params, text="Petit (0 → 20 000)", variable=self.interval_choice,
                        value="petit", command=self.update_interval).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(params, text="Moyen (0 → 50 000)", variable=self.interval_choice,
                        value="moyen", command=self.update_interval).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(params, text="Grand (0 → 100 000)", variable=self.interval_choice,
                        value="grand", command=self.update_interval).grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(params, text="Très grand (0 → 200 000)", variable=self.interval_choice,
                        value="tresgrand", command=self.update_interval).grid(row=3, column=0, sticky="w")
        ttk.Radiobutton(params, text="Manuel", variable=self.interval_choice,
                        value="manuel", command=self.update_interval).grid(row=4, column=0, sticky="w")

        ttk.Label(params, text="Début :").grid(row=0, column=1, sticky="w")
        self.entry_start = ttk.Entry(params, width=12)
        self.entry_start.grid(row=0, column=2, padx=5)

        ttk.Label(params, text="Fin :").grid(row=1, column=1, sticky="w")
        self.entry_end = ttk.Entry(params, width=12)
        self.entry_end.grid(row=1, column=2, padx=5)

        ttk.Label(params, text="Nombre SG à générer :").grid(row=2, column=1, sticky="w")
        self.entry_count = ttk.Entry(params, width=8)
        self.entry_count.grid(row=2, column=2, padx=5)

        ttk.Label(params, text="Nombre safe primes :").grid(row=3, column=1, sticky="w")
        self.entry_safe = ttk.Entry(params, width=8)
        self.entry_safe.grid(row=3, column=2, padx=5)

        # Grammaires
        grammar_frame = ttk.LabelFrame(frm, text="Grammaires actives")
        grammar_frame.pack(fill="x", pady=5)

        self.use_g1 = tk.BooleanVar(value=True)
        self.use_g2 = tk.BooleanVar(value=True)
        self.use_g3 = tk.BooleanVar(value=True)

        ttk.Checkbutton(grammar_frame, text="G1 (squelette)", variable=self.use_g1,
                        command=self.update_sg_recommendation).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(grammar_frame, text="G2 (motifs)", variable=self.use_g2,
                        command=self.update_sg_recommendation).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(grammar_frame, text="G3 (anomalies)", variable=self.use_g3,
                        command=self.update_sg_recommendation).grid(row=0, column=2, sticky="w")

        # Bouton TURBO
        self.btn_turbo = ttk.Button(grammar_frame, text="Activer mode TURBO", command=self.toggle_turbo)
        self.btn_turbo.grid(row=1, column=0, columnspan=3, pady=5)

        # Boutons d’action
        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=5)

        self.btn_run = ttk.Button(btns, text="Générer SG (grammaire)", command=self.on_run_sg)
        self.btn_run.pack(side="left", padx=5)

        self.btn_safe = ttk.Button(btns, text="Générer safe primes", command=self.on_run_safe)
        self.btn_safe.pack(side="left", padx=5)

        self.btn_plots = ttk.Button(btns, text="Mettre à jour les graphiques", command=self.update_plots)
        self.btn_plots.pack(side="left", padx=5)

        self.btn_export_tex = ttk.Button(btns, text="Exporter en .tex", command=self.on_export_tex)
        self.btn_export_tex.pack(side="left", padx=5)
        
        self.btn_export = ttk.Button(btns, text="Exporter (CSV/Excel)", command=self.on_export)
        self.btn_export.pack(side="left", padx=5)

        self.btn_reset = ttk.Button(btns, text="Reset", command=self.on_reset)
        self.btn_reset.pack(side="left", padx=5)

        self.btn_quit = ttk.Button(btns, text="Quitter", command=self.destroy)
        self.btn_quit.pack(side="right", padx=5)
        

    

        # Zone de texte monospace
        text_frame = ttk.Frame(frm)
        text_frame.pack(fill="both", expand=True)

        self.text = tk.Text(
            text_frame,
            wrap="word",
            font=("Monospace", 11)
        )
        scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)

        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")


        # Onglet Explication mathématique
        info_text = tk.Text(
            self.frm_info,
            wrap="word",
            font=("Monospace", 11),
            padx=10,
            pady=10
        )
        # info_scroll = ttk.Scrollbar(self.frm_info, orient="vertical", command=info_text.yview)
        # info_text.configure(yscrollcommand=info_scroll.set)
        
        # info_text.pack(side="left", fill="both", expand=True)
        # info_scroll.pack(side="right", fill="y")
        
        explication = """
        # === explication mathématique ===
        
        # 1. sophie germain (sg)
        # un nombre p est dit sophie germain si p est premier et si q = 2p + 1 est aussi premier.
        # le nombre q est alors appelé "safe prime".
        
        # 2. pourquoi l’angle 348° (mod 30)
        # les nombres premiers > 5 sont tous dans les résidus {1, 7, 11, 13, 17, 19, 23, 29} modulo 30.
        # les sg réels observés dans les grands intervalles se concentrent presque exclusivement
        # dans le résidu 29 mod 30, que nous appelons "angle 348°".
        
        # 3. structure grammaticale g1 / g2 / g3
        # g1 : squelette — écarts k fréquents et réguliers.
        # g2 : motifs internes — transitions (k1, k2) privilégiées.
        # g3 : anomalies — séquences rares mais réelles, observées dans les données.
        
        # la grammaire simule la dynamique interne des sg réels.
        
        # 4. modèle grammatical vs modèle hasard
        # le modèle grammatical produit une chaîne dense, cohérente, avec des écarts k faibles.
        # le modèle hasard produit des sg rares, dispersés, avec des écarts k très grands.
        
        # 5. safe primes
        # chaque sg p génère un safe prime q = 2p + 1.
        # le générateur safe primes utilise un filtrage supplémentaire pour sélectionner les p
        # qui produisent un q premier dans l’angle 348°.
        # """
        
        #info_text.insert("1.0", explication)
        #info_text.config(state="disabled")
        # ============================
        #  Onglet Explication mathématique
        # ============================
        info_text = tk.Text(
            self.frm_info,
            wrap="word",
            font=("Monospace", 11),
            padx=10,
            pady=10
        )
        info_scroll = ttk.Scrollbar(self.frm_info, orient="vertical", command=info_text.yview)
        info_text.configure(yscrollcommand=info_scroll.set)

        info_text.pack(side="left", fill="both", expand=True)
        info_scroll.pack(side="right", fill="y")

        explication = """
=== Explication mathématique ===

1. Nombres de Sophie Germain (SG)
Un nombre p est dit Sophie Germain si p est premier et si q = 2p + 1 est aussi premier.
Le nombre q est alors appelé "safe prime".

2. Angle 348° (mod 30)
Les nombres premiers > 5 appartiennent aux résidus {1, 7, 11, 13, 17, 19, 23, 29} modulo 30.
Les SG observés empiriquement se concentrent presque exclusivement dans le résidu 29 mod 30,
que nous appelons "angle 348°".

3. Grammaires G1 / G2 / G3
G1 : squelette — écarts k fréquents et réguliers.
G2 : motifs internes — transitions (k1, k2) privilégiées.
G3 : anomalies — séquences rares mais réelles, observées dans les données.

La grammaire simule la dynamique interne des SG réels.

4. Modèle grammatical vs modèle hasard
Le modèle grammatical produit une chaîne dense, cohérente, avec des écarts k faibles.
Le modèle hasard produit des SG rares, dispersés, avec des écarts k très grands.

5. Safe primes
Chaque SG p génère un safe prime q = 2p + 1.
Le générateur de safe primes applique un filtrage supplémentaire pour sélectionner les p
qui produisent un q premier dans l’angle 348°.
"""
        info_text.insert("1.0", explication)
        info_text.config(state="disabled")
        # ============================
        #  Onglet Analyse
        # ============================
        self.analysis_text = tk.Text(
            self.frm_analysis,
            wrap="word",
            font=("Monospace", 11),
            padx=10,
            pady=10
        )
        analysis_scroll = ttk.Scrollbar(self.frm_analysis, orient="vertical", command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scroll.set)

        self.analysis_text.pack(side="left", fill="both", expand=True)
        analysis_scroll.pack(side="right", fill="y")
        
        
    
    # ------------------------------------------------------------
    #  MODE TURBO
    # ------------------------------------------------------------
    def toggle_turbo(self):
        self.turbo_mode = not self.turbo_mode

        if self.turbo_mode:
            self.use_g1.set(True)
            self.use_g2.set(False)
            self.use_g3.set(False)
            self.btn_turbo.config(text="Désactiver mode TURBO")
            self.status.config(text="Mode TURBO activé : G1 seul.")
        else:
            self.btn_turbo.config(text="Activer mode TURBO")
            self.status.config(text="Mode TURBO désactivé.")

        self.update_sg_recommendation()

    # ------------------------------------------------------------
    #  INTERVALLES LOGIQUES
    # ------------------------------------------------------------
    def update_interval(self):
        choice = self.interval_choice.get()

        self.entry_start.config(state="normal")
        self.entry_end.config(state="normal")

        if choice == "petit":
            self.entry_start.delete(0, tk.END)
            self.entry_end.delete(0, tk.END)
            self.entry_start.insert(0, "0")
            self.entry_end.insert(0, "20000")
            self.entry_start.config(state="disabled")
            self.entry_end.config(state="disabled")

        elif choice == "moyen":
            self.entry_start.delete(0, tk.END)
            self.entry_end.delete(0, tk.END)
            self.entry_start.insert(0, "0")
            self.entry_end.insert(0, "50000")
            self.entry_start.config(state="disabled")
            self.entry_end.config(state="disabled")

        elif choice == "grand":
            self.entry_start.delete(0, tk.END)
            self.entry_end.delete(0, tk.END)
            self.entry_start.insert(0, "0")
            self.entry_end.insert(0, "100000")
            self.entry_start.config(state="disabled")
            self.entry_end.config(state="disabled")

        elif choice == "tresgrand":
            self.entry_start.delete(0, tk.END)
            self.entry_end.delete(0, tk.END)
            self.entry_start.insert(0, "0")
            self.entry_end.insert(0, "200000")
            self.entry_start.config(state="disabled")
            self.entry_end.config(state="disabled")

        self.update_sg_recommendation()

    # ------------------------------------------------------------
    #  RECOMMANDATION SG / SAFE
    # ------------------------------------------------------------
    def update_sg_recommendation(self):
        try:
            start = int(self.entry_start.get())
            end = int(self.entry_end.get())
        except ValueError:
            return

        interval_size = max(1, end - start)

        sg_max = recommend_sg_max(interval_size, self.use_g2.get(), self.use_g3.get())

        self.entry_count.delete(0, tk.END)
        self.entry_count.insert(0, str(sg_max))

        self.entry_safe.delete(0, tk.END)
        self.entry_safe.insert(0, str(min(sg_max, 100)))

    # ------------------------------------------------------------
    #  GÉNÉRATION SG (GRAMMAIRE)
    # ------------------------------------------------------------
    def on_run_sg(self):
        try:
            start = int(self.entry_start.get())
            end = int(self.entry_end.get())
            count = int(self.entry_count.get())
        except ValueError:
            messagebox.showerror("Erreur", "Les paramètres doivent être des entiers.")
            return

        if start >= end:
            messagebox.showerror("Erreur", "Début doit être < Fin.")
            return

        if not (self.use_g1.get() or self.use_g2.get() or self.use_g3.get()):
            messagebox.showerror("Erreur", "Au moins une grammaire doit être cochée.")
            return

        if not self.check_feasibility(start, end, count, 0):
            return

        self.status.config(text="Génération SG…")
        self.progress["value"] = 0

        rng = random.Random()
        self.start_time = time.time()

        self.sg_grammar, self.gaps_grammar = generate_sg_grammar_strict(
            start, end, count, rng,
            use_g1=self.use_g1.get(),
            use_g2=self.use_g2.get(),
            use_g3=self.use_g3.get(),
            progress_callback=self.update_progress,
            time_callback=self.update_time_estimate
        )

        self.sg_random, self.gaps_random = generate_random_model(
            start, end, len(self.sg_grammar), rng
        )

        self.safe_primes = []
        self.safe_sg = []

        self._display_results_sg()
        self.update_analysis()


    # ------------------------------------------------------------
    #  GÉNÉRATION SAFE PRIMES
    # ------------------------------------------------------------
    def on_run_safe(self):
        try:
            start = int(self.entry_start.get())
            end = int(self.entry_end.get())
            count_safe = int(self.entry_safe.get())
        except ValueError:
            messagebox.showerror("Erreur", "Les paramètres doivent être des entiers.")
            return

        if start >= end:
            messagebox.showerror("Erreur", "Début doit être < Fin.")
            return

        if not (self.use_g1.get() or self.use_g2.get() or self.use_g3.get()):
            messagebox.showerror("Erreur", "Au moins une grammaire doit être cochée.")
            return

        if not self.check_feasibility(start, end, 0, count_safe):
            return

        self.status.config(text="Génération safe primes…")
        self.progress["value"] = 0

        rng = random.Random()
        self.start_time = time.time()

        self.safe_primes, self.safe_sg = generate_safe_primes_grammar(
            start, end, count_safe, rng,
            use_g1=self.use_g1.get(),
            use_g2=self.use_g2.get(),
            use_g3=self.use_g3.get(),
            progress_callback=self.update_progress,
            time_callback=self.update_time_estimate
        )

        self._display_results_safe()
        self.update_analysis()

    # ------------------------------------------------------------
    #  AFFICHAGE SG
    # ------------------------------------------------------------
    def _display_results_sg(self):

        start = int(self.entry_start.get())
        end = int(self.entry_end.get())
        start_corrige = debut_corrige_348(start)

        grammaires = []
        if self.use_g1.get(): grammaires.append("G1")
        if self.use_g2.get(): grammaires.append("G2")
        if self.use_g3.get(): grammaires.append("G3")
        grammaires_str = ", ".join(grammaires)

        self.text.insert(tk.END, "\n=== Modèle grammatical (SG) ===\n")
        self.text.insert(tk.END, f"Grammaire Active = {grammaires_str}\n")
        self.text.insert(tk.END, f"Nombre de Début = {start}\n")
        self.text.insert(tk.END, f"Nombre Début corrigé 348° = {start_corrige}\n")
        self.text.insert(tk.END, f"Nombre Fin = {end}\n")
        self.text.insert(tk.END, "==============================\n")
        self.text.insert(tk.END, f"Nombre de SG générés : {len(self.sg_grammar)}\n")
        self.text.insert(tk.END, f"SG : {self.sg_grammar}\n")
        self.text.insert(tk.END, f"Écarts k : {self.gaps_grammar}\n\n")

        self.text.insert(tk.END, "=== Modèle hasard (SG) ===\n")
        self.text.insert(tk.END, f"Nombre de SG trouvés : {len(self.sg_random)}\n")
        self.text.insert(tk.END, f"SG : {self.sg_random}\n")
        self.text.insert(tk.END, f"Écarts k : {self.gaps_random}\n\n")

        def mean(xs):
            return sum(xs) / len(xs) if xs else float("nan")

        m_g = mean(self.gaps_grammar)
        m_r = mean(self.gaps_random)

        self.text.insert(tk.END, "=== Statistiques comparatives (SG) ===\n")
        self.text.insert(tk.END, f"Moyenne des écarts (grammaire) : {m_g:.3f}\n")
        self.text.insert(tk.END, f"Moyenne des écarts (hasard)    : {m_r:.3f}\n\n")

        self.status.config(text="Génération SG terminée.")

    # ------------------------------------------------------------
    #  AFFICHAGE SAFE PRIMES
    # ------------------------------------------------------------
    def _display_results_safe(self):

        start = int(self.entry_start.get())
        end = int(self.entry_end.get())
        start_corrige = debut_corrige_348(start)

        grammaires = []
        if self.use_g1.get(): grammaires.append("G1")
        if self.use_g2.get(): grammaires.append("G2")
        if self.use_g3.get(): grammaires.append("G3")
        grammaires_str = ", ".join(grammaires)

        self.text.insert(tk.END, "\n=== Safe primes générés (q = 2p+1) ===\n")
        self.text.insert(tk.END, f"Grammaire Active = {grammaires_str}\n")
        self.text.insert(tk.END, f"Nombre de Début = {start}\n")
        self.text.insert(tk.END, f"Nombre Début corrigé 348° = {start_corrige}\n")
        self.text.insert(tk.END, f"Nombre Fin = {end}\n")
        self.text.insert(tk.END, f"Nombre de safe primes : {len(self.safe_primes)}\n")
        self.text.insert(tk.END, f"Safe primes q : {self.safe_primes}\n")
        self.text.insert(tk.END, f"SG associés p : {self.safe_sg}\n\n")

        self.status.config(text="Génération safe primes terminée.")

    # ------------------------------------------------------------
    #  PROGRESSION + TEMPS RESTANT
    # ------------------------------------------------------------
    def update_progress(self, current, total):
        pct = int((current / total) * 100) if total > 0 else 0
        self.progress["value"] = pct
        self.update_idletasks()

    def update_time_estimate(self, elapsed, remaining):
        self.status.config(text=f"Génération… max 120 sec. écoulé : {elapsed:.1f} s")
        self.update_idletasks()


    # ------------------------------------------------------------
    #  AVERTISSEMENT AUTOMATIQUE
    # ------------------------------------------------------------
    def check_feasibility(self, start, end, count_sg, count_safe):
        interval = end - start

        sg_max = recommend_sg_max(interval, self.use_g2.get(), self.use_g3.get())
        if count_sg > sg_max:
            messagebox.showwarning(
                "Intervalle insuffisant",
                f"Trop de SG demandés ({count_sg}) pour l’intervalle {interval}.\n"
                f"Maximum recommandé : {sg_max}.\n\n"
                "Génération annulée."
            )
            return False

        if count_safe > sg_max:
            messagebox.showwarning(
                "Intervalle insuffisant",
                f"Trop de safe primes demandés ({count_safe}).\n"
                f"Intervalle trop petit.\n\n"
                "Génération annulée."
            )
            return False

        return True

    # ------------------------------------------------------------
    #  RESET (efface uniquement la zone texte)
    # ------------------------------------------------------------
    def on_reset(self):
        self.text.delete("1.0", tk.END)
        self.status.config(text="Résultats effacés.")

    # ------------------------------------------------------------
    #  EXPORT CSV / EXCEL
    # ------------------------------------------------------------
    def on_export(self):
        if not (self.sg_grammar or self.safe_primes):
            messagebox.showwarning("Export", "Aucune donnée à exporter.")
            return

        filetypes = [("CSV", "*.csv")]
        if pd is not None:
            filetypes.append(("Excel", "*.xlsx"))

        filename = filedialog.asksaveasfilename(
            title="Exporter les résultats",
            defaultextension=".csv",
            filetypes=filetypes
        )
        if not filename:
            return

        max_len = max(
            len(self.sg_grammar),
            len(self.sg_random),
            len(self.safe_primes)
        )

        sg_g = self.sg_grammar + [None] * (max_len - len(self.sg_grammar))
        sg_r = self.sg_random + [None] * (max_len - len(self.sg_random))
        gaps_g = self.gaps_grammar + [None] * (max_len - len(self.gaps_grammar))
        gaps_r = self.gaps_random + [None] * (max_len - len(self.gaps_random))
        safe_q = self.safe_primes + [None] * (max_len - len(self.safe_primes))
        safe_p = self.safe_sg + [None] * (max_len - len(self.safe_sg))

        rows = []
        for i in range(max_len):
            rows.append({
                "SG_grammar": sg_g[i],
                "gap_grammar": gaps_g[i],
                "SG_random": sg_r[i],
                "gap_random": gaps_r[i],
                "safe_prime_q": safe_q[i],
                "safe_prime_p": safe_p[i],
            })

        if filename.endswith(".xlsx") and pd is not None:
            df = pd.DataFrame(rows)
            df.to_excel(filename, index=False)
        else:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

        messagebox.showinfo("Export", f"Résultats exportés vers {filename}")

    # ------------------------------------------------------------
    #  EXPORT LaTeX (.tex)
    # ------------------------------------------------------------
    def on_export_tex(self):
        filename = filedialog.asksaveasfilename(
            title="Exporter en LaTeX",
            defaultextension=".tex",
            filetypes=[("Fichier LaTeX", "*.tex")]
        )
        if not filename:
            return

        # Préparation des données
        sg_g = self.sg_grammar
        gaps_g = self.gaps_grammar
        sg_r = self.sg_random
        gaps_r = self.gaps_random
        safe_q = self.safe_primes
        safe_p = self.safe_sg

        def latex_list(xs):
            return ", ".join(str(x) for x in xs)

        def mean(xs):
            return sum(xs) / len(xs) if xs else float("nan")

        # Contenu LaTeX propre (sans \\ après les titres)
        tex = r"""\documentclass[12pt]{article}
\usepackage{amsmath, amssymb}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{hyperref}
\geometry{margin=1in}

\title{Analyse grammaticale des nombres de Sophie Germain}
\author{Michel Monfette}
\date{\today}

\begin{document}
\maketitle

\section{Paramètres}
Intervalle: """ + f"{self.entry_start.get()} -- {self.entry_end.get()}" + r"""
Grammaires actives: """ + ", ".join(
            g for g, v in [("G1", self.use_g1.get()), ("G2", self.use_g2.get()), ("G3", self.use_g3.get())] if v
        ) + r"""

\section{Modèle grammatical (SG)}
Nombre de SG générés: """ + str(len(sg_g)) + r"""

\subsection*{Liste des SG}
""" + latex_list(sg_g) + r"""

\subsection*{Écarts k}
""" + latex_list(gaps_g) + r"""

Moyenne des écarts: """ + f"{mean(gaps_g):.3f}" + r"""

\section{Modèle hasard (SG)}
Nombre de SG trouvés: """ + str(len(sg_r)) + r"""

\subsection*{Liste des SG}
""" + latex_list(sg_r) + r"""

\subsection*{Écarts k}
""" + latex_list(gaps_r) + r"""

Moyenne des écarts: """ + f"{mean(gaps_r):.3f}" + r"""

\section{Analyse comparative}

\subsection*{SG grammaticaux sans safe prime}
""" + latex_list(sorted(set(sg_g) - set(safe_p))) + r"""

\subsection*{SG safe primes absents de la chaîne grammaticale}
""" + latex_list(sorted(set(safe_p) - set(sg_g))) + r"""

\section{Safe primes}
Nombre de safe primes: """ + str(len(safe_q)) + r"""

\subsection*{Liste des q}
""" + latex_list(safe_q) + r"""

\subsection*{SG associés p}
""" + latex_list(safe_p) + r"""

\section{Graphiques}
\begin{figure}[h!]
\centering
\includegraphics[width=0.9\textwidth]{ecarts_histogramme.png}
\caption{Distribution des écarts k pour le modèle grammatical et le modèle hasard.}
\end{figure}

\newpage
\section*{Explication mathématique}

\subsection*{1. Nombres de Sophie Germain (SG)}
Un nombre $p$ est dit \textbf{Sophie Germain} si $p$ est premier et si $q = 2p + 1$ est aussi premier.
Le nombre $q$ est alors appelé \textit{safe prime}.

\subsection*{2. Angle 348° (mod 30)}
Les nombres premiers $> 5$ appartiennent aux résidus
$\{1, 7, 11, 13, 17, 19, 23, 29\}$ modulo $30$.
Les SG observés empiriquement se concentrent presque exclusivement dans le résidu $29 \bmod 30$,
que nous appelons \textbf{angle 348°}.

\subsection*{3. Grammaires G1 / G2 / G3}
\begin{itemize}
    \item \textbf{G1 : squelette} — écarts $k$ fréquents et réguliers.
    \item \textbf{G2 : motifs internes} — transitions $(k_1, k_2)$ privilégiées.
    \item \textbf{G3 : anomalies} — séquences rares mais réelles, observées dans les données.
\end{itemize}

La grammaire simule la dynamique interne des SG réels.

\subsection*{4. Modèle grammatical vs modèle hasard}
Le modèle grammatical produit une chaîne dense, cohérente, avec des écarts $k$ faibles.\\
Le modèle hasard produit des SG rares, dispersés, avec des écarts $k$ très grands.

\subsection*{5. Safe primes}
Chaque SG $p$ génère un safe prime $q = 2p + 1$.\\
Le générateur de safe primes applique un filtrage supplémentaire pour sélectionner les $p$
qui produisent un $q$ premier dans l’angle $348^\circ$.

\subsection*{Définition}
Un nombre $p$ est dit \textbf{Sophie Germain} si $p$ est premier et si $2p+1$ est premier.

\subsection*{Angle 348°}
Les SG se concentrent dans le résidu $29 \mod 30$, appelé angle $348^\circ$.

\subsection*{Grammaires}
\begin{itemize}
\item G1 : squelette
\item G2 : motifs internes
\item G3 : anomalies
\end{itemize}

\end{document}
"""

        # Écriture du fichier
        with open(filename, "w", encoding="utf-8") as f:
            f.write(tex)

        messagebox.showinfo("Export LaTeX", f"Fichier .tex exporté vers:\n{filename}")

# ============================
#  LANCEMENT DE L’APPLICATION
# ============================

if __name__ == "__main__":
    app = SGApp()
    app.mainloop()
