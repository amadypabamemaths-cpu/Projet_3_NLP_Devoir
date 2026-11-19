"""Chargement et génération des données.

Toutes les fonctions ont un repli déterministe : le notebook tourne sur un
Colab frais, même sans accès réseau. L'équipe remplace progressivement les
gabarits par les vrais messages dans data/local/*.jsonl.
"""
import hashlib
import io
import random
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd

from src.templates import FRAUD_TEMPLATES, LEGIT_TEMPLATES, TRAP_TEMPLATES, fill

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# --- Constantes à ajuster par l'équipe après le 1er run ---------------------
# Recopier ici le hash affiché à la fin de la cellule 6 du notebook.
EXPECTED_TEST_HASH: Optional[str] = None


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# SMS Spam Collection (UCI) avec repli synthétique
# ---------------------------------------------------------------------------
def load_uci_sms() -> pd.DataFrame:
    urls = [
        "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip",
        "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip",
    ]
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                z = zipfile.ZipFile(io.BytesIO(r.read()))
            name = [n for n in z.namelist() if n.endswith("SMSSpamCollection")][0]
            rows = []
            for line in z.read(name).decode("utf-8").splitlines():
                if "\t" in line:
                    label, text = line.split("\t", 1)
                    rows.append({
                        "text": text, "label": int(label.strip() == "spam"),
                        "lang": "en", "source": "uci_sms_spam",
                    })
            print(f"[UCI] {len(rows)} messages chargés ({sum(r['label'] for r in rows)} spam).")
            return pd.DataFrame(rows)
        except Exception as e:
            print(f"[UCI] échec {url[:60]}… : {e}")

    print("[UCI] repli synthétique.")
    synth = [
        ("Free entry! Win £1000 cash now. Text WIN to 80086", 1),
        ("CONGRATULATIONS! You have won a £2000 prize. Call 09061701461", 1),
        ("URGENT! Your mobile was awarded £2000 Bonus. Call now", 1),
        ("Your account will be suspended. Verify at http://bit.ly/xx", 1),
        ("Hey, are we still on for lunch tomorrow?", 0),
        ("Your package has been delivered. Thanks for shopping", 0),
        ("Your OTP is 4829. Do not share", 0),
        ("Can you send me the report by 5pm?", 0),
    ]
    return pd.DataFrame([
        {"text": t, "label": l, "lang": "en", "source": "synthetic_en"}
        for t, l in synth
    ])


# ---------------------------------------------------------------------------
# Corpus local : chargement si présent, sinon génération depuis gabarits
# ---------------------------------------------------------------------------
def load_local_corpus() -> pd.DataFrame:
    local_dir = DATA / "local"
    local_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(local_dir.glob("*.jsonl"))
    if paths:
        df = pd.concat([pd.read_json(p, lines=True) for p in paths], ignore_index=True)
        print(f"[Local] {len(df)} messages chargés depuis data/local/.")
        return df
    print("[Local] génération depuis gabarits.")
    return _generate_from_templates(n_fraud=260, n_legit=520, seed=42)


def _generate_from_templates(n_fraud: int, n_legit: int, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for i in range(n_fraud):
        typ, tpl = FRAUD_TEMPLATES[i % len(FRAUD_TEMPLATES)]
        rows.append({
            "id": f"f{i:04d}", "text": fill(tpl, rng),
            "label": 1, "lang": "fr", "type": typ, "source": "template",
        })
    for i in range(n_legit):
        typ, tpl = LEGIT_TEMPLATES[i % len(LEGIT_TEMPLATES)]
        rows.append({
            "id": f"l{i:04d}", "text": fill(tpl, rng),
            "label": 0, "lang": "fr", "type": typ, "source": "template",
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Test gelé : chargement ou génération, avec vérification du hash
# ---------------------------------------------------------------------------
def get_frozen_test(path: Optional[Path] = None) -> pd.DataFrame:
    path = path or (DATA / "test_frozen.jsonl")
    if path.exists():
        if EXPECTED_TEST_HASH and file_sha256(path) != EXPECTED_TEST_HASH:
            raise RuntimeError(
                f"TEST GELÉ MODIFIÉ !\n  Attendu : {EXPECTED_TEST_HASH}\n"
                f"  Obtenu  : {file_sha256(path)}"
            )
        df = pd.read_json(path, lines=True)
        print(f"[Test gelé] {len(df)} messages — hash {file_sha256(path)[:16]}…")
        return df

    df = _generate_frozen_test()
    df.to_json(path, orient="records", lines=True, force_ascii=False)
    print(f"[Test gelé] généré : {len(df)} messages ({int(df.label.sum())} fraudes, "
          f"{int((df.type=='trap').sum())} pièges).")
    print(f"[Test gelé] ⚠️ HASH À NOTER : {file_sha256(path)}")
    return df


def _generate_frozen_test(seed: int = 43) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for i in range(40):
        typ, tpl = FRAUD_TEMPLATES[i % len(FRAUD_TEMPLATES)]
        rows.append({"id": f"tf{i:03d}", "text": fill(tpl, rng), "label": 1,
                     "lang": "fr", "type": typ, "source": "frozen_test"})
    hand_frauds = [
        "Bonjour, je suis le service client Wave. Votre compte est suspendu. Envoyez votre code PIN au 77 123 45 67.",
        "Félicitations cher client, vous avez gagné 1 500 000 FCFA. Payez 10 000 FCFA de frais pour recevoir.",
        "URGENT : votre transfert de 250 000 FCFA est bloqué. Cliquez http://wave-verif.xyz pour débloquer.",
        "Papa c'est moi, j'ai eu un accident. Envoie 100 000 FCFA vite au 78 999 88 77.",
        "Offre emploi : 300 000 FCFA/mois. Frais dossier 3 000 FCFA au 76 111 22 33. Urgent.",
        "J'ai envoyé 50 000 par erreur, renvoyez au 77 555 44 33 s'il vous plaît.",
        "Votre colis est bloqué à la douane. Réglez 15 000 FCFA au 70 123 45 67 pour le libérer.",
        "Cher client, votre carte bancaire expire. Confirmez vos informations ici : http://bit.ly/card-update",
        "Vous avez gagné un iPhone 15 ! Cliquez http://promo-gratuit.tk pour réclamer.",
        "Bonjour, je suis Aminata, j'ai besoin d'aide urgente. Envoyez 25 000 FCFA au 77 000 11 22.",
    ]
    for i, txt in enumerate(hand_frauds):
        rows.append({"id": f"tfh{i:02d}", "text": txt, "label": 1,
                     "lang": "fr", "type": "hand", "source": "frozen_test"})
    for i, tpl in enumerate(TRAP_TEMPLATES):
        rows.append({"id": f"tr{i:02d}", "text": fill(tpl, rng), "label": 0,
                     "lang": "fr", "type": "trap", "source": "frozen_test"})
    for i in range(90):
        typ, tpl = LEGIT_TEMPLATES[i % len(LEGIT_TEMPLATES)]
        rows.append({"id": f"tl{i:03d}", "text": fill(tpl, rng), "label": 0,
                     "lang": "fr", "type": typ, "source": "frozen_test"})
    return pd.DataFrame(rows).sample(frac=1, random_state=seed).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Test d'évasion
# ---------------------------------------------------------------------------
def get_evasion(path: Optional[Path] = None) -> pd.DataFrame:
    path = path or (DATA / "evasion.jsonl")
    if path.exists():
        return pd.read_json(path, lines=True)
    df = _generate_evasion()
    df.to_json(path, orient="records", lines=True, force_ascii=False)
    print(f"[Évasion] généré : {len(df)} messages.")
    return df


def _generate_evasion(seed: int = 44) -> pd.DataFrame:
    import re as _re
    rng = random.Random(seed)

    def obfuscate(text: str) -> str:
        leet = {"a": "@", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}
        out = []
        for c in text:
            if c.lower() in leet and rng.random() < 0.25:
                out.append(leet[c.lower()])
            elif rng.random() < 0.03:
                out.append(c + "\u200b")
            else:
                out.append(c)
        s = "".join(out)
        return _re.sub(r"(\d{2})(\d{2})", r"\1 \2", s)

    fraud = _generate_from_templates(n_fraud=15, n_legit=0, seed=seed)
    legit = _generate_from_templates(n_fraud=0, n_legit=15, seed=seed + 100)
    rows = []
    for _, r in fraud.iterrows():
        rows.append({"id": "ev_f_" + r["id"], "text": obfuscate(r["text"]),
                     "label": 1, "lang": "fr", "type": "evasion_fraud", "source": "evasion"})
    for _, r in legit.iterrows():
        rows.append({"id": "ev_l_" + r["id"], "text": r["text"],
                     "label": 0, "lang": "fr", "type": "evasion_legit", "source": "evasion"})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Chargement complet pour entraînement
# ---------------------------------------------------------------------------
def load_all_train() -> pd.DataFrame:
    """Concatène UCI + local. Retourne un DataFrame avec colonnes normalisées."""
    uci = load_uci_sms()
    local = load_local_corpus()
    cols = ["text", "label", "lang", "source"]
    return pd.concat([uci[cols], local[cols]], ignore_index=True)