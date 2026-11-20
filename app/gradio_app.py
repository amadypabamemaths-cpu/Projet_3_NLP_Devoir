import gradio as gr
import sys
from pathlib import Path
import joblib

# Permettre l'import de src/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rules import rule_score

MODEL_PATH = ROOT / "data" / "processed" / "model_b3.joblib"
b3 = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

# --- Dictionnaire des exemples ---
EXEMPLES = {
    "💸 Faux gain": ("Félicitations ! Vous avez gagné 500 000 FCFA. Cliquez ici : http://bit.ly/xx", "SMS", False),
    "🕵️ Faux agent": ("Bonjour, j'ai envoyé 25 000 FCFA par erreur. Renvoyez-les au 77 123 45 67 svp.", "WhatsApp", False),
    "⚠️ Piège (Lien+Montant)": ("Vous avez reçu 25 000 FCFA de Awa Diop. Voir le reçu : https://wave.com/recu/8841", "SMS", True),
    "💬 Légitime": ("Salut, on se voit toujours à 19h ce soir ?", "SMS", False)
}

def render_dashboard(message, canal, expediteur_verifie):
    if not message or message.strip() == "":
        return "<div style='color: #64748b; text-align: center; margin-top: 100px;'>En attente d'un message...</div>"

    rule_s, reasons = rule_score(message)
    ml_score = b3.predict_proba([message])[0, 1] if b3 else rule_s
    final_score = max(rule_s, ml_score)
    
    penalite_verifie = ""
    if expediteur_verifie:
        final_score = final_score * 0.3
        penalite_verifie = "<span style='color:#10b981; font-size:0.8em; display:block; margin-top:5px;'>✓ Expéditeur certifié : pénalité de risque appliquée.</span>"
        if "lien" in reasons: reasons.remove("lien")
        if "montant" in reasons: reasons.remove("montant")

    if final_score < 0.30:
        action_text, color, glow, icon = "SÉCURISÉ", "#10b981", "rgba(16, 185, 129, 0.4)", "✅"
    elif final_score < 0.60:
        action_text, color, glow, icon = "SUSPECT", "#f59e0b", "rgba(245, 158, 11, 0.4)", "⚠️"
    else:
        action_text, color, glow, icon = "DANGEREUX", "#ef4444", "rgba(239, 68, 68, 0.4)", "🚨"

    stroke_dasharray = 125.6
    stroke_dashoffset = stroke_dasharray - (final_score * stroke_dasharray)

    if not reasons:
        badges_html = "<span style='color: #64748b; font-size: 0.9em;'>Aucun signal fort détecté</span>"
    else:
        badges_html = "".join([
            f"<span style='background-color: rgba(255,255,255,0.05); border: 1px solid {color}; color: {color}; padding: 4px 10px; border-radius: 4px; font-size: 0.85em; font-weight: 600; margin-right: 8px; margin-bottom: 8px; display: inline-block; box-shadow: 0 0 8px {glow};'>{r.upper()}</span>" 
            for r in reasons
        ])

    html = f"""
    <style>
        .dash-container {{
            background-color: #0f172a;
            border-radius: 12px;
            padding: 25px;
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
            border: 1px solid #1e293b;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 280px;
        }}
        .gauge-wrapper {{
            position: relative;
            width: 200px;
            height: 100px;
            overflow: hidden;
            margin-bottom: 15px;
        }}
        .gauge-text {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 2em;
            font-weight: bold;
            color: {color};
            text-shadow: 0 0 10px {glow};
        }}
        .action-badge {{
            background-color: {color};
            color: #0f172a;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 800;
            font-size: 1.1em;
            letter-spacing: 1px;
            box-shadow: 0 0 15px {glow};
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .reasons-container {{
            width: 100%;
            text-align: center;
            margin-top: 10px;
            border-top: 1px solid #1e293b;
            padding-top: 15px;
        }}
        .reasons-title {{
            font-size: 0.8em;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }}
        .canal-badge {{
            background-color: #1e293b;
            color: #cbd5e1;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-bottom: 15px;
            border: 1px solid #334155;
        }}
    </style>

    <div class="dash-container">
        <div class="canal-badge">Canal : {canal}</div>
        
        <div class="gauge-wrapper">
            <svg viewBox="0 0 100 50" style="width: 100%; height: 100%;">
                <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#1e293b" stroke-width="8" stroke-linecap="round"/>
                <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{color}" stroke-width="8" stroke-linecap="round"
                      stroke-dasharray="{stroke_dasharray}" stroke-dashoffset="{stroke_dashoffset}"
                      style="transition: stroke-dashoffset 0.8s ease-in-out, stroke 0.3s ease; filter: drop-shadow(0 0 6px {glow});"/>
            </svg>
            <div class="gauge-text">{int(final_score*100)}%</div>
        </div>

        <div class="action-badge">
            {icon} {action_text}
        </div>
        {penalite_verifie}

        <div class="reasons-container">
            <div class="reasons-title">Signaux détectés</div>
            <div>{badges_html}</div>
        </div>
    </div>
    """
    return html

# --- Fonction pour charger un exemple et lancer l'analyse ---
def load_example(name):
    msg, canal, verif = EXEMPLES[name]
    return msg, canal, verif, render_dashboard(msg, canal, verif)

# --- CORRECTIF CSS GLOBAL ET FORCÉ ---
css = """
textarea, input[type="text"], .wrap-inner {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
}
.gradio-container label, .gradio-container span {
    color: #cbd5e1 !important;
}
ul.options, .dropdown-menu, .secondary-wrap {
    background-color: #0f172a !important;
    color: #f8fafc !important;
    border-color: #334155 !important;
}
ul.options li:hover {
    background-color: #1e293b !important;
}
.ex-btn button {
    background-color: #1e293b !important;
    color: #94a3b8 !important;
    border: 1px solid #334155 !important;
    border-radius: 20px !important;
    font-size: 0.85em !important;
    padding: 5px 10px !important;
    transition: all 0.2s ease;
}
.ex-btn button:hover {
    background-color: #334155 !important;
    color: #f8fafc !important;
    border-color: #475569 !important;
}
"""

dark_theme = gr.themes.Base(
    primary_hue="blue",
    neutral_hue="slate",
).set(
    body_background_fill="#020617",
    background_fill_primary="#0f172a",
    background_fill_secondary="#1e293b",
    block_background_fill="#0f172a",
    block_border_color="#334155",
    block_label_background_fill="#0f172a",
    block_label_text_color="#94a3b8",
    body_text_color="#f8fafc",
    input_background_fill="#1e293b"
)

with gr.Blocks(theme=dark_theme, title="Bouclier Anti-Fraude | TALN", css=css) as demo:
    
    gr.HTML("""
        <div style="text-align: center; margin-top: 20px; margin-bottom: 30px;">
            <h1 style="color: #f8fafc; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2.2em; letter-spacing: -1px;">
                🛡️ BOUCLIER <span style="color: #3b82f6;">ANTI-FRAUDE</span>
            </h1>
            <p style="color: #64748b; font-size: 1.1em;">Moteur de détection de messages frauduleux (TALN)</p>
        </div>
    """)
    
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            txt_input = gr.Textbox(
                label="Message entrant", 
                lines=5, 
                placeholder="Collez ici le SMS ou message WhatsApp suspect...",
                show_label=True
            )
            
            with gr.Row():
                canal = gr.Dropdown(
                    choices=["SMS", "WhatsApp", "Courriel", "Notification"], 
                    value="SMS", 
                    label="Canal de réception"
                )
                expediteur_verifie = gr.Checkbox(
                    label="Expéditeur certifié", 
                    value=False,
                    info="Simuler un compte officiel."
                )

            btn = gr.Button("Analyser le message", variant="primary", size="lg")
            
            gr.HTML("<hr style='border-color: #1e293b; margin: 20px 0 10px 0;'>")
            gr.HTML("<p style='color: #64748b; font-size: 0.85em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;'>Ou testez un exemple rapide :</p>")
            
            with gr.Row():
                btn_ex1 = gr.Button("💸 Faux gain", elem_classes="ex-btn")
                btn_ex2 = gr.Button("🕵️ Faux agent", elem_classes="ex-btn")
            
            with gr.Row():
                btn_ex3 = gr.Button("⚠️ Piège", elem_classes="ex-btn")
                btn_ex4 = gr.Button("💬 Légitime", elem_classes="ex-btn")

        with gr.Column(scale=1):
            html_output = gr.HTML(
                value="<div style='background-color: #0f172a; border: 1px dashed #334155; border-radius: 12px; height: 400px; display: flex; align-items: center; justify-content: center; color: #475569; font-family: Inter, sans-serif;'>Le résultat de l'analyse s'affichera ici</div>"
            )
            
    btn.click(fn=render_dashboard, inputs=[txt_input, canal, expediteur_verifie], outputs=html_output)

    outputs_ex = [txt_input, canal, expediteur_verifie, html_output]
    btn_ex1.click(fn=lambda: load_example("💸 Faux gain"), outputs=outputs_ex)
    btn_ex2.click(fn=lambda: load_example("🕵️ Faux agent"), outputs=outputs_ex)
    btn_ex3.click(fn=lambda: load_example("⚠️ Piège (Lien+Montant)"), outputs=outputs_ex)
    btn_ex4.click(fn=lambda: load_example("💬 Légitime"), outputs=outputs_ex)

if __name__ == "__main__":
    demo.launch()