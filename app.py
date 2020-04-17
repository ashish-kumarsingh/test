from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import re
import scipy.misc

import numpy as np
from scipy import misc
from keras.models import model_from_json
import json
import os, shutil
import csv

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
#from keras.preprocessing import image
import pickle
from multiprocessing import Pool,Process
import time

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
# from gevent.pywsgi import WSGIServer

# Define a flask app

app = Flask(__name__)

classifier_f = open("int_to_word_out.pickle", "rb")
int_to_word_out = pickle.load(classifier_f)
classifier_f.close()
def load_model():
    # load json and create model
    json_file = open('models/mobilenet_model_face.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    #start = time.time()
    loaded_model.load_weights("models/mobilenet_model_face.h5")
    print("Loaded model from disk")

    #print('Load_model 2: Elapsed time', time.time() - start)


    return loaded_model
# Model saved with Keras model.save()
# Load your trained model     # Necessary
# print('Model loaded. Start serving...')


def delete():
    folder = 'uploads/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    return None




def pre_process(img):
    start = time.time()
    img = img.astype('float32')
    img = img / 255.0
    print('Pre_process: Elapsed time', time.time() - start)

    return img

def load_image(img_path,model):
    start = time.time()
    image = np.array(misc.imread(img_path))
    image = misc.imresize(image, (224,224))
    image = np.array([image])
    image = pre_process(image)
    prediction = model.predict(image)
    print('Load_image: Elapsed time', time.time() - start)


    return prediction

def calories_count(predicted):
    start = time.time()
    f = open('foods.csv','r')
    reader = csv.reader(f)
    foods = {}
    print("Predicted"+predicted)
    print('Calories: Elapsed time', time.time() - start)


    for row in reader:
        foods[row[0]]={'calories':row[1],'fats':row[2]}

    calories=(foods[predicted])
    return calories




@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads

        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, secure_filename(f.filename))
        f.save(file_path)
        # Make prediction
        print("File path"+file_path)
        model = load_model()

        print("Model Loaded")
        pred= load_image(file_path,model)
        preds= int_to_word_out[np.argmax(pred)]
        pred_acc = str(round((np.max(pred)),2))
        calc = calories_count(preds)
        print(calc)
        calories= calc['calories']
        fats =calc['fats']


        calc1 = preds + ' : ' + ' Acc: ' + pred_acc + ' ,  ' + calories + ' calories, '  + fats + ' fats '




    return calc1
    return None


if __name__ == '__main__':
    app.run(debug=True)

