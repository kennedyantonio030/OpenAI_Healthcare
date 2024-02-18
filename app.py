import warnings
warnings.simplefilter('ignore')

import os
import cv2
import sys
import pickle
import subprocess
import numpy as np
from PIL import Image
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from src.utils import gen_from_image, gen_from_text
from flask import Flask, render_template,request,redirect,url_for
from src.Multi_Disease_System.Parkinsons_Disease_Prediction.pipelines.Prediction_pipeline import Parkinsons_Data, PredictParkinsons
from src.Multi_Disease_System.Breast_Cancer_Prediction.pipelines.Prediction_pipeline import BCancer_Data, PredictBCancer
from src.Multi_Disease_System.Heart_Disease_Prediction.pipelines.Prediction_pipeline import CustomData, PredictPipeline
brain_model = load_model('Artifacts\Brain_Tumour\BrainModel.h5')
kidney_model = load_model('Artifacts\Kidney_Disease\Kidney_Model.h5')

app = Flask(__name__)

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except:
        return render_template('error.html')
    

@app.route('/redirect')
def redirect_to_landing():
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    return render_template('index')

@app.route('/chatbot')
def run_streamlit():
    try:
        subprocess.Popen(['streamlit', 'run', 'src/GeminiMed/app.py'])
        return redirect(url_for('index'))
    except:
        return render_template('error.html')


@app.route('/recognition')
def run_streamlit1():
    try:
        subprocess.Popen(['streamlit', 'run', 'src/MedicineRecognition/app.py'])
        return redirect(url_for('index'))
    except:
        return render_template('error.html')



@app.route('/brain', methods=['GET', 'POST'])
def brain():
    if request.method == 'POST':
        try:
            def preprocess_image(image):
                img = Image.open(image)
                img = img.resize((299, 299))
                img = np.asarray(img)
                img = np.expand_dims(img, axis=0)
                img = img / 255
                return img
            
            class_labels = {0: 'Glioma Tumour', 1: 'Meningioma Tumour', 2: 'No Tumour', 3: 'Pituitary Tumour'}
            file = request.files['file']
            file_path = 'temp.jpg'
            file.save(file_path)
            processed_image = preprocess_image(file_path)
            predictions = brain_model.predict(processed_image)
            prediction_label = class_labels[np.argmax(predictions)]
            confidence = np.max(predictions)
            os.remove(file_path)
            return render_template('brain_tumour.html', prediction=prediction_label, confidence=confidence)
        except:
            return render_template('error.html')
    return render_template('brain_tumour.html')


@app.route('/bcancer', methods=["GET", "POST"])
def brain_post():
    if request.method == 'POST':
        try:
            data = BCancer_Data(
                texture_mean = float(request.form['texture_mean']),
                smoothness_mean = float(request.form['smoothness_mean']),
                compactness_mean = float(request.form['compactness_mean']),
                concave_points_mean = float(request.form['concave_points_mean']),
                symmetry_mean = float(request.form['symmetry_mean']),
                fractal_dimension_mean = float(request.form['fractal_dimension_mean']),
                texture_se = float(request.form['texture_se']),
                area_se = float(request.form['area_se']),
                smoothness_se = float(request.form['smoothness_se']),
                compactness_se = float(request.form['compactness_se']),
                concavity_se = float(request.form['concavity_se']),
                concave_points_se = float(request.form['concave_points_se']),
                symmetry_se = float(request.form['symmetry_se']),
                fractal_dimension_se = float(request.form['fractal_dimension_se']),
                texture_worst = float(request.form['texture_worst']),
                area_worst = float(request.form['area_worst']),
                smoothness_worst = float(request.form['smoothness_worst']),
                compactness_worst = float(request.form['compactness_worst']),
                concavity_worst = float(request.form['concavity_worst']),
                concave_points_worst = float(request.form['concave_points_worst']),
                symmetry_worst = float(request.form['symmetry_worst']),
                fractal_dimension_worst = float(request.form['fractal_dimension_worst'])
                )
            final_data = data.get_data_as_dataframe()
            predict_pipeline = PredictBCancer()
            pred = predict_pipeline.predict(final_data)
            result = round(pred[0], 2)
            return render_template('bcancer.html', final_result=result)
        except:
            return render_template('error.html')
    return render_template('bcancer.html')

@app.route('/diabetes')
def bcancer_post():
        try:
            return render_template('diabetes.html')
        except:
            return render_template('error.html')

@app.route('/heart', methods=["GET", "POST"])
def heart():
    if request.method == "POST":
        try:
            data = CustomData(
                age=request.form.get("age"),
                sex=request.form.get("sex"),
                cp=(request.form.get("cp")),
                trestbps=(request.form.get("trestbps")),
                chol=(request.form.get("chol")),
                fbs=request.form.get("fbs"),
                restecg=request.form.get("restecg"),
                thalach=(request.form.get("thalach")),
                exang=request.form.get("exang"),
                oldpeak=request.form.get("oldpeak"),
                slope=request.form.get("slope"),
                ca=request.form.get("ca"),
                thal=(request.form.get("thal")))
            final_data = data.get_data_as_dataframe()
            predict_pipeline = PredictPipeline()
            pred = predict_pipeline.predict(final_data)
            result = round(pred[0], 2)
            return render_template("heart.html", final_result=result)
        except:
            return render_template("error.html")
    return render_template("heart.html")

@app.route('/kidney', methods=['GET', 'POST'])
def kidney():
    if request.method == 'POST':
        try:
            class_labels = {0: 'Cyst', 1: 'Normal', 2: 'Stone', 3: 'Tumor'}
            file = request.files['file']
            if file.filename == '':
                return render_template('error.html', message='No file selected')

            file_path = 'temp.jpg'
            file.save(file_path)

            img = cv2.imread(file_path)
            img = cv2.resize(img, (150, 150))
            img = img / 255.0
            img = np.expand_dims(img, axis=0)

            # Make predictions using the loaded model
            predictions = kidney_model.predict(img)
            prediction_label = class_labels[np.argmax(predictions)]
            os.remove(file_path)
            return render_template('kidney.html', prediction=prediction_label)
        except Exception as e:
            return render_template('error.html', message=str(e))
    return render_template('kidney.html')

@app.route('/liver')
def liver():
    try:
        return render_template('liver.html')
    except:
        return render_template('error.html')


@app.route('/lung')
def lung():
    try:
        return render_template('lung.html')
    except:
        return render_template('error.html')

@app.route('/malaria')
def malaria():
    try:
        return render_template('malaria.html')
    except:
        return render_template('error.html')
    

@app.route('/parkinsons', methods=["GET", "POST"])
def parkinsons():
    if request.method == 'POST':
        try:
            data = Parkinsons_Data(
                    MDVPFO=float(request.form.get("MDVPFO")),
                    MDVPFHI=float(request.form.get("MDVPFHI")),
                    MDVPFLO=float(request.form.get("MDVPFLO")),
                    MDVPJ=float(request.form.get("MDVPJ")),
                    RPDE=float(request.form.get("RPDE")),
                    DFA=float(request.form.get("DFA")),
                    spread2=float(request.form.get("spread2")),
                    D2=float(request.form.get("D2")))
            final_data = data.get_data_as_dataframe()
            predict_pipeline = PredictParkinsons()
            pred = predict_pipeline.predict(final_data)
            result = round(pred[0], 2)
            return render_template("parkinsons.html", final_result=result)
        except:
            return render_template("error.html")
    return render_template('parkinsons.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)