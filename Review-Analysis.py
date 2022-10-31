import requests
import json
import tkinter as tk
import re
import text2emotion as te
import nltk
import ssl
from matplotlib import pyplot as plt
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

ASIN = ""
amazonloc = ""
reviewbodies = []
totalreview = ""
def press():
    global ASIN, amazonloc
    url = entry.get().strip()
    pathstatement.after(1, pathstatement.destroy)
    GETTER = re.search(
        r"^http(?:s)?.+(?:www.)(amazon\..+)/.+/dp/(.+)/.+$", url, re.IGNORECASE)
    if GETTER:
        amazonloc = GETTER.group(1)
        ASIN = GETTER.group(2)
        rainforestapi()

    else:
        wrongurlerror = tk.Label(
            text="Please enter the correct and complete URL of the Amazon Product page.")
        wrongurlerror.pack()
        wrongurlerror.after(3000, wrongurlerror.destroy)


def rainforestapi():
    global reviewbodies, totalreview
    # set up the request parameters
    params = {
        'api_key': 'CEF5302F18F0425885333125C2A2D715',
        'type': 'reviews',
        'amazon_domain': f'{amazonloc}',
        'asin': f"{ASIN}"
    }
    # make the http GET request to Rainforest API
    api_result = requests.get('https://api.rainforestapi.com/request', params)

    # store the JSON response from Rainforest API
    jsonresp = json.dumps(api_result.json())
    totaldict = json.loads(jsonresp)
    for _ in totaldict["reviews"]:
        reviewbodies.append(_["body"])
    for review in reviewbodies:
        totalreview += f". {review}"
    toppositivecomment = totaldict["top_positive"]["body"]
    topcriticalcomment = totaldict["top_critical"]["body"]
    emotionanalysis = te.get_emotion(totalreview)
    display(topcriticalcomment, toppositivecomment, emotionanalysis)

def display(critical, positive, emotions):
    plt.style.use("fivethirtyeight")
    slices = []
    labels = []
    explode = []
    maxslice = 0.0
    emotions["Uncertainity"] = emotions.pop("Fear")
    emotions["Satisfied"] = emotions.pop("Happy")
    emotions["Dissatisfied"] = emotions.pop("Sad")
    for emotion in emotions:
        labels.append(emotion)
        slices.append(emotions[emotion])
    for i in slices:
        if i > maxslice:
            maxslice = i
        explode.append(0)
    index = slices.index(maxslice)
    explode[index] = 0.1
    top = tk.Label(text=f"Top Positive Review ✨: {positive}", fg="white", bg="#DAA520")
    top.pack()
    bot = tk.Label(text=f"Top Negative Review 👎: {critical}", fg="white", bg="#CC5500")
    bot.pack()



    plt.pie(slices, labels = labels, wedgeprops={"edgecolor": "black"}, shadow= True, startangle=90, autopct='%1.1f%%', explode=explode)
    plt.title("Amazon Product Review Emotion Analysis")
    plt.tight_layout()
    plt.show()




window = tk.Tk()
window.title(string="Amazon Review analyser")
window.attributes('-fullscreen', True)
window.config(bg="#0096FF")
pathstatement = tk.Label(
    text="Enter the URL of the Amazon product page, below:", fg="black", bg="white")
pathstatement.pack()
entry = tk.Entry(window, fg="black", bg="white", width=50)
entry.pack()
button = tk.Button(window, text="Confirm", width=30, command=press)
button.place(relx=.5, rely=0.2, anchor="center")
window.mainloop()
