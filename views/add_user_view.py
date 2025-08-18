# debut du fichier add_user_view.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from controller import register_user_from_file, register_user_from_frame

def add_user_tab():
    st.markdown(
        '<p style="text-align:center; font-size:0.9em; background-color:#d1ecf1; color:#0c5460; padding:10px; border-radius:5px;">'
        '💡 Pour ajouter un employé : entrez son nom, puis importez une photo ou activez la webcam.'
        '</p>',
        unsafe_allow_html=True
    )
    # --- Champ unique pour le nom (en dehors des colonnes) ---
    name = st.text_input("Nom de l'employé", key="name")

    col1, col2 = st.columns([1, 2])

    # --- Colonne gauche : Importer depuis fichier ---
    with col1:
        st.markdown('<h3 style="font-size:1.2em;">📂 Importer une photo</h3>', unsafe_allow_html=True)
        photo_file = st.file_uploader("", type=["jpg", "png"], key="photo_file", accept_multiple_files=False, help="💡 Importez une photo claire de l'employé (jpg ou png)")

        if st.button("📥 Enregistrer photo", use_container_width=True):
            if name and photo_file:
                if register_user_from_file(name, photo_file):
                    st.success(f"✅ Employé **{name}** ajouté avec succès.")
                else:
                    st.error("❌ Aucun visage détecté sur la photo.")
            else:
                st.warning("⚠️ Veuillez saisir un nom et importer une photo.")

    # --- Colonne droite : Capture webcam ---
    with col2:
        st.markdown('<h3 style="font-size:1.2em;">📸 Capture via webcam</h3>', unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align:center; font-size:0.85em; background-color:#d1ecf1; color:#0c5460; padding:8px; border-radius:5px;">'
            '💡 Démarrez la webcam et placez le visage au centre avant de cliquer sur "📷 Capturer".'
            '</p>',
            unsafe_allow_html=True
        )



        class AddUserTransformer(VideoTransformerBase):
            def __init__(self):
                self.last_frame = None
            def transform(self, frame):
                self.last_frame = frame.to_ndarray(format="bgr24")
                return self.last_frame

        webrtc_ctx = webrtc_streamer(
            key="add_user",
            video_transformer_factory=AddUserTransformer,
            media_stream_constraints={"video": True, "audio": False},
            async_transform=True
        )

        if st.button("📷 Capturer et enregistrer", use_container_width=True):
            if name and webrtc_ctx.video_transformer and webrtc_ctx.video_transformer.last_frame is not None:
                frame = webrtc_ctx.video_transformer.last_frame
                if register_user_from_frame(name, frame):
                    st.success(f"✅ Employé **{name}** ajouté avec succès.")
                else:
                    st.error("❌ Aucun visage détecté.")
            else:
                st.warning("⚠️ Veuillez saisir un nom et activer la webcam si ce n'est pas activé.")
# fin du fichier add_user_view.py