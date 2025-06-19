from PIL import ImageFont, ImageDraw, Image
import numpy as np
import cv2

def draw_nepali_text_on_frame(frame, text, position, font_path="fonts/NotoSansDevanagari-Regular.ttf", font_size=32, color=(255, 0, 0)):
    # Convert OpenCV image (BGR) to PIL image (RGB)
    cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im_rgb)

    # Load font and create draw object
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(pil_im)

    # Draw text on image
    draw.text(position, text, font=font, fill=color)

    # Convert back to OpenCV image (BGR)
    frame_with_text = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
    return frame_with_text
