"""Interface web (Streamlit) do assistente.

Uso (a partir da pasta `src`, com a API no ar em http://localhost:8000):

    streamlit run app/ui.py
"""

import os

import streamlit as st

from app.rag.http import HttpError, request_json

API_URL = os.getenv("API_URL", "http://localhost:8000")
EXAMPLES = [
    "Como sobrescrever uma dependência em testes?",
    "Como declarar um parâmetro de consulta opcional?",
    "Como integrar o FastAPI com a Stripe?",
]

st.set_page_config(page_title="Assistente da documentação do FastAPI", page_icon="📚")
st.title("📚 Assistente da documentação do FastAPI")
st.caption(
    "Responde em português usando só a documentação oficial (versão 0.162.0) e sempre cita a "
    "fonte. Se a documentação não tiver a resposta, o assistente diz que não sabe."
)

if "question" not in st.session_state:
    st.session_state.question = ""

for example in EXAMPLES:
    if st.button(example, key=example):
        st.session_state.question = example

question = st.text_input("Sua pergunta", key="question")

if st.button("Perguntar", type="primary") and question.strip():
    with st.spinner("Buscando na documentação e escrevendo a resposta..."):
        try:
            data = request_json("POST", f"{API_URL}/ask", {"question": question}, timeout=300)
        except (ConnectionError, HttpError) as error:
            st.error(f"Não consegui falar com a API: {error}")
            st.stop()
    if data["refused"]:
        st.warning(
            "Não encontrei essa informação na documentação. "
            "Tente reformular a pergunta ou consulte outra fonte."
        )
    else:
        st.markdown(data["answer"])
        if not data["sources"]:
            st.info("Atenção: esta resposta não citou nenhum trecho. Confira na documentação.")
        for source in data["sources"]:
            with st.expander(f"[{source['n']}] {source['source_file']}"):
                st.code(source["text"], language="markdown")
    st.caption(f"Tempo: {data['seconds']:.1f} s | similaridade: {data['top_score']:.3f}")
