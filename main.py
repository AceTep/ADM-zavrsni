import sys
import pandas as pd
import os
import networkx as nx
import matplotlib.pyplot as plt

# Otvori tekstualnu datoteku za pisanje izlaza
output_file_path = "output.txt"
output_file = open(output_file_path, "w")
sys.stdout = output_file

# Učitaj skup podataka
df = pd.read_csv("Cs_5DIZ_17_07_2023_10_27_A4.csv")

# Definiraj vremenske intervale u frejmovima
interval_length_frames = 240  # frejmovi (ekvivalentno 10 sekundi)
interval_shift_frames = 120    # frejmovi (ekvivalentno 5 sekundi)

# Stvori direktorij za spremanje vizualizacija ako ne postoji
visualization_dir = "vizualizacije"
os.makedirs(visualization_dir, exist_ok=True)

# Inicijaliziraj brojač
interval_counter = 0

# Inicijaliziraj listu za pohranu rezultata
results = []

for start_frame in range(0, df['time_fps'].max(), interval_shift_frames):
    end_frame = start_frame + interval_length_frames
    
    # Filtriraj interakcije unutar trenutnog intervala
    interval_interactions = df[(df['time_fps'] >= start_frame) & (df['time_fps'] < end_frame)]
    
    # Konstruiraj mrežu za trenutni interval
    G = nx.from_pandas_edgelist(interval_interactions, 'source', 'target')
    
    # Izračunaj mrežne metrike
    metrics = {
        'Degree Centrality': nx.degree_centrality(G),
        'Betweenness Centrality': nx.betweenness_centrality(G),
        'Closeness Centrality': nx.closeness_centrality(G)
    }
    
    # Provjeri ima li graf bridova prije izračuna koeficijenta klasteriranja
    if G.number_of_edges() > 0:
        metrics['Clustering Coefficient'] = nx.average_clustering(G)
    else:
        metrics['Clustering Coefficient'] = 0.0  # Ako nema bridova postavljanje koeficijenta klasteriranja na 0
        
    # Inkrementiraj brojač intervala
    interval_counter += 1
    
    # Provjeri jesu li neke mrežne metrike prazne
    if any(len(metric) == 0 for metric in metrics.values() if isinstance(metric, dict)):
        print(f"Interval {interval_counter}: Nema pronađenih interakcija za [{start_frame}, {end_frame})")
    else:
        # Ispiši mrežne metrike
        print(f"Interval {interval_counter} Metrike za [{start_frame}, {end_frame}):")
        for metric_name, metric_value in metrics.items():
            print(f"{metric_name}: {metric_value}")
        
        
        # Stvori raspored pomoću 'spring' algoritma za mrežu
        pos = nx.spring_layout(G)
        
        # Nacrtaj mrežu
        plt.figure(figsize=(8, 8))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500, edge_color='gray', linewidths=1, font_size=10)
        plt.title(f"Mreža za vremenski interval [{start_frame}, {end_frame})")
        
        # Spremi vizualizaciju u datoteku
        plt.savefig(f"{visualization_dir}/vizualizacija_{interval_counter}.png")
        
        # Zatvori trenutnu sliku kako bi oslobodila memoriju
        plt.close()
        
        print(f"Vizualizacija spremljena u {visualization_dir}/vizualizacija_{interval_counter}.png")
        
        output_file.write('\n')

        # Dodaj rezultate u listu
        results.append({
            'Interval': f"[{start_frame}, {end_frame})",
            **metrics,
            'Vizualizacija': f"{visualization_dir}/vizualizacija_{interval_counter}.png"
        })

# Pretvori listu rezultata u DataFrame
df_results = pd.DataFrame(results)

# Ispiši DataFrame
print(df_results)

# Zatvori izlaznu datoteku
output_file.close()

# Vrati stdout u njegovo izvorno stanje
sys.stdout = sys.__stdout__

print(f"Svi podaci spremljeni su u {output_file_path}")
