"""Data extraction from a PDF table with semi-structured layout."""
import tempfile
from io import StringIO
import tabula
import camelot
import pandas as pd
import numpy as np
import pdftotext
from PIL import Image, ImageFont, ImageDraw
from pdf2image import convert_from_path
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import dataframe_image as dfi
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# %%

pd.set_option('display.max_colwidth', None)


# %%

def make_df_image(table,
                  max_cols=-1,
                  max_rows=-1):
    """Return dataframe as image."""
    with tempfile.NamedTemporaryFile(suffix='.jpg',
                                     delete=False) as tmp:
        dfi.export(table, tmp.name, max_cols=max_cols, max_rows=max_rows)
        image = mpimg.imread(tmp.name)
        return image


def make_lines_image(lines,
                     mrgn=15,
                     background=(0, 0, 0),
                     text_color=(255, 255, 255),
                     font_size=8):
    """Return raw text in lines as image."""
    lines = pd.Series(lines)
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
    for n, line in enumerate(lines):
        y = y0 + n * line_height
        draw.text((x, y), line, text_color, monospace)
    return image


# %%

PDF = 'example_ready/example.pdf'
pdf_img = convert_from_path(PDF)[0]

plt.axis('off')
plt.imshow(pdf_img)

# %%

tabula_df = (tabula
             .read_pdf(PDF,
                       stream=True,
                       pages="all"))

camelot_df = (camelot
              .read_pdf(PDF,
                        flavor="stream",
                        suppress_stdout=True,
                        pages="all")
              [0].df)


fig, ax = plt.subplots(2, 1)
titles = ['tabula 2.2.0', 'camelot 0.8.2']
for i, img in enumerate(map(make_df_image, [tabula_df, camelot_df])):
    ax[i].axis("off")
    ax[i].set_adjustable("box")
    ax[i].title.set_text(titles[i])
    ax[i].imshow(img)
fig.tight_layout()

# %%

pdfminer_string = StringIO()
with open(PDF, "rb") as in_file:
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr,
                           pdfminer_string,
                           laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
pdfminer_lines = pdfminer_string.getvalue().splitlines()
pdfminer_lines = [ln for ln in pdfminer_lines if ln]

with open(PDF, 'rb') as file:
    pdftotext_string = pdftotext.PDF(file)
pdftotext_lines = ("\n\n".join(pdftotext_string).splitlines())
pdftotext_lines = [ln for ln in pdftotext_lines if ln]

fig, ax = plt.subplots(2, 1)
titles = ['pdfminer.six 20201018', 'pdftotext 2.1.5']
for i, img in enumerate(map(make_lines_image,
                            [pdfminer_lines, pdftotext_lines])):
    ax[i].axis("off")
    ax[i].set_adjustable("box")
    ax[i].title.set_text(titles[i])
    ax[i].imshow(img)
fig.tight_layout()


# %%

def adjust_string(s, out_width):
    """Pad string with whitespaces to the right.

    It wil make current string of the same length as longest
    string in a series. Needed further to evenly split strings
    into columns on a divider such as empty vertical-wise
    string through all the rows.
    """
    fill_width = out_width - len(s)
    s += ' ' * fill_width
    return s


def concat_cols_on_condition(table, filter_func, iterable=None):
    """Concatenate columns of a given dataframe on some condition."""
    if iterable is None:
        iterable = table
    for col in table.columns:
        if filter_func(iterable,
                       col):
            prev_col_idx = table.columns.get_loc(col) - 1
            prev_col = table.columns[prev_col_idx]
            table[prev_col] = table[[prev_col, col]].agg(' '.join, axis=1)
            table.drop([col], axis=1, inplace=True)
    return table


def add_postfix_after(in_list):
    """Rename duplicates in a given list.

    in:
        print(add_postfix_after([0, 1, 2, 2, 3, 3, 3, 4, 5, 6, 6]))
    out:
        ['0', '1', '2', '2_1', '3', '3_1', '3_2', '4', '5', '6', '6_1']

    Needed to further compare list of columns with added ones to the
    index of original columns.
    """
    out_list = []
    x = 0
    while x < len(in_list) - 1:
        if in_list[x] != in_list[x + 1]:
            out_list.append(str(in_list[x]))
            x += 1
        else:
            out_list.append(str(in_list[x]))
            y = 1
            while x + y < len(in_list):
                if in_list[x] == in_list[x + y]:
                    out_list.append("{}_{}".format(in_list[x], y))
                    y += 1
                else:
                    break
            x += y
    if x == len(in_list) - 1:
        out_list.append(str(in_list[-1]))
    return out_list


# %%

# get matrix with all elements of a string including spaces
# to further search for a vertical empty string through all the rows
pdf_lines = pd.Series(pdfminer_lines)
max_width = pdf_lines.str.len().max()
pdf_lines_adjusted = pdf_lines.apply(adjust_string, args=(max_width, ))
pdf_lines_mtx = np.stack(pdf_lines_adjusted.map(list).to_numpy())

# indicies of empty vertical strings as column dividers
whitespace_сols = np.where(np.all(pdf_lines_mtx == ' ', axis=0))[0]
rightmost_whitespace_cols = np.where(np.diff(whitespace_сols) != 1)[0]
column_dividers = np.append(whitespace_сols[rightmost_whitespace_cols],
                            whitespace_сols[-1])

# %%

df_mtx = pd.DataFrame(pdf_lines_mtx)
df_mtx_w_dividers = df_mtx.copy()

df_mtx_w_dividers.loc[:, column_dividers] = (df_mtx_w_dividers[column_dividers]
                                             .replace({' ': '\u2022'}))

fig, ax = plt.subplots(2, 1)
titles = ['char matrix ...', '... with rightmost column dividers']
for i, img in enumerate([make_df_image(d, max_cols=60)
                         for d in [df_mtx, df_mtx_w_dividers]]):
    ax[i].axis("off")
    ax[i].set_adjustable("box")
    ax[i].title.set_text(titles[i])
    ax[i].imshow(img)
fig.tight_layout()

# %%

splitted_lines = []
for row in pdf_lines_adjusted:
    current_row = []
    for e in range(len(column_dividers) - 1):
        if e == 0:
            current_row.append(row[: column_dividers[e]].strip())
        (current_row
         .append(row[column_dividers[e]: column_dividers[e + 1]]
                 .strip()))
    current_row.append(row[column_dividers[-1]:].strip())
    splitted_lines.append(current_row)

# %%

pdf_df = pd.DataFrame(splitted_lines)
empty_cols = (pdf_df == '').all()
pdf_df = pdf_df[pdf_df.columns[~empty_cols]]

plt.axis('off')
plt.imshow(make_df_image(pdf_df))

# %%

header_row = pdf_df.iloc[0, :].copy()
table_rows = pdf_df.iloc[1:, :].copy()

odd_rows = table_rows.iloc[::2].copy()
odd_rows.reset_index(drop=True, inplace=True)

evn_rows = table_rows[1::2].copy()
evn_rows.reset_index(drop=True, inplace=True)

evn_rows.replace({'': np.nan}, inplace=True)
evn_rows.dropna(axis=1, how='all', inplace=True)

all_rows = pd.concat([odd_rows, evn_rows], axis=1, sort=True)
all_rows.sort_index(axis=1, inplace=True)
all_rows.columns = all_rows.columns.astype(str)
all_rows.reset_index(drop=True, inplace=True)
all_rows.replace({np.nan: ''}, inplace=True)

fig, ax = plt.subplots(2, 1)
titles = ['original layout', 'flatten layout']
for i, img in enumerate(map(make_df_image, [table_rows, all_rows])):
    ax[i].axis("off")
    ax[i].set_adjustable("box")
    ax[i].title.set_text(titles[i])
    ax[i].imshow(img)
fig.tight_layout()

# %%

# columns with underscored indicies got from splitting original names by '/'
header_splitted = header_row.str.split('/')

header_indicies = []
for i, element in enumerate(header_splitted):
    if len(element) == 1:
        header_indicies.append(str(i))
    else:
        for j, w in enumerate(element):
            if j == 0:
                header_indicies.append(str(i))
            else:
                header_indicies.append('{}_{}'.format(i, j))

header_elements = [item for sublist in header_splitted
                   for item in sublist]

column_names = pd.Series(data=header_elements,
                         index=header_indicies)

# %%

all_rows.columns = add_postfix_after(all_rows.columns.astype(int).tolist())

plt.axis('off')
plt.imshow(make_df_image(all_rows, max_rows=3))


# %%

final_table = concat_cols_on_condition(table=all_rows,
                                       iterable=column_names.index,
                                       filter_func=lambda iterable, element:
                                           str(element) not in iterable)

final_table.columns = column_names[final_table.columns]

fig, ax = plt.subplots(2, 1)
titles = ['semi-structured data', 'structured data']
for i, img in enumerate([make_lines_image(pdfminer_lines),
                         make_df_image(final_table)]):
    ax[i].axis("off")
    ax[i].set_adjustable("box")
    ax[i].title.set_text(titles[i])
    ax[i].imshow(img)
fig.tight_layout()
