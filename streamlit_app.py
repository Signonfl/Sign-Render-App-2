import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tempfile
import os
from streamlit_drawable_canvas import st_canvas

# App configuration
st.set_page_config(page_title="Sign Render App", layout="wide")

# Load and display brand logo
logo_path = "/mnt/data/1. Sign On Logo-tran-2.png"
try:
    logo_main = Image.open(logo_path).convert("RGBA")
    st.image(logo_main, width=150)
except:
    pass

st.title("Custom Sign Design Rendering to Scale")

# --- Sidebar ---
st.sidebar.header("Branding & Inputs")
logo_file_app = st.sidebar.file_uploader("Upload brand logo", type=["png","jpg","jpeg"])
if logo_file_app:
    st.sidebar.image(Image.open(logo_file_app).convert("RGBA"), use_column_width=True)

# Upload inputs
bg_file = st.sidebar.file_uploader("Upload background image", type=["png","jpg","jpeg"])
calib_label = st.sidebar.text_input("Calibration object name (e.g. door)", value="door")

st.sidebar.markdown("---")
# Step 1: calibration
st.sidebar.subheader("Calibration")
real_h = st.sidebar.number_input(f"{calib_label} real height (inches)", min_value=1.0, value=80.0)

# Step 2: sign dimensions
st.sidebar.subheader("Sign Dimensions")
sign_w_in = st.sidebar.number_input("Sign width (inches)", min_value=1.0, value=48.0)
sign_h_in = st.sidebar.number_input("Sign height (inches)", min_value=1.0, value=12.0)

# Step 3: text options with font selection
st.sidebar.subheader("Text Overlay & Fonts")
use_text = st.sidebar.checkbox("Enable text overlay")
text_value = st.sidebar.text_input("Text to render")
# Preloaded fonts
preloaded_fonts = {
    "Arial": "fonts/Arial.ttf",
    "Arial Bold": "fonts/Arial Bold.ttf",
    "Arial Black": "fonts/Arial Black.ttf",
    "Futura": "fonts/Futura.ttf"
}
font_choice = st.sidebar.selectbox("Font", list(preloaded_fonts.keys()) + ["Custom upload"])
custom_font_file = None
if font_choice == "Custom upload":
    custom_font_file = st.sidebar.file_uploader("Upload font (.ttf)", type=["ttf"], key="fontfile")
font_h_in = st.sidebar.number_input("Text height (inches)", min_value=1.0, value=12.0)
text_color = st.sidebar.color_picker("Text color", "#FFFFFF")
stroke_col = st.sidebar.color_picker("Stroke color", "#000000")
stroke_w = st.sidebar.slider("Stroke width", 0, 10, 1)
letter_sp = st.sidebar.number_input("Letter spacing (px)", min_value=0, value=0)

# Step 4: placement & dims
off_x_pct = st.sidebar.number_input("X offset (%)", 0.0, 100.0, 50.0)
off_y_pct = st.sidebar.number_input("Y offset (%)", 0.0, 100.0, 50.0)
show_dims = st.sidebar.checkbox("Show overlay dimensions")

# Main workflow
if bg_file:
    # Load background
    bg = Image.open(bg_file).convert("RGBA")
    bg_w, bg_h = bg.size

    # Calibration canvas
    st.subheader("Step 1: Draw a box around the calibration object")
    calib_canvas = st_canvas(
        background_image=bg,
        update_streamlit=True,
        height=bg_h,
        width=bg_w,
        drawing_mode="rect",
        key="calib_canvas"
    )

    px_per_in = None
    if getattr(calib_canvas, 'json_data', None) and calib_canvas.json_data.get("objects"):
        obj = calib_canvas.json_data["objects"][0]
        obj_h = obj.get("height", 0)
        if obj_h > 0 and real_h > 0:
            px_per_in = obj_h / real_h
            st.success(f"Calibration: {px_per_in:.2f} pixels per inch")

    if px_per_in:
        overlay = Image.new("RGBA", (bg_w, bg_h), (255,255,255,0))
        # Sign overlay
        sign_w_px = int(sign_w_in * px_per_in)
        sign_h_px = int(sign_h_in * px_per_in)
        x = int((off_x_pct/100)*(bg_w-sign_w_px))
        y = int((off_y_pct/100)*(bg_h-sign_h_px))

        sign_file = st.sidebar.file_uploader("Upload sign mockup", type=["png","jpg","jpeg"], key="sign_upload")
        if sign_file:
            sign_img = Image.open(sign_file).convert("RGBA")
            sign_resized = sign_img.resize((sign_w_px, sign_h_px), Image.ANTIALIAS)
            overlay.paste(sign_resized, (x,y), sign_resized)

        # Text overlay
        if use_text and text_value:
            text_h_px = int(font_h_in * px_per_in)
            if font_choice != "Custom upload":
                font_path = preloaded_fonts[font_choice]
                font = ImageFont.truetype(font_path, text_h_px)
            else:
                try:
                    font = ImageFont.truetype(custom_font_file, text_h_in)
                except:
                    font = ImageFont.load_default()
            dummy = ImageDraw.Draw(Image.new("RGBA", (1,1)))
            tw, th = dummy.textsize(text_value, font)
            txt_img = Image.new("RGBA", (tw + letter_sp * len(text_value), th), (255,255,255,0))
            d = ImageDraw.Draw(txt_img)
            cx = 0
            for ch in text_value:
                d.text((cx,0), ch, font=font, fill=text_color, stroke_width=stroke_w, stroke_fill=stroke_col)
                cx += dummy.textsize(ch, font)[0] + letter_sp
            overlay.paste(txt_img, (x,y), txt_img)

        comp = Image.alpha_composite(bg, overlay)
        if show_dims:
            d2 = ImageDraw.Draw(comp)
            d2.rectangle([(x,y),(x+sign_w_px, y+sign_h_px)], outline="red", width=2)
            d2.text((x, y-sign_h_px*0.05), f'{sign_w_in}" x {sign_h_in}"', fill="red")
        st.subheader("Rendered Mockup")
        st.image(comp, use_column_width=True)
else:
    st.info("Upload a background image to begin.")

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Custom Sign AI")
