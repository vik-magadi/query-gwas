from bokeh.plotting import figure, output_file, save, ColumnDataSource
from bokeh.models.tickers import FixedTicker
import sqlite3  as sql
import numpy as np
import pandas as pd

mydir = "/usr/src/app/templates/"

def plot_variant(connection, var):

    mydir = "/usr/src/app/templates/"
    output_file(filename = mydir + "plot_variant_" + var + ".html")

    con = sql.connect(connection)
 
    join = con.cursor()
    join.execute("CREATE VIEW joined AS SELECT * FROM regenie LEFT OUTER JOIN variant ON regenie.Name = variant.tagsampler__samples;")
 
    
    cur = con.cursor()
    cur.execute("SELECT Trait, Pval FROM joined WHERE Name = (?)", (var,))
    
    rows = cur.fetchall()
    
    names = list(zip(*rows))[0]
    pvals = np.array(list(zip(*rows))[1])
  
    p = figure(x_range = names, title = "P-values of variant " + var, x_axis_label = "Traits associated with variant", y_axis_label = "-log10 of P-values")
    
    p.vbar(x=names, top=-np.log10(pvals), width=0.9)
    save(p)
    
    drop = con.cursor()
    drop.execute("DROP VIEW joined;")
    con.close()
    return "plot_variant_" + var + ".html"


def plot_gene(connection, gene):
    mydir = "/usr/src/app/templates/"
    
    output_file(filename = mydir + "plot_gene_" + gene + ".html")

    con = sql.connect(connection)
    
    join = con.cursor()
    join.execute("CREATE VIEW joined AS SELECT * FROM regenie LEFT OUTER JOIN variant ON regenie.Name = variant.tagsampler__samples;")
 
    get_var = con.cursor()
    get_var.execute("SELECT DISTINCT Name FROM joined WHERE base__hugo = (?)", (gene,))
    var_list = get_var.fetchall()
    
    p = []
    for var in var_list:
        v = var[0]
        cur = con.cursor()
        cur.execute("SELECT Trait, Pval FROM joined WHERE Name = (?)", (v,))
    
        rows = cur.fetchall()
    
        names = list(zip(*rows))[0]
        pvals = np.array(list(zip(*rows))[1])
  
        fig = figure(x_range = names, title = "P-values of variant " + v, x_axis_label = "Traits associated with variant", y_axis_label = "-log10 of P-values")
    
        fig.vbar(x=names, top=-np.log10(pvals), width=0.9)
        
        p.append(fig)
    
    drop = con.cursor()
    drop.execute("DROP VIEW joined;")
    con.close()
    save(p)
    return "plot_gene_" + gene + ".html"

def plot_trait(connection, trait):
    
    mydir = "/usr/src/app/templates/"
    output_file(filename =  mydir + "plot_trait_" + trait + ".html")

    con = sql.connect(connection)
    
    join = con.cursor()
    join.execute("CREATE VIEW joined AS SELECT * FROM regenie LEFT OUTER JOIN variant ON regenie.Name = variant.tagsampler__samples;")
    
    get_var = con.cursor()
    get_var.execute("SELECT DISTINCT Chr, Pos, Pval, Name FROM joined WHERE Trait = (?)", (trait,))
    var_list = get_var.fetchall()
    
    positions = pd.DataFrame(data = {"Chr": list(zip(*var_list))[0], "Pos" : list(zip(*var_list))[1],
                                     "Pval": list(zip(*var_list))[2], "Name" :list(zip(*var_list))[3]})
    positions = positions.sort_values(by=['Chr', 'Pos'])
    positions['rel_pos'] = [0.0]*len(positions)
    i = 0
    while i < len(positions):
        chromosome = positions.loc[positions['Chr']==positions['Chr'][i]]
        for j in range(len(chromosome)):
            x = positions['Chr'][i+j] + (1.0/len(chromosome))*j
            positions.at[i+j, 'rel_pos'] = x
        i += len(chromosome)
    
    
    source = ColumnDataSource(data=dict(
    x = positions['rel_pos'],
    y = -np.log10(np.array(positions['Pval'])),
    pvals = positions['Pval'],
    name=positions['Name']))
    
    TOOLTIPS = [
    ("Variant", "@name"),
    ("P-value", "@pvals")]
    
  
    fig = figure(x_range = [1,23], title = "P-values of trait " + trait, x_axis_label = "Chromosome", 
                 y_axis_label = "-log10 of P-values",tooltips = TOOLTIPS)
    fig.xaxis.ticker = FixedTicker(ticks = np.arange(1,24))
    fig.circle('x', 'y', source= source, size = 10, color = "#28aae0")
    
    
    drop = con.cursor()
    drop.execute("DROP VIEW joined;")
    con.close()
    save(fig)
    return "plot_trait_" + trait + ".html"
    
#plot_trait("var_m30_4oc.txt.sqlite", "E80_PROXY")




