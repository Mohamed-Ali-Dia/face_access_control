import streamlit as st
from models import get_all_accounts, add_account, update_account, delete_account, get_account_by_username

def account_management_tab():

    st.markdown("""
        <div style="text-align:center; margin-bottom:1.5vw;">
            <p style="color:#1e3a8a; font-size:1.2vw; word-wrap: break-word;background-color:#d1ecf1; color:#0c5460; padding:8px; border-radius:5px">
                💡 Sélectionnez une action ci-dessous et suivez les instructions pour gérer les comptes utilisateurs.
            </p>
        </div>
        """, unsafe_allow_html=True)

    action = st.selectbox("Choisir une action", ["Créer un utilisateur", "Modifier mot de passe", "Modifier rôle", "Supprimer utilisateur"])
    
    # Charger la liste des comptes existants pour certains actions
    all_accounts = [u for u, r in get_all_accounts()]

    if action == "Créer un utilisateur":
        new_user = st.text_input("Nom utilisateur (nouveau)", key="create_user")
        new_pass = st.text_input("Mot de passe", type="password", key="create_pass")
        role = st.selectbox("Rôle", ["gardien", "admin"], key="create_role")
        if st.button("Créer compte", key="create_button"):
            try:
                add_account(new_user, new_pass, role)
                st.success(f"✅ Compte {new_user} ({role}) créé.")
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    st.error(f"❌ Erreur : le nom d'utilisateur '{new_user}' existe déjà.")
                else:
                    st.error(f"❌ Erreur inattendue : {e}")

    elif action == "Modifier mot de passe":
        user_to_update = st.selectbox("Utilisateur", all_accounts, key="update_pass_user")
        new_pass = st.text_input("Nouveau mot de passe", type="password", key="update_pass")
        if st.button("Mettre à jour le mot de passe", key="update_pass_button"):
            try:
                update_account(user_to_update, new_password=new_pass)
                st.success(f"✅ Mot de passe de '{user_to_update}' mis à jour.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

    elif action == "Modifier rôle":
        user_to_update = st.selectbox("Utilisateur", all_accounts, key="update_role_user")
        new_role = st.selectbox("Nouveau rôle", ["gardien", "admin"], key="update_role")
        if st.button("Mettre à jour le rôle", key="update_role_button"):
            try:
                update_account(user_to_update, new_role=new_role)
                st.success(f"✅ Rôle de '{user_to_update}' mis à jour en {new_role}.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

    elif action == "Supprimer utilisateur":
        user_to_delete = st.selectbox("Utilisateur", all_accounts, key="delete_user")
        confirm_delete = st.checkbox(f"Confirmer la suppression de '{user_to_delete}'", key="confirm_delete")
        if st.button("Supprimer", key="delete_button") and confirm_delete:
            try:
                delete_account(user_to_delete)
                st.success(f"✅ Compte '{user_to_delete}' supprimé.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")