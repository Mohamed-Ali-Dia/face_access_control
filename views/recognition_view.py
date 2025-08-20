import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoTransformerBase
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from controller import recognize_faces
import os

# ---------------------
# Helpers
# ---------------------
def get_font(font_size: int):
    """Retourne une police dispo (Arial si présent, sinon DejaVuSans)."""
    try:
        return ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        return ImageFont.truetype("DejaVuSans.ttf", font_size)

def put_text_pil(img, text, pos, font_size=20, color=(0,255,0)):
    """Ajoute du texte avec Pillow pour un rendu net."""
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = get_font(font_size)
    draw.text(pos, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# ---------------------
# Vue principale
# ---------------------
def recognition_tab():
    # ---------------------
    # Transformer WebRTC
    # ---------------------
    class FaceRecognitionTransformer(VideoTransformerBase):
        def __init__(self):
            self.last_name = None

        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            height, width = img.shape[:2]

            results, alert = recognize_faces(img)

            # Détection principale
            if results:
                main_name = next((name for (_, name) in results if name != "Inconnu"), "Inconnu")
            else:
                main_name = "Pas de visage détecté"

            self.last_name = main_name

            # Dessin rectangles
            for ((top, right, bottom, left), detected_name) in results:
                color = (0, 255, 0) if detected_name != "Inconnu" else (0, 0, 255)
                thickness = max(2, width // 200)
                cv2.rectangle(img, (left, top), (right, bottom), color, thickness)

            # Texte HUD
            if main_name == "Inconnu":
                hud_text = "Accès refusé : visage inconnu"
                hud_color = (0, 0, 255)
            elif main_name == "Pas de visage détecté":
                hud_text = "Pas de visage détecté"
                hud_color = (255, 255, 0)
            else:
                hud_text = f"Accès autorisé : {main_name}"
                hud_color = (0, 255, 0)

            # Taille texte adaptative
            font_size = max(14, min(width // 25, 32))
            font = get_font(font_size)
            text_w, text_h = font.getbbox(hud_text)[2:]

            hud_x = (width - text_w) // 2
            hud_y = 20  # un petit décalage sous le bord

            # Bandeau semi-transparent noir
            overlay = img.copy()
            cv2.rectangle(overlay,
                        (hud_x - 10, hud_y - 5),
                        (hud_x + text_w + 100, hud_y + text_h + 10),
                        (0, 0, 0), -1)
            img = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)

            # Ajout texte
            img = put_text_pil(img, hud_text, (hud_x, hud_y), font_size=font_size, color=hud_color)

            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
    # --- Container fixe pour la vidéo ---
    with st.container():
        # Message juste au-dessus de la vidéo
        st.markdown("""
            <div style="text-align:center; margin-bottom:0.5vw;">
                <p style="font-size:1.2vw; background-color:#d1ecf1; color:#0c5460; padding:6px; border-radius:5px">
                💡 Placez-vous face à la caméra pour que le système détecte et reconnaisse votre visage.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # CSS pour réduire les marges internes
        st.markdown("""
        <style>
        /* Réduire espace au-dessus et en dessous du composant webrtc_streamer */
        .streamlit-expanderHeader, .stButton, .stMarkdown, .stContainer {
            margin-top: 0px !important;
            margin-bottom: 0px !important;
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }

        /* Container vidéo fixe */
        .video-container {
            width: 400px;
            height: 300px;
            margin: 0 auto;
        }
        .video-container video {
            width: 100% !important;
            height: 100% !important;
            object-fit: cover;
        }
        </style>
        """, unsafe_allow_html=True)

        # Wrapper HTML pour vidéo
        st.markdown('<div class="video-container">', unsafe_allow_html=True)

        ctx = webrtc_streamer(
            key="recognition",
            mode=WebRtcMode.SENDRECV,
            video_transformer_factory=FaceRecognitionTransformer,
            media_stream_constraints={
                "video": {"width": 640, "height": 480},
                "audio": False
            },
            async_transform=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

        if ctx.state.playing is None or not ctx.state.playing:
            st.warning("⚠️ Veuillez cliquer sur Start pour activer la caméra.")