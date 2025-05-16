import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
# (Optional) For drag-and-drop placement UI
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Sign Render App", layout="wide")
st.title("Custom Sign Design Rendering to Scale")

# Sidebar inputs
bg_file = st.sidebar.file_uploader("Upload background image (building/sign)", type=["png", "jpg", "jpeg"])
sign_file = st.sidebar.file_uploader("Upload signage mockup image (with transparency recommended)", type=["png", "jpg", "jpeg"])
st.sidebar.markdown("---")

# Real-world background dimensions (in inches)
bg_width_in = st.sidebar.number_input("Background real width (inches)", min_value=1.0, value=240.0)
bg_height_in = st.sidebar.number_input("Background real height (inches)", min_value=1.0, value=120.0)

# Calibration using known object measurement
H_px = st.sidebar.number_input("Measured object pixel height", min_value=1, value=100)
H_in = st.sidebar.number_input("Measured object real height (inches)", min_value=1.0, value=80.0)
px_per_in = H_px / H_in if H_in else 0

st.sidebar.markdown("---")
# Overlay and styling options
use_mockup = st.sidebar.checkbox("Use mockup image overlay", value=True)
use_text = st.sidebar.checkbox("Use text overlay", value=False)
use_dragdrop = st.sidebar.checkbox("Enable drag-and-drop placement", value=False)
show_measure = st.sidebar.checkbox("Show measurement annotations", value=False)

# Mockup dimensions
sign_width_in = st.sidebar.number_input("Sign real width (inches)", min_value=1.0, value=48.0)
sign_height_in = st.sidebar.number_input("Sign real height (inches)", min_value=1.0, value=12.0)

# Text styling inputs
text_input = st.sidebar.text_input("Enter sign text")
font_file = st.sidebar.file_uploader("Upload font (.ttf)", type=["ttf"])
font_size_in = st.sidebar.number_input("Text height (inches)", min_value=1.0, value=12.0)
text_color = st.sidebar.color_picker("Text Color", "#FFFFFF")
stroke_color = st.sidebar.color_picker("Text Stroke Color", "#000000")
stroke_width = st.sidebar.slider("Text Stroke Width (px)", 0, 10, 1)
letter_spacing = st.sidebar.number_input("Letter Spacing (px)", min_value=0, value=0)

# Manual offset if not using drag-and-drop
off_x = st.sidebar.number_input("Overlay X offset (% of bg)", min_value=0.0, max_value=100.0, value=50.0)
off_y = st.sidebar.number_input("Overlay Y offset (% of bg)", min_value=0.0, max_value=100.0, value=50.0)

if bg_file:
    bg = Image.open(bg_file).convert("RGBA")
    bg_w, bg_h = bg.size
    composite = bg.copy()
    x = y = None

    # Drag-and-drop placement
    if use_dragdrop:
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)", stroke_width=1,
            stroke_color="#FF0000", background_image=bg,
            update_streamlit=True, height=bg_h, width=bg_w,
            drawing_mode="transform", key="canvas"
        )
        if canvas_result.json_data and canvas_result.json_data.get("objects"):
            obj = canvas_result.json_data["objects"][0]
            x = int(obj.get("left", 0))
            y = int(obj.get("top", 0))

    # Mockup overlay
    if use_mockup and sign_file:
        sign = Image.open(sign_file).convert("RGBA")
        w_px = int(sign_width_in * px_per_in)
        h_px = int(sign_height_in * px_per_in)
        sign_resized = sign.resize((w_px, h_px), Image.ANTIALIAS)
        if x is None or y is None:
            x = int(off_x/100 * (bg_w - w_px))
            y = int(off_y/100 * (bg_h - h_px))
        composite.paste(sign_resized, (x, y), sign_resized)

    # Text overlay
    if use_text and text_input:
        font_px = int(font_size_in * px_per_in)
        try:
            font = ImageFont.truetype(font_file, size=font_px) if font_file else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        dummy = Image.new("RGBA", (1, 1))
        draw_dummy = ImageDraw.Draw(dummy)
        # Measure and create spaced text image
        text_w, text_h = draw_dummy.textsize(text_input, font=font)
        text_img = Image.new("RGBA", (text_w + letter_spacing*len(text_input), text_h), (0,0,0,0))
        draw = ImageDraw.Draw(text_img)
        cursor_x = 0
        for ch in text_input:
            draw.text((cursor_x, 0), ch, font=font, fill=text_color,
                      stroke_width=stroke_width, stroke_fill=stroke_color)
            cursor_x += draw_dummy.textsize(ch, font=font)[0] + letter_spacing
        if x is None or y is None:
            x = int(off_x/100 * (bg_w - text_img.width))
            y = int(off_y/100 * (bg_h - text_img.height))
        composite.paste(text_img, (x, y), text_img)

    # Measurement annotations
    if show_measure and use_mockup:
        draw2 = ImageDraw.Draw(composite)
        # Rectangle around sign
        draw2.rectangle([(x, y), (x+w_px, y+h_px)], outline="red", width=2)
        # Dimension labels
        label_w = f"{sign_width_in}""
        label_h = f"{sign_height_in}""
        # Position labels centered
        draw2.text((x + w_px/2 - len(label_w)*3, y - 20), label_w, fill="red")
        draw2.text((x + w_px + 5, y + h_px/2 - 10), label_h, fill="red")

    st.image(composite, caption="Rendered Mockup", use_column_width=True)
else:
    st.info("Upload a background image to begin.")

st.sidebar.markdown("---")
st.sidebar.markdown("Developed by Custom Sign AI | Adjust settings and preview your design.")
