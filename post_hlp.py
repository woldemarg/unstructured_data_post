import random
import string

from fpdf import FPDF



from sandbox.latest.v_08.pdf_parser_class import PDFparser

# %%

PDF = 'pdf_doc/in_all_pdf_sorted/Purchase_Order (6).PDF'

# %%

my_parser = PDFparser()

# %%

df = my_parser.get_rows_marked(PDF)

# %%

table = df.loc[df['mark'].isin(['tbl_hdr', 'tbl_row']), 0]

# %%

table_cln = (table.iloc[1:]
             .apply(lambda x: x.replace('|', ''))
             .apply(lambda x: x.replace('_', ' '))
             .reset_index(drop=True))

# %%

r = []
for i, s in enumerate(table_cln[1:]):
    n = []
    for letter in s:
        if letter.isalpha():
            n.append(random.choice(string.ascii_uppercase))
        elif letter.isdigit():
            n.append(random.randint(0, 9))
        else:
            n.append(letter)
    r.append(''.join([str(x) for x in n]))

# %%

r[:0] = [table_cln[0]]
changed = '\n'.join(r)

# %%

pdf = FPDF()
pdf.add_page(orientation="L")
pdf.set_font("Courier", size=8)
for k, st in enumerate(r):
    pdf.cell(w=0,
             h=5,
             border=0,
             align="L",
             ln=1,
             txt=st)
pdf.output("test.pdf")


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
