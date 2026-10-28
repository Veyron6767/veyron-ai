import streamlit as st
from groq import Groq

# 1. Konfiguracja strony - układ scentrowany (jak w telefonie/Messengerze)
st.set_page_config(page_title="Veyron AI", page_icon="⚡", layout="centered")

# CSS - Wygląd a'la Messenger
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dymek Użytkownika (Prawa strona - Niebieski z zaokrągleniami Messengera) */
    div[data-testid="stChatMessage"]:has(div:contains("👤")) {
        flex-direction: row-reverse;
        text-align: right;
    }
    div[data-testid="stChatMessage"]:has(div:contains("👤")) div[data-testid="stChatMessageContent"] {
        background-color: #0084ff;
        color: white;
        padding: 10px 16px;
        border-radius: 18px 18px 4px 18px;
        display: inline-block;
        max-width: 80%;
        border: none;
        box-shadow: none;
    }
    
    /* Dymek Asystenta (Lewa strona - Ciemnoszary z zaokrągleniami Messengera) */
    div[data-testid="stChatMessage"]:has(div:contains("⚡")) {
        flex-direction: row;
        text-align: left;
    }
    div[data-testid="stChatMessage"]:has(div:contains("⚡")) div[data-testid="stChatMessageContent"] {
        background-color: #3e4042;
        color: white;
        padding: 10px 16px;
        border-radius: 18px 18px 18px 4px;
        display: inline-block;
        max-width: 80%;
        border: none;
        box-shadow: none;
    }
</style>
""", unsafe_allow_html=True)

# 2. Bezpieczne pobieranie klucza
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = None

# 3. Górna sekcja (Zamiast panelu bocznego)
st.caption("Wybierz moduł AI:")
tryb = st.selectbox(
    "Wybierz moduł AI:",
    ["Veyron 1.5 flash", "Veyron 1.7 pro", "Veyron 2.0 learn", "Veyron 3.1 coding", "Veyron custom"],
    label_visibility="collapsed"
)

st.title(f"⚡ Veyron")

# Konfiguracja parametrów
temperatura = 0.7
max_tokens = 2048
system_prompt = "Jesteś inteligentnym, nowoczesnym asystentem."
model_id = "openai/gpt-oss-120b"

if tryb == "Veyron 1.5 flash":
    model_id = "qwen/qwen3.8-27b"
    system_prompt = "Odpowiadaj błyskawicznie, zwięźle i konkretnie. Jesteś trybem Flash."
    temperatura = 0.5
elif tryb == "Veyron 1.7 pro":
    model_id = "openai/gpt-oss-120b"
    system_prompt = "Jesteś zaawansowanym analitykiem Veyron Pro. Rozwiązuj problemy krok po kroku, bądź precyzyjny."
    temperatura = 0.3
elif tryb == "Veyron 2.0 learn":
    model_id = "openai/gpt-oss-120b"
    system_prompt = "Jesteś mentorem edukacyjnym. Tłumacz złożone zjawiska prostym językiem, używaj przykładów."
    temperatura = 0.6
elif tryb == "Veyron 3.1 coding":
    model_id = "openai/gpt-oss-120b"
    system_prompt = "Jesteś ekspertem programowania. Podawaj zoptymalizowany kod z komentarzami."
    temperatura = 0.2
elif tryb == "Veyron custom":
    with st.expander("⚙️ Ustawienia niestandardowe"):
        temperatura = st.slider("Kreatywność (Temperature):", 0.0, 1.5, 0.7, 0.1)
        max_tokens = st.slider("Długość odpowiedzi:", 256, 4096, 2048, 128)
        system_prompt = st.text_area("Instrukcja:", "Jesteś w pełni dostosowanym modelem.")
    model_id = "openai/gpt-oss-120b"

# 4. Inicjalizacja wiadomości w stylu komunikatora
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hej! W czym mogę Ci dzisiaj pomóc? 👋"})

avatar_dict = {"user": "👤", "assistant": "⚡"}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatar_dict[msg["role"]]):
        st.markdown(msg["content"])

# 5. Dolna sekcja - Załącznik nad polem tekstowym
st.markdown("---")
with st.expander("📎 Dodaj załącznik (opcjonalnie)"):
    uploaded_file = st.file_uploader("Wybierz plik", label_visibility="collapsed", type=["txt", "py", "md", "csv"])

user_prompt = st.chat_input("Napisz wiadomość...")

# Logika wysyłania wiadomości
if user_prompt:
    if not api_key:
        st.error("Brak dostępu do klucza API w chmurze! Upewnij się, że wpisałeś GROQ_API_KEY w zakładce Secrets.")
    else:
        client = Groq(api_key=api_key)
        pelna_wiadomosc = user_prompt
        
        if uploaded_file is not None:
            try:
                zawartosc = uploaded_file.read().decode("utf-8")
                pelna_wiadomosc += f"\n\n> **Załączono plik: {uploaded_file.name}**\n```\n{zawartosc}\n```"
            except:
                pelna_wiadomosc += f"\n\n> **Załączono plik binarny: {uploaded_file.name}**"

        st.session_state.messages.append({"role": "user", "content": pelna_wiadomosc})
        with st.chat_message("user", avatar="👤"):
            st.markdown(pelna_wiadomosc)

        with st.chat_message("assistant", avatar="⚡"):
            wiadomosci_api = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages:
                wiadomosci_api.append({"role": m["role"], "content": m["content"]})
            
            with st.spinner("Veyron odpisuje..."):
                try:
                    odpowiedz = client.chat.completions.create(
                        model=model_id,
                        messages=wiadomosci_api,
                        temperature=temperatura,
                        max_tokens=max_tokens
                    )
                    tekst_odpowiedzi = odpowiedz.choices[0].message.content
                    st.markdown(tekst_odpowiedzi)
                    st.session_state.messages.append({"role": "assistant", "content": tekst_odpowiedzi})
                except Exception as e:
                    st.error(f"Wystąpił błąd: {e}")
