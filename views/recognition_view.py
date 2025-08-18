# debut du fichier arecognition_view.py
from networkx import draw
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoTransformerBase
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from controller import recognize_faces

def put_text_pil(img, text, pos, font_path="arial.ttf", font_size=None, color=(0,255,0)):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    if font_size is None:
        font_size = max(12, img.shape[1] // 30)  # adaptatif à la largeur
    font = ImageFont.truetype(font_path, font_size)
    draw.text(pos, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

class FaceRecognitionTransformer(VideoTransformerBase):
    def __init__(self):
        self.last_name = None
        self.active = True

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        height, width = img.shape[:2]

        results, alert = recognize_faces(img)

        # Nom principal
        main_name = None
        if results:
            for (_, detected_name) in results:
                if detected_name != "Inconnu":
                    main_name = detected_name
                    break
            if not main_name:
                main_name = "Inconnu"
        else:
            main_name = "Pas de visage détecté"

        self.last_name = main_name

        # Dessin rectangles adaptatifs semi-transparents
        for ((top, right, bottom, left), detected_name) in results:
            color = (0, 255, 0) if detected_name != "Inconnu" else (0, 0, 255)
            thickness = max(1, width // 300)
            overlay = img.copy()
            cv2.rectangle(overlay, (left, top), (right, bottom), color, thickness)
            alpha = 0.4
            img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

        # HUD centré adaptatif avec padding
        if main_name == "Inconnu":
            hud_text = "Accès refusé : visage inconnu"
            hud_color = (0, 0, 255)
        elif main_name == "Pas de visage détecté":
            hud_text = "Pas de visage détecté"
            hud_color = (255, 255, 0)
        else:
            hud_text = f"Accès autorisé : {main_name}"
            hud_color = (0, 255, 0)

        font_size = max(14, min(width // 25, 32))  # texte adaptatif mais jamais trop grand ni trop petit
        text_w, text_h = draw.textsize(hud_text, font=ImageFont.truetype("arial.ttf", font_size))

        hud_x = (width - text_w) // 2
        hud_y = 0  # top padding pour le HUD

        overlay = img.copy()
        cv2.rectangle(overlay, (hud_x - 20, hud_y - 10), (hud_x + text_w + 20, hud_y + text_h + 10), (0, 0, 0), -1)
        img = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)

        img = put_text_pil(img, hud_text, (hud_x, hud_y), font_size=font_size, color=hud_color)

        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def recognition_tab():
    if "recognized_name" not in st.session_state:
        st.session_state["recognized_name"] = None
    if "recognized_done" not in st.session_state:
        st.session_state["recognized_done"] = False

    # Conteneur avec padding automatique
    with st.container():
        st.markdown("""
            <div style="text-align:center; margin-bottom:1.5vw;">
                <p style="color:#1e3a8a; font-size:1.2vw; word-wrap: break-word;background-color:#d1ecf1; color:#0c5460; padding:8px; border-radius:5px">
                    💡 Placez-vous face à la caméra pour que le système détecte et reconnaisse votre visage.
                </p>
            </div>
            """, unsafe_allow_html=True)

        ctx = webrtc_streamer(
            key="recognition",
            mode=WebRtcMode.SENDRECV,
            video_transformer_factory=FaceRecognitionTransformer,
            media_stream_constraints={"video": {"width": 640, "height": 240}, "audio": False},
            async_processing=True
        )

        if ctx and ctx.video_transformer and ctx.video_transformer.last_name:
            name = ctx.video_transformer.last_name
            if name and name != "Pas de visage détecté":
                if name != "Inconnu":
                    st.success(f"Accès autorisé : {name}")
                else:
                    st.error("Accès refusé : visage inconnu")
            else:
                st.info("Pas de visage détecté")
# fin du fichier arecognition_view.py