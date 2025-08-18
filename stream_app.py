import streamlit as st
from streamlit_option_menu import option_menu
from models import (
    init_db, authenticate,
    create_session, get_session, delete_session
)
from views.add_user_view import add_user_tab
from views.recognition_view import recognition_tab
from views.account_management_view import account_management_tab

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
        font-size: 1.8em;
        margin-bottom: 6px;
    }
    h2 {
        color: #2563eb;
        font-size: 1.4em;
        margin-bottom: 4px;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .stButton > button {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        background-color: #2563eb;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1e40af;
        color: white;
    }
    /* Animation barre header */
    @keyframes slide {
        0% { transform: scaleX(0); }
        50% { transform: scaleX(1.2); }
        100% { transform: scaleX(0); }
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

# --------------------
# Page de connexion
# --------------------
if not st.session_state.authenticated:
    st.markdown("""
        <div style="text-align:center; margin-bottom:15px;">
            <h1>🔑 Connexion au système</h1>
            <div style="width:50px; height:3px; background-color:#2563eb; margin:0 auto 5px; border-radius:2px; animation: slide 1.2s ease-in-out infinite;"></div>
        </div>
    """, unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------
# Interface utilisateur après connexion
# --------------------
else:
    # --- Sidebar utilisateur ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3064/3064197.png", width=80)
        st.markdown(f"### 👤 {st.session_state.username}")
        st.caption(f"Rôle : {st.session_state.role}")
        if st.button("🚪 Se déconnecter"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.username = None
            delete_session()
            st.rerun()

        st.markdown("---")
        # Menu navigation
        if st.session_state.role == "admin":
            choice = option_menu(
                "",
                ["Nouveau visage", "Reconnaissance", "Gestion comptes"],
                icons=["person-plus", "camera-video", "gear"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"background-color": "#1e3a8a"},
                    "icon": {"color": "white", "font-size": "20px"},
                    "nav-link": {"color": "white", "font-size": "16px", "text-align": "left"},
                    "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
                }
            )
        else:
            choice = option_menu(
                "Navigation",
                ["Nouveau visage", "Reconnaissance"],
                icons=["person-plus", "camera-video"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"background-color": "#1e3a8a"},
                    "icon": {"color": "white", "font-size": "20px"},
                    "nav-link": {"color": "white", "font-size": "16px", "text-align": "left"},
                    "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
                }
            )

    # --- Header principal animé ---
    st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <h1>🔒 Système de contrôle d'accès par reconnaissance faciale</h1>
            <div style="width:60px; height:4px; background-color:#2563eb; margin:0 auto 6px; border-radius:2px; animation: slide 1.2s ease-in-out infinite;"></div>
        </div>
    """, unsafe_allow_html=True)

    # --- Contenu en fonction du choix ---
    if choice == "Nouveau visage":
        add_user_tab()
    elif choice == "Reconnaissance":
        recognition_tab()
    elif choice == "Gestion comptes":
        account_management_tab()
