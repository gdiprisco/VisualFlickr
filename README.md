# VisualFlickr

VisualFlickr is a CNN-based tool which can infer emotion and sentiment from Flickr pictures.  
It is based on Caffe framework.  
VF allows keyword based search and the analysis of entire profiles from Flickr.  
The GUI shows photos, data and pie charts in order to clarify provided information.  
All info in VisualFlickr complete white paper.pdf   

## Requirements

- [Caffe](https://caffe.berkeleyvision.org/) deep learning framework installed on your machine  
  If you use *__aptitude__* package manager, you can run:
  ```
  apt install caffe-cpu
  ```
  or
  ```
  apt install caffe-cuda
  ```    

- Python 3.x
- You can install all the necessary packages running:
  ```
  pip install -r requirements.txt
  ``` 
 - ImageTK  
   If you use *__aptitude__* package manager, you can run
     ```
     apt install python3-pil.imagetk
     ```
## Tested
VisualFlickr has been tested on __Ubuntu 18.04__ in Tilix terminal emulator and in PyCharm IDE.

## Run
Convolutional neural network used for this project are available in [this Drive folder](https://drive.google.com/drive/folders/1wAimZB7Zq3ozZk2pK0EC5u_xvpd7wzTq?usp=sharing).
You have to download the six directories labelled with the langauge names and put into the _net_ directory.
Run __demo.py__ in your Python interpreter.

### Tree view of the entire project
```
VisualFlickr
│   demo.py
│   README.md
│   requirements.txt
│   tags.txt
│   tree.txt
│   users.json
│   
├───image_test
├───modules
├───mvso_scores
│   ├───ANP_emotion_scores
│   └───mvso_sentiment
│           
├───net
│   ├───chinese
│   ├───english
│   ├───french
│   ├───german
│   ├───italian
│   └───spanish
│           
└───settings
```        


