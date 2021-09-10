from flask import Flask, render_template, request
import sqlite3 as sql
import re
import plots
import regenie
import os


# gets the database name and text file name from the environment
db_name = "data/" + os.environ.get("db_name")
txt_name = "data/" + os.environ.get("txt_name")



app = Flask(__name__)

#home page
@app.route('/')
def home():
    return render_template("home.html")


#query results page
@app.route('/query/', methods = ["POST","GET"])
def query():
    query = request.form['query']

    search_term = request.form['search_term']
         
    c = sql.connect(db_name)
    c.row_factory = sql.Row

    #creates a table regenie in the database which contains trait information  
    regenie.reformat(txt_name, "\t",db_name)
    
    join = c.cursor()
    #combines the trait and variant information
    join.execute("CREATE VIEW joined AS SELECT * FROM regenie LEFT OUTER JOIN variant ON regenie.Name = variant.tagsampler__samples;")
    
    drop = c.cursor()
 
    con = sql.connect(db_name)
    con.row_factory = sql.Row
    
    #displays different templates based on whether the user queries by variant, gene, or trait 
    if query == 'variant':
        cur = con.cursor()
        cur.execute("SELECT DISTINCT * FROM joined WHERE Name =:s",{"s": search_term})
           
        rows = cur.fetchall(); 
        drop.execute("DROP VIEW joined")   
        drop.execute("DROP TABLE regenie")
        return render_template("variant.html",rows = rows)
    
    if query == 'gene':
        cur = con.cursor()
        cur.execute("SELECT DISTINCT base__hugo, Name, Chr, Pos, Ref, Alt, Pval, Trait FROM joined WHERE base__hugo =:s",{"s": search_term})
           
        rows = cur.fetchall(); 
        drop.execute("DROP VIEW joined") 
        drop.execute("DROP TABLE regenie")
        return render_template("gene.html",rows = rows)
    
    if query == 'trait':
       con.create_function("regexp", 2, lambda x, y: 1 if re.search(x,y) else 0)
       cur = con.cursor()
       cur.execute("SELECT * FROM joined WHERE Trait REGEXP ?",(search_term,))
       rows = cur.fetchall()
       drop.execute("DROP VIEW joined") 
       drop.execute("DROP TABLE regenie")
       return render_template("trait.html",rows=rows)
   
#bokeh plot for variant    
@app.route('/variant/plot/',methods = ["POST","GET"])
def var_plot():
    c = sql.connect(db_name)
    regenie.reformat(txt_name, "\t",db_name)
    join = c.cursor()
    #combines the trait and variant information
    join.execute("CREATE VIEW joined AS SELECT * FROM regenie LEFT OUTER JOIN variant ON regenie.Name = variant.tagsampler__samples;")
    s = render_template(plots.plot_variant(db_name, request.form["variant"]))
    
    drop = c.cursor()
    drop.execute("DROP TABLE regenie")
    drop.execute("DROP VIEW joined")
    return s
#bokeh plot for gene
@app.route('/gene/plot/',methods = ["POST","GET"])
def gene_plot():
    c = sql.connect(db_name)
    regenie.reformat(txt_name, "\t",db_name)
    join = c.cursor()
    #combines the trait and variant information
    join.execute("CREATE VIEW joined AS SELECT * FROM regenie LEFT OUTER JOIN variant ON regenie.Name = variant.tagsampler__samples;")
    s = render_template(plots.plot_gene(db_name, request.form["gene_name"]))
    
    drop = c.cursor()
    drop.execute("DROP TABLE regenie")
    drop.execute("DROP VIEW joined")
    return s
#bokeh plot for trait
@app.route('/trait/plot/',methods = ["POST","GET"])
def trait_plot():
    c = sql.connect(db_name)    
    regenie.reformat(txt_name, "\t",db_name)
    join = c.cursor()
    #combines the trait and variant information
    join.execute("CREATE VIEW joined AS SELECT * FROM regenie LEFT OUTER JOIN variant ON regenie.Name = variant.tagsampler__samples;")
    s = render_template(plots.plot_trait(db_name, request.form["trait"]))
    drop = c.cursor()
    drop.execute("DROP TABLE regenie")
    drop.execute("DROP VIEW joined")
    return s
   
   
if __name__ == '__main__':
   app.run(debug = True)