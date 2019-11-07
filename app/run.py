import pandas as pd
import numpy as np
from flask import Flask
from flask import render_template, request, jsonify
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.externals import joblib
from sqlalchemy import create_engine

app = Flask(__name__)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
    return clean_tokens

def create_labels():
    labels = ["bad", "ok", "promising", "superior"]
    return labels

def create_bins(df):
    limit0 = df["Y_pred"].quantile([.0]).iloc[0]
    limit25 = df["Y_pred"].quantile([.25]).iloc[0]
    limit50 = df["Y_pred"].quantile([.5]).iloc[0]
    limit75 = df["Y_pred"].quantile([.75]).iloc[0]
    bins = [limit0, limit25, limit50, limit75, np.inf]
    return bins

# load the data
engine = create_engine("sqlite:///data/USvideos.db")
df = pd.read_sql_table("trends_data", engine)
# load the model
model = joblib.load("data/model.pkl")


@app.route("/")
@app.route("/index")

def index():
    return render_template("master.html")

# web page that handles user query and displays results
@app.route("/go")
def go():
    # save user input in query
    query = request.args.get("query", "") 
    # use model to predict a value for a query
    predicted_value = model.predict([query])
    labels = create_labels()
    bins = create_bins(df)
    # create a label based on value
    full_output = pd.cut(predicted_value, bins, labels=labels)
    # parse output to get only the label
    classification_results = full_output[0] 
    # render the go.html
    return render_template(
        "go.html",
        query=query,
        classification_result=classification_results
    )

def main():
    app.run(host="0.0.0.0", port=3000, debug=True)


if __name__ == "__main__":
    main()