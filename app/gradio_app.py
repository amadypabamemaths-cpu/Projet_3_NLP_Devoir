import gradio as gr
import sys
from pathlib import Path

# Permettre l'import de src/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rules import rule_score
from src.models import build_b3
import joblib

# On charge un modèle pré-entraîné (B3 est rapide et robuste)
# S'il n'existe pas, on le crée sur le pouce
MODEL_PATH = ROOT / "data" / "processed" / "model_b3.joblib"
if MODEL_PATH.exists():
    b3 = joblib.load(MODEL_PATH)
else:
    # Fallback (si le notebook n'a pas encore sauvegardé le modèle)
    b3 = None

def analyser(message):
    # 1. Score des règles (explicable)
    rule_s, reasons = rule_score(message)
    
    # 2. Score du modèle ML (si dispo)
    if b3 is not None:
        ml_score = b3.predict_proba([message])[0, 1]
    else:
        ml_score = rule_s
        
    # Décision (seuil 0.3 pour être prudent dans la démo)
    final_score = max(rule_s, ml_score)
    
    if final_score < 0.3:
        action = "✅ Laisser passer"
    elif final_score < 0.6:
        action = "⚠️ Avertir le client"
    else:
        action = "🚨 Envoyer à un analyste"
        
    return {
        "score_de_risque": round(float(final_score), 2),
        "raisons_detectees": reasons if reasons else ["aucune"],
        "action_recommandee": action
    }

with gr.Blocks(title="Détection de Fraude NLP") as demo:
    gr.Markdown("# 🛡️ Détection de messages frauduleux")
    gr.Markdown("Entrez un message ci-dessous pour analyser son niveau de risque.")
    
    with gr.Row():
        with gr.Column():
            txt_input = gr.Textbox(label="Message reçu", lines=4, placeholder="Ex: Félicitations, vous avez gagné 500 000 FCFA...")
            btn = gr.Button("Analyser le message", variant="primary")
        with gr.Column():
            json_output = gr.JSON(label="Résultat de l'analyse")
            
    btn.click(fn=analyser, inputs=txt_input, outputs=json_output)
    
    gr.Examples(
        examples=[
            ["Félicitations ! Vous avez gagné 500 000 FCFA. Cliquez ici : http://bit.ly/xx"],
            ["Bonjour, j'ai envoyé 25 000 FCFA par erreur sur votre numéro. Renvoyez-les au 77 123 45 67 svp."],
            ["Vous avez reçu 25 000 FCFA de Awa Diop le 12/03. Réf : MP240312. Voir le reçu : https://wave.com/recu/8841"],
            ["Votre code de confirmation est 4829. Ne le partagez avec personne."]
        ],
        inputs=txt_input
    )

if __name__ == "__main__":
    demo.launch()