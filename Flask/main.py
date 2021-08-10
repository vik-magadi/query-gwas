from flask import Flask, render_template, request
import sqlite3 as sql
import re
import plots

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/query/', methods = ["POST","GET"])
def query():
    query = request.form['query']

    search_term = request.form['search_term']
         
    c = sql.connect("var_m30_4oc.txt.sqlite")
    c.row_factory = sql.Row
    
    join = c.cursor()
    join.execute("CREATE VIEW joined AS SELECT * FROM regenie LEFT OUTER JOIN variant ON regenie.Name = variant.tagsampler__samples;")
    drop = c.cursor()
 
    con = sql.connect("var_m30_4oc.txt.sqlite")
    con.row_factory = sql.Row
    if query == 'variant':
        cur = con.cursor()
        cur.execute("SELECT DISTINCT * FROM joined WHERE Name =:s",{"s": search_term})
           
        rows = cur.fetchall(); 
        drop.execute("DROP VIEW joined")   
        return render_template("variant.html",rows = rows)
    
    if query == 'gene':
        cur = con.cursor()
        cur.execute("SELECT DISTINCT base__hugo, Name, Chr, Pos, Ref, Alt, Pval, Trait FROM joined WHERE base__hugo =:s",{"s": search_term})
           
        rows = cur.fetchall(); 
        drop.execute("DROP VIEW joined") 
        return render_template("gene.html",rows = rows)
    
    if query == 'trait':
       con.create_function("regexp", 2, lambda x, y: 1 if re.search(x,y) else 0)
       cur = con.cursor()
       cur.execute("SELECT * FROM joined WHERE Trait REGEXP ?",(search_term,))
       rows = cur.fetchall()
       drop.execute("DROP VIEW joined") 
       return render_template("trait.html",rows=rows)
   
@app.route('/variant/plot/',methods = ["POST","GET"])
def var_plot():
    
    return render_template(plots.plot_variant("var_m30_4oc.txt.sqlite", request.form["variant"]))

@app.route('/gene/plot/',methods = ["POST","GET"])
def gene_plot():
    
    return render_template(plots.plot_gene("var_m30_4oc.txt.sqlite", request.form["gene_name"]))

@app.route('/trait/plot/',methods = ["POST","GET"])
def trait_plot():
    
    return render_template(plots.plot_trait("var_m30_4oc.txt.sqlite", request.form["trait"]))
    


   
if __name__ == '__main__':
   app.run(debug = True)