import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix

# --- Graphique 1 : Matrice de confusion ---
cm = np.array([[84, 16], [2, 48]])
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Légitime (0)', 'Fraude (1)'], 
            yticklabels=['Légitime (0)', 'Fraude (1)'])
plt.title('Matrice de confusion (Modèle M1, seuil 0.26)')
plt.ylabel('Vérité terrain')
plt.xlabel('Prédiction')
plt.tight_layout()
plt.savefig('slide_matrice_confusion.png', dpi=300)
plt.close()

# --- Graphique 2 : Test d'évasion ---
modeles = ['B2 (mots)', 'B3 (caractères)', 'M1 (embeddings)']
scores = [100, 100, 93.3]
plt.figure(figsize=(6, 4))
bars = plt.bar(modeles, scores, color=['#ff9999', '#66b3ff', '#99ff99'])
plt.ylim(0, 110)
plt.title("Rappel sur 15 messages frauduleux obfusqués")
plt.ylabel("Rappel (%)")
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval}%', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig('slide_evasion.png', dpi=300)
plt.close()

# --- Graphique 3 : Courbe Précision-Rappel (simulée avec vos chiffres) ---
plt.figure(figsize=(6, 4))
# Approximation des points de fonctionnement
thresholds = [0.1, 0.26, 0.47, 0.8]
precision = [0.5, 0.75, 0.91, 0.99]
recall = [0.99, 0.96, 0.97, 0.70]

plt.plot(recall, precision, marker='o', linestyle='-', color='#2c3e50', linewidth=2)
plt.scatter([0.96], [0.75], color='red', s=150, zorder=5, label='Seuil choisi (0.26)')
plt.title('Courbe Précision-Rappel (Modèle M1)')
plt.xlabel('Rappel (Sensibilité)')
plt.ylabel('Précision')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('slide_courbe_pr.png', dpi=300)
plt.close()

print("Graphiques générés avec succès !")