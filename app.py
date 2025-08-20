import streamlit as st
from streamlit_option_menu import option_menu
from models.models import init_db, authenticate, create_session, get_session, delete_session
from views.add_user_view import add_user_tab
from views.recognition_view import recognition_tab
from views.account_management_view import account_management_tab
from PIL import Image
import base64

# --------------------
# Config page
# --------------------
st.set_page_config(
    page_title="Système de Contrôle d'Accès",
    page_icon="🔒",
    layout="wide"
)

# --------------------
# CSS custom
# --------------------
st.markdown("""
    <style>
    .main { 
        background-color: #f7f9fc; 
    }
    h1 { 
        text-align: center;
        color: #1e3a8a; 
        font-size: 2.2em; 
        margin-bottom: 10px;
    }
    .card { 
        background-color: white;
        padding: 25px;
        border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px; 
    }
    .stButton > button { border-radius: 8px; padding: 6px 12px; font-weight: bold; font-size: 0.9em; background-color: #2563eb; color: white; border: none; }
    .stButton > button:hover { background-color: #1e40af; color: white; }
    div.stButton > button[key="sidebar_logout"] {
        background-color: #dc2626 !important;  /* rouge vif */
        color: white !important;
        font-weight: bold;
        border-radius: 8px;
        padding: 6px 12px;
        width: 100%;
    }
    div.stButton > button[key="sidebar_logout"]:hover {
        background-color: #b91c1c !important;  /* rouge foncé au survol */
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------
# Initialisation DB
# --------------------
init_db()

# --------------------
# Session state
# --------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.username = None

# Restaurer session depuis DB
if not st.session_state.authenticated:
    username, role = get_session()
    if username and role:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.role = role

# Fonction pour encoder l'image en base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Chemin vers ton logo local
logo_base64 = get_base64_of_bin_file("logo_dit.png")

# --------------------
# Page de connexion
# --------------------
if not st.session_state.authenticated:
    st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center; padding-bottom: 30px;">
        <img src="data:image/png;base64,{logo_base64}" 
            alt="Logo DIT"
            style="width: 100%; height: auto; max-width: 200px;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align:center; margin-bottom:1.5vw;">
            <p style="background-color:#d1ecf1; color:#0c5460; padding:10px; border-radius:5px; font-size:1.2vw;">
            🔑 Veuillez sélectionner votre type d'utilisateur puis entrer vos identifiants pour accéder au système
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        user_type = st.selectbox("Type d'utilisateur", ["admin", "gardien"], index=0)
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            ok, role = authenticate(username, password)
            if ok:
                st.session_state.authenticated = True
                st.session_state.role = role
                st.session_state.username = username
                create_session(username, role)
                st.success(f"✅ Connecté en tant que {username} ({role})")
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects")

# --------------------
# Interface après connexion
# --------------------
else:
    # --- Sidebar utilisateur ---
    with st.sidebar:
        # Affichage logo + rôle
        st.markdown(f"""
            <div style="width: 100%; display: flex; justify-content: center; align-items: center; padding-bottom: 50px;">
                <img src="data:image/png;base64,{logo_base64}" 
                    alt="Logo DIT"
                    style="width: 100%; height: auto; max-width: 600px;">
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<span style='font-size:1em'>👤 {st.session_state.role}</span>", unsafe_allow_html=True)
        
        # Menu navigation
        menu_items = ["Nouveau visage", "Reconnaissance"]
        menu_icons = ["person-plus", "camera-video"]
        if st.session_state.role == "admin":
            menu_items.append("Gestion comptes")
            menu_icons.append("gear")

        choice = option_menu(
            "",
            menu_items,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {
                    "background": "linear-gradient(180deg, #1e3a8a, #2563eb)",
                    "padding": "10px",
                    "border-radius": "10px",
                    "box-shadow": "0 4px 12px rgba(0,0,0,0.2)"
                },
                "icon": {
                    "color": "white",
                    "font-size": "10vw",
                    "text-shadow": "1px 1px 2px rgba(0,0,0,0.3)"
                },
                "nav-link": {
                    "color": "white",
                    "font-size": "clamp(12px, 1.2vw, 16px)",
                    "text-align": "left",
                    "white-space": "nowrap",
                    "overflow": "hidden",
                    "padding": "12px 16px",
                    "border-radius": "5px",
                    "transition": "all 0.2s ease"
                },
                "nav-link-hover": {
                    "background-color": "#3b82f6",
                    "color": "white",
                    "cursor": "pointer"
                },
                "nav-link-selected": {
                    "background-color": "#60a5fa",
                    "color": "white",
                    "font-weight": "bold"
                }
            }
        )

        if st.button("⏻ Logout", key="sidebar_logout"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.username = None
            delete_session()
            st.rerun()

    # --- Header option dynamique ---
    option_texts = {
        "Nouveau visage": "Ajouter un nouvel employé au système",
        "Reconnaissance": "Contrôle d'accès via reconnaissance faciale",
        "Gestion comptes": "Gestion des comptes utilisateurs"
    }
    st.markdown(f"""
        <div style="text-align:center; margin-bottom:2vw;">
            <h1 style="color:#1e3a8a; font-size:2.5vw; margin-bottom:0.5vw; word-wrap: break-word;">
                {option_texts.get(choice, "")}
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # --- Contenu selon le choix ---
    if choice == "Nouveau visage":
        add_user_tab()
    elif choice == "Reconnaissance":
        recognition_tab()
    elif choice == "Gestion comptes":
        account_management_tab()