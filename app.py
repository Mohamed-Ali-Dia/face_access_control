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
        font-size: 2.2em;
        margin-bottom: 10px;
    }
    h2 {
        color: #2563eb;
    }
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton > button {
        border-radius: 8px;
        padding: 6px 12px;
        font-weight: bold;
        font-size: 0.9em;  
        background-color: #2563eb;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1e40af;
        color: white;
    }
            
    /* Sidebar complète prend 100% de la hauteur */
    .sidebar .css-1d391kg {
        height: 100vh !important;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    /* Option menu prend tout l'espace et ne scroll pas */
    .sidebar .menu-container {
        flex: 1 1 auto !important;
        overflow: hidden !important;
    }
    iv.stButton > button:first-child {
        padding: 3px 6px;
        font-size: 0.7em;      
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
    st.markdown("<h1>🔑 Connexion au système</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align:center; margin-bottom:1.5vw;">
            <p style="color:#1e3a8a; font-size:1.2vw; word-wrap: break-word;background-color:#d1ecf1; color:#0c5460; padding:10px; border-radius:5px">
            💡 Veuillez sélectionner votre type d'utilisateur puis entrer vos identifiants pour accéder au système
            </p>
        </div>
    """, unsafe_allow_html=True)
    with st.container():
        user_type = st.selectbox(
            "Type d'utilisateur",
            ["admin", "gardien"],
            index=0
        )
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            ok, role = authenticate(username, password, user_type)  # transmettre user_type si nécessaire
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
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"<span style='font-size:1em'>👤 {st.session_state.role}</span>", unsafe_allow_html=True)
        with col2:
            if st.button("⏻ Logout", key="sidebar_logout"):
                st.session_state.authenticated = False
                st.session_state.role = None
                st.session_state.username = None
                delete_session()
                st.rerun()


        st.markdown("""
            <h2 style="
                text-align:center; 
                background: linear-gradient(90deg, #1e3a8a, #2563eb);
                color:white; 
                font-size:1.5vw; 
                padding:15px; 
                border-radius:10px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.2); 
                margin-bottom:1vw;
                ">
                <span style="display:block; font-size:3vw; color:#ffd700; text-shadow: 1px 1px 2px black;">🔒</span>
                Système de contrôle d'accès par reconnaissance faciale
            </h2>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Augmenter la largeur de la sidebar pour que le texte tienne
        st.sidebar.markdown("""
                            <style>
                            .css-1d391kg { width: 250px !important; }
                            </style>
                            """, unsafe_allow_html=True)

        # Menu navigation adaptatif, texte sur une seule ligne
        if st.session_state.role == "admin":
            choice = option_menu(
                "",
                ["Nouveau visage", "Reconnaissance", "Gestion comptes"],
                icons=["person-plus", "camera-video", "gear"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"background-color": "#1e3a8a"},
                    "icon": {"color": "white", "font-size": "2vw"},
                    "nav-link": {
                        "color": "white",
                        "font-size": "clamp(12px, 1.2vw, 16px)",
                        "text-align": "left",
                        "white-space": "nowrap",      # force une seule ligne
                        "overflow": "hidden",         # masque débordement
                        "text-overflow": "ellipsis"   # ajoute "…" si texte trop long
                    },
                    "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
                }
            )
        else:
            choice = option_menu(
                "",
                ["Nouveau visage", "Reconnaissance"],
                icons=["person-plus", "camera-video", "gear"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"background-color": "#1e3a8a"},
                    "icon": {"color": "white", "font-size": "2vw"},
                    "nav-link": {
                        "color": "white",
                        "font-size": "clamp(12px, 1.2vw, 16px)",
                        "text-align": "left",
                        "white-space": "nowrap",      # force une seule ligne
                        "overflow": "hidden",         # masque débordement
                        "text-overflow": "ellipsis"   # ajoute "…" si texte trop long
                    },
                    "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
                }
            )



        # Header principal adaptatif avec le nom de l'option sélectionnée
        option_texts = {
            "Nouveau visage": "Ajouter un nouvel visage (employé) au système",
            "Reconnaissance": "Control d'accès via la reconnaissance faciale",
            "Gestion comptes": "Gestion des comptes utilisateurs existants"
        }

        st.markdown(f"""
        <div style="text-align:center; margin-bottom:3vw;">
            <h1 style="color:#1e3a8a; font-size:2.5vw; margin-bottom:0.5vw; word-wrap: break-word;">
                {option_texts.get(choice, "")}
            </h1>
            <div style="width:10vw; max-width:60px; height:0.5vw; background-color:#2563eb; margin:0 auto 1vw; border-radius:2px;"></div>
        </div>
        """, unsafe_allow_html=True)


        # --- Contenu en fonction du choix ---
        if choice == "Nouveau visage":
            add_user_tab()
        elif choice == "Reconnaissance":
            recognition_tab()
        elif choice == "Gestion comptes":
            account_management_tab()
