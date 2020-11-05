# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 15:48:53 2020

@author: holomb_vv
"""

# %%

PDF = 'Purolator_Beyond_List_Q3_2020 (1).pdf'
camelot_df = (camelot
              .read_pdf(PDF,
                        flavor="stream",
                        suppress_stdout=True,
                        pages="all"))

dfs = camelot_df[5:]

new = []
for i, t in enumerate(dfs):
    if i != len(dfs[:-1]):
        new.append(t.df.iloc[4:-5])
    else:
        new.append(t.df.iloc[4:])



g = pd.concat(new)
g.replace({'': np.nan}, inplace=True)
g.dropna(axis=1, how='all', inplace=True)
# g.reset_index(drop=True, inplace=True)
g = g.apply(lambda s: s.str.replace('\n', ' '))
g.to_csv('purolator.csv')





g['new'] = g.iloc[:, 0].str.cat(g.iloc[:, 1: ], sep = ' ')


tabula_df = (tabula
             .read_pdf(PDF,
                       stream=True,
                       pages='4-322'))

f = tabula_df[~tabula_df.iloc[:, 0].str.startswith(('2020 Purolator',
                                               'Postal Code',
                                               'code postal',
                                               ))]


t = f.iloc[:, 0].str.split(' ', 4, True)

n = t.iloc[:, 0].str.cat(t.iloc[:, 1], ' ')

result = pd.concat([n, t.iloc[:, 2:], f.iloc[:, 1:]], axis=1, sort=False)

k = result.iloc[:, 5].str.split(' ', expand=True)
h = pd.concat([result.iloc[:, :5], k, result.iloc[:, -1]], axis=1, sort=False)

df = (tabula
             .read_pdf(PDF,
                       stream=True,
                       pages='323'))
f2 = df[~df.iloc[:, 0].str.startswith(('2020 Purolator',
                                               'Postal Code',
                                               'code postal',
                                               ))]
t2 = f2.iloc[:, 0].str.split(' ', 4, True)
n2 = t2.iloc[:, 0].str.cat(t2.iloc[:, 1], ' ')
result2 = pd.concat([n2, t2.iloc[:, 2:], f2.iloc[:, 1:]], axis=1, sort=False)

a = pd.concat([result, result2])
a.dropna(axis=1, how='all', inplace=True)
a.columns = range(a.shape[1])
a.to_csv('purolator.csv', index=False)
m = a.iloc[:, 5].str.split(' ', expand=True)
b = pd.concat([a.iloc[:, :5], m, a[6]], axis=1)
b.columns = range(b.shape[1])
b1 = b.iloc[:, :4]
b1.columns=range(4)
b2 = b.iloc[:, 4:]
b2.columns=range(4)

v = pd.concat([b1, b2], axis=1, ignore_index=True)

b3 = b1.append(b2)
b3.dropna(axis=0, how='all', inplace=True)
b3.sort_values(by=0, inplace=True)
b3.to_csv('purolator_new.csv', index=False)
