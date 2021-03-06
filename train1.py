import numpy
import matplotlib.pyplot as plt
from keras.layers import Dropout
from keras.layers import Flatten
from keras.constraints import maxnorm
from keras.optimizers import SGD
from keras.layers import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.utils import np_utils
from keras import backend as K
import load_data
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
import keras
from keras.models import Model
from keras.optimizers import Adam
from keras.layers import Input,Dropout,Flatten
from keras.layers import GlobalAveragePooling2D
from keras.preprocessing.image import ImageDataGenerator
import random
from keras.applications.inception_v3 import InceptionV3
from keras import backend as K
from keras.applications.vgg16 import VGG16
from keras.applications.mobilenet import MobileNet





K.common.set_image_dim_ordering('tf')
# fix random seed for reproducibility
seed = 7
numpy.random.seed(seed)

def pre_process(X):

    # normalize inputs from 0-255 to 0.0-1.0

    X = X.astype('float32')
    X = X / 255.0

    return X

def one_hot_encode(y):

    # one hot encode outputs
    y = np_utils.to_categorical(y)
    num_classes = y.shape[1]
    return y,num_classes

def mobileNet(num_classes,epochs):
    mobile = MobileNet(input_tensor= Input(shape=(224, 224, 3)),include_top= False , weights='imagenet')
    ##input_tensor= Input(shape=(64, 64, 3))
    ##input_tensor=input_tensor
    ##print(input_tensor)
    print(mobile.summary())

    x = mobile.layers[-6].output
    x = Flatten()(x)

    predictions = Dense(num_classes,activation='softmax')(x)
    mobile_model = Model(inputs=mobile.input, output=predictions)

    for layer in mobile_model.layers[:-8]:
        layer.trainable = False

    print(mobile_model.summary())


    #mobile_model.compile(Adam(lr=0.0001),loss='categorical_crossentropy', metrics=['accuracy'])
    mobile_model.compile(optimizer=Adam(lr=0.001),
                         loss='categorical_crossentropy',
                         metrics=['accuracy'])



    return mobile_model


# load data
X,y=load_data.load_datasets()

# pre process
X=pre_process(X)

#one hot encode
y,num_classes=one_hot_encode(y)

#split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=7)

aug = ImageDataGenerator(rotation_range=20,
                         zoom_range=0.15,
                         width_shift_range=0.2,
                         height_shift_range=0.2,
                         shear_range=0.15,
                         horizontal_flip=True,
                         fill_mode="nearest")

epochs = 10
#define model
mobile_model=mobileNet(num_classes,epochs)


# Fit the model
history=mobile_model.fit_generator(
    aug.flow(X_train,y_train,batch_size=32),
    validation_data=(X_test,y_test),
    steps_per_epoch=len(X_train)/32,
    epochs=epochs
)
#history=mobile_model.fit(X_train, y_train, validation_split=0.3, epochs=epochs, batch_size=32,shuffle=True)

# list all data in history
print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()


# Final evaluation of the model
scores = mobile_model.evaluate(X_test, y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))

# serialize model to JSONx
model_json = mobile_model.to_json()
with open("models/mobile_model_face.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
mobile_model.save_weights("models/mobile_model_face.h5")
print("Saved model to disk")

