import streamlit as st
import pandas as pd
import re
from io import BytesIO

# === Table de correction à enrichir ===
CORRECTIONS = {
    '@': 'à',
    '(c)': '©',
    '(r)': '®',
    '(tm)': '™',
    'oe': 'œ',
    'a`': 'à',
    'e`': 'è',
    # Ajoute ici tes corrections...
}

def corriger_texte(texte):
    if not isinstance(texte, str):
        return texte
    # Correction par mapping exact
    for k, v in CORRECTIONS.items():
        texte = texte.replace(k, v)
    # Correction de caractères isolés non imprimables
    texte = re.sub(r'[^\w\sÀ-ÿ\'.,;:!?()-]', '', texte)
    return texte

def corriger_dataframe(df):
    return df.applymap(corriger_texte)

def trouver_suspects(df):
    suspects = []
    for cell in df.values.flatten():
        if isinstance(cell, str):
            suspects += re.findall(r'[^\w\sÀ-ÿ\']{2,6}', cell)
    return pd.Series(suspects).value_counts()

# --- Interface Streamlit ---
st.title("Correcteur Excel – Caractères illisibles")
uploaded_file = st.file_uploader("Téléverse ton fichier Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("Aperçu du fichier original")
    st.dataframe(df.head())
    
    # Détection caractères suspects
    suspects = trouver_suspects(df)
    if not suspects.empty:
        st.warning("Caractères/séquences suspects détectés :")
        st.write(suspects)
    else:
        st.success("Aucun caractère suspect détecté !")

    if st.button("Corriger le fichier"):
        df_corr = corriger_dataframe(df)
        st.subheader("Aperçu du fichier corrigé")
        st.dataframe(df_corr.head())
        
        # Sauvegarde Excel en mémoire
        output = BytesIO()
        df_corr.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        st.download_button(
            label="Télécharger le fichier corrigé",
            data=output,
            file_name="fichier_corrigé.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
