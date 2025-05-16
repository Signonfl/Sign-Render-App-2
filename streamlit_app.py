import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# App configuration
st.set_page_config(page_title="Sign Render App", layout="wide")

# Load and display brand logo at top-left
logo_path = "/mnt/data/1. Sign On Logo-tran-2.png"
try:
    logo_main = Image.open(logo_path).convert("RGBA")
    st.image(logo_main, width=150)
except:
    pass

st.title("Custom Sign Design Rendering to Scale")

# --- Sidebar Branding ---
logo_file_app = st.sidebar.file_uploader("Upload your brand logo", type=["png", "jpg", "jpeg"], key="app_logo")
if logo_file_app:
    st.sidebar.image(Image.open(logo_file_app).convert("RGBA"), use_column_width=True)

st.sidebar.markdown("---")
# Upload inputs
bg_file = st.sidebar.file_uploader("Upload background image (building/sign)", type=["png", "jpg", "jpeg"], key="bg")
sign_file = st.sidebar.file_uploader("Upload signage mockup image (transparent png recommended)", type=["png", "jpg", "jpeg"], key="sign")

st.sidebar.markdown("---")
# Real-world background calibration
defined_object_px = st.sidebar.number_input("Measured object pixel height", min_value=1, value=100)
object_real_in = st.sidebar.number_input("Measured object real height (inches)", min_value=1.0, value=80.0)
px_per_in = defined_object_px / object_real_in if object_real_in else 0

# Sign dimensions for overlay
sign_w_in = st.sidebar.number_input("Sign width (inches)", min_value=1.0, value=48.0)
sign_h_in = st.sidebar.number_input("Sign height (inches)", min_value=1.0, value=12.0)

# Text overlay options
use_text = st.sidebar.checkbox("Enable text overlay", value=False)
text_value = st.sidebar.text_input("Sign text to render")
font_file = st.sidebar.file_uploader("Upload font (.ttf)", type=["ttf"])
font_h_in = st.sidebar.number_input("Text height (inches)", min_value=1.0, value=12.0)
text_color = st.sidebar.color_picker("Text color", "#FFFFFF")
stroke_col = st.sidebar.color_picker("Stroke color", "#000000")
stroke_w = st.sidebar.slider("Stroke width (px)", 0, 10, 1)
letter_sp = st.sidebar.number_input("Letter spacing (px)", min_value=0, value=0)

# Placement controls (percentage offsets)
off_x_pct = st.sidebar.number_input("X offset (% of background)", 0.0, 100.0, 50.0)
off_y_pct = st.sidebar.number_input("Y offset (% of background)", 0.0, 100.0, 50.0)

# Measurement annotation toggle
show_dims = st.sidebar.checkbox("Show overlay dimensions", value=False)

if bg_file:
    # Load background
    bg = Image.open(bg_file).convert("RGBA")
    bg_w, bg_h = bg.size
    composite = bg.copy()

    # Calculate overlay size
    sign_w_px = int(sign_w_in * px_per_in)
    sign_h_px = int(sign_h_in * px_per_in)

    # Compute position
    x = int((off_x_pct / 100) * (bg_w - sign_w_px))
    y = int((off_y_pct / 100) * (bg_h - sign_h_px))

    # Overlay sign mockup
    if sign_file:
        sign_img = Image.open(sign_file).convert("RGBA")
        sign_resized = sign_img.resize((sign_w_px, sign_h_px), Image.ANTIALIAS)
        composite.paste(sign_resized, (x, y), sign_resized)
    else:
        st.warning("Upload a sign mockup image to overlay.")

    # Overlay text
    if use_text and text_value:
        text_h_px = int(font_h_in * px_per_in)
        try:
            font = ImageFont.truetype(font_file, text_h_px) if font_file else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        draw_dummy = ImageDraw.Draw(Image.new("RGBA", (1,1)))
        txt_w, txt_h = draw_dummy.textsize(text_value, font=font)
        txt_img = Image.new("RGBA", (txt_w + letter_sp * len(text_value), txt_h), (0,0,0,0))
        d = ImageDraw.Draw(txt_img)
        cx = 0
        for ch in text_value:
            d.text((cx, 0), ch, font=font, fill=text_color, stroke_width=stroke_w, stroke_fill=stroke_col)
            cx += draw_dummy.textsize(ch, font=font)[0] + letter_sp
        composite.paste(txt_img, (x, y), txt_img)

    # Show dimensions
    if show_dims:
        dl = ImageDraw.Draw(composite)
        dl.rectangle([(x, y), (x+sign_w_px, y+sign_h_px)], outline="red", width=2)
        dl.text((x, y-20), f'{sign_w_in}" W', fill="red")
        dl.text((x+sign_w_px+5, y), f'{sign_h_in}" H', fill="red")

    # Display result
    st.image(composite, caption="Rendered Mockup", use_column_width=True)
else:
    st.info("Please upload a background image to start.")

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Custom Sign AI")
