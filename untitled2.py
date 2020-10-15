# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 17:48:18 2020

@author: holomb_vv
"""

import matplotlib.pyplot as plt
from PIL import Image, ImageFont, ImageDraw

# %%

def make_pdf_image(lines,
                   mrgn=15,
                   background=(0, 0, 0),
                   text_color=(255, 255, 255),
                   font_size=8):

    longest_line = lines[lines.str.len().idxmax()]

    image = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(image)

    monospace = ImageFont.truetype(r'С:\Windows\Fonts\cour.ttf', font_size)
    line_width, line_height = draw.textsize(longest_line, monospace)

    img_width, img_height = (line_width + mrgn * 2,
                             len(lines) * line_height + mrgn * 2)

    image = Image.new("RGBA", (img_width, img_height), background)
    draw = ImageDraw.Draw(image)

    x, y0 = (mrgn, mrgn)
    for j, line in enumerate(lines):
        y = y0 + j * line_height
        draw.text((x, y), line, text_color, monospace)

    return image


# %%

fig, ax = plt.subplots(1, 1)
ax.axis("off")
ax.imshow(make_pdf_image(table_cln.copy()))

# %%
