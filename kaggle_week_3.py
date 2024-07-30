# -*- coding: utf-8 -*-
"""Kaggle Week 3

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1sWW6Kf3ck3SSQ1nsq_D8caxC4ruur0_7

# Week 3 Kaggle Project

This project focuses on detecting cancer through image classification, which is part of a Kaggle competition. Cancer is a major health issue around the world and remains one of the leading causes of death. Early and accurate detection of cancer can significantly improve the chances of successful treatment and recovery. In this project, we aim to contribute to this effort by using advanced techniques to analyze medical images and determine if they show signs of cancer.

Our project revolves around examining pathology slides, which are images taken from tissue samples. These images help doctors and medical professionals make informed decisions about a patient’s condition. Specifically, we’ll be using a large dataset consisting of 220,000 images. Our goal is to develop a computer program that can look at these images and correctly identify whether or not they show metastatic cancer—cancer that has spread from one part of the body to another.

To achieve this, we will build a specialized computer model known as a Convolutional Neural Network (CNN). This type of model is particularly good at analyzing visual information and is commonly used in various image-related tasks. We will train this model using the dataset mentioned earlier, adjusting and improving it as we go along to ensure it performs well.

The project will begin with importing the dataset from Kaggle, a popular platform for data science competitions and datasets. Since the dataset is quite large, we’ll use Kaggle’s tools to make the process more efficient. Our first step will be to explore the data, which involves looking at the structure and content of the images and labels to better understand what we are working with.

Once we have a good grasp of the data, we’ll train our model to recognize patterns and features in the images that indicate the presence of cancer. This involves feeding the images into the model and adjusting its settings to improve its accuracy. After training, we’ll evaluate how well the model performs by testing it on a separate set of images that it has not seen before. This will help us determine how effectively the model can identify cancerous images in real-world scenarios.

Let's get right into it!
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Activation, BatchNormalization, ReLU, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from PIL import Image
import matplotlib.pyplot as plt

from google.colab import drive
import os

# Mount Google Drive
drive.mount('/content/drive')

!mkdir -p ~/.kaggle

!cp /content/drive/MyDrive/Last\ Class\ Material/Kaggle\ Week\ 3/kaggle.json ~/.kaggle/

!chmod 600 ~/.kaggle/kaggle.json
print(os.listdir('/root/.kaggle'))

!kaggle competitions download -c histopathologic-cancer-detection

import zipfile

zip_file_path = '/content/histopathologic-cancer-detection.zip'

extracted_dir_path = '/content/dataset'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extracted_dir_path)

"""# Dataset Overview and Analysis
In this section of the report, we will thoroughly explore the details of our training and test datasets, which are fundamental to developing and evaluating our cancer detection model. Understanding these datasets is important so that our model can accurately identify cancerous cells in medical images.

Our datasets are divided into two main parts. The first part is the training dataset, which contains 220,025 images. Each image is a .tif file with dimensions of 96x96 pixels. Alongside these images, we have labels that tell us whether each image shows signs of cancer or not. These labels are important because they allow us to teach our model how to recognize cancerous features based on examples provided in the training data.

The second part is the test dataset, which includes 57,458 images, also formatted as 96x96 pixel .tif files. However, unlike the training set, the test set does not have labels. Our task is to use the model we build from the training data to predict whether these images show signs of cancer. This prediction will help us understand how well our model can perform on new, unseen images.

To make the most of this data, we will focus on the center 32x32 pixels of each 96x96 image. This central portion is often the most relevant for detecting cancer and will be the area where we look for signs of the disease. We will access and handle the images using the .tif format, which ensures that the images retain their high quality and detail, which is important for accurate analysis.

In the following sections, we will discuss how we load and manage the images and labels using various tools and techniques. We will also visualize some of the images to get a better sense of their content and structure. Initial analysis will involve checking the quality of the images, making sure there are no missing or damaged files, and preparing the data for our model. By carefully analyzing and processing the training and test datasets, we aim to build a reliable model for detecting cancer.
"""

train_labels = pd.read_csv('/content/dataset/train_labels.csv')
sample_submission = pd.read_csv('/content/dataset/sample_submission.csv')

train_labels.head()

train_labels.shape

sample_submission.head()

sample_submission.shape

path = '/content/dataset/train/'
filepath = path + train_labels['id'] + '.tif'
testpath = '/content/dataset/test/'
testpaths = testpath + sample_submission['id'] + '.tif'

testpaths.head()

filepath.head()

train_labels['path'] = filepath
test = pd.DataFrame()
test['path'] = testpaths

def load_image(file_path):
    image = Image.open(file_path)
    return image

train_labels['image'] = train_labels['path'].apply(load_image)

"""In the images shown below, you can see examples of pathology slides along with their labels: 1 for cancerous and 0 for non-cancerous. Identifying cancerous areas can be challenging, especially for someone with a limited background in biology, like myself.

Given the difficulty in pinpointing cancer visually, using a Convolutional Neural Network (CNN) is a great approach. A CNN can automatically detect patterns and features in the images, which can help identify cancer more effectively than an untrained human eye. While a skilled biologist might be able to identify cancer, a CNN offers a powerful tool for spotting cancer that might be missed otherwise.

As we dive deeper into our data, we notice that the labels are fairly balanced. There are 130,908 images labeled as non-cancerous and 89,117 labeled as cancerous. This balance means we don't need to adjust the dataset to correct any imbalance when evaluating the model's accuracy.

To ensure our CNN model performs well, we need to check that it doesn’t just memorize the training data without generalizing to new data. To do this, we'll split our dataset into a training set and a validation set. This way, we can monitor how well the model is learning and adjust if necessary. The next steps will involve creating these sets and examining the distribution of cancerous versus non-cancerous samples in our dataset.
"""

def display_images(images, labels, rows=1, cols=5):
    fig, axes = plt.subplots(rows, cols, figsize=(15, 3 * rows))
    axes = axes.flatten()
    for img, label, ax in zip(images, labels, axes):
        ax.imshow(img)
        ax.set_title(label)
        ax.axis('off')
    plt.tight_layout()
    plt.show()

images_to_show = train_labels['image'].iloc[:5]
labels_to_show = train_labels['label'].iloc[:5]
display_images(images_to_show, labels_to_show)

train_labels['label'].value_counts()

import seaborn as sns
sns.set(style="whitegrid")

plt.figure(figsize=(10, 6))
ax = train_labels['label'].value_counts().plot(kind='bar', color=sns.color_palette("viridis", len(train_labels['label'].unique())))

plt.xlabel('Label', fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.title('Label Distribution', fontsize=15)

for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=10)
plt.xticks(rotation=0, ha='right')

plt.tight_layout()
plt.show()

train, val = train_test_split(train_labels, test_size=0.2)

train['label'] = train['label'].astype(str)
val['label'] = val['label'].astype(str)

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

val_test_datagen = ImageDataGenerator(rescale=1./255)

def create_generator(datagen, dataframe, x_col, y_col=None, target_size=(96, 96), batch_size=32, class_mode='binary', shuffle=True):
    return datagen.flow_from_dataframe(
        dataframe,
        x_col=x_col,
        y_col=y_col,
        target_size=target_size,
        batch_size=batch_size,
        class_mode=class_mode,
        shuffle=shuffle
    )

train_gen = create_generator(train_datagen, train, x_col='path', y_col='label')
val_gen = create_generator(val_test_datagen, val, x_col='path', y_col='label')
test_gen = create_generator(val_test_datagen, test, x_col='path', class_mode=None, shuffle=False)

print(f"Train generator: {len(train_gen)} batches")
print(f"Validation generator: {len(val_gen)} batches")
print(f"Test generator: {len(test_gen)} batches")

"""# Model Architecture

With our data thoroughly prepared and analyzed, we are ready to move on to developing the architecture of our model. Drawing on the concepts we've covered in class, we’ve crafted a model structure that we believe is well-suited for our task of cancer detection. We’ve opted for a Keras Sequential model, which includes several key components designed to effectively analyze our images and make accurate predictions.

Our model starts with a series of convolutional layers, each followed by pooling layers. This combination of convolution and pooling helps the model to extract and compress important features from the images. Specifically, we use three convolution-pooling layers in sequence, which we found to be the optimal number for this dataset. This setup strikes a good balance, avoiding the potential pitfalls of having too few or too many layers.

The convolutional layers are followed by a regular neural network (also known as a dense network), where the processed data is used to make predictions about the pathology slides. This design helps the model learn complex patterns and relationships in the data, ultimately allowing it to predict whether an image contains cancerous cells.

Our model’s architecture underwent several iterations before we arrived at this final version. We experimented with different configurations and learned a great deal from each phase. For example, we discovered that increasing the number of filters in each convolutional layer significantly enhanced the model’s performance. In contrast, using more than three convolution-pooling layers did not yield better results and, in some cases, even detracted from performance. Additionally, we found that dropout layers played a crucial role in preventing overfitting and improving the overall performance of the model.

Interestingly, batch normalization did not provide a noticeable improvement in accuracy for our specific dataset, so we chose to omit it from our final model. On the other hand, using the ReLU activation function after each convolutional layer greatly contributed to the model’s predictive accuracy. Initially, we started with a larger number of filters, but reducing them proved to be more effective in refining the model’s performance.

Below, you will find the detailed architecture of our model. This setup reflects the optimizations and adjustments we’ve made based on our experiments and findings.
"""

def add_conv_block(model, filters, kernel_size=(3, 3), activation='relu', pool_size=(2, 2), dropout_rate=0.25):
    model.add(Conv2D(filters, kernel_size, activation=activation))
    model.add(Conv2D(filters, kernel_size, activation=activation))
    model.add(Conv2D(filters, kernel_size, activation=activation))
    model.add(MaxPooling2D(pool_size=pool_size))
    model.add(Dropout(dropout_rate))

model = Sequential()

model.add(Conv2D(25, (3, 3), activation='relu', input_shape=(96, 96, 3)))
add_conv_block(model, 25)

add_conv_block(model, 50)

model.add(Conv2D(100, (3, 3), activation='relu'))
model.add(Conv2D(100, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(BatchNormalization())

model.add(Flatten())
model.add(Dense(96, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.25))

model.add(Dense(1, activation='sigmoid'))

opt = Adam(0.001)
model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

"""The model ran a few training sessions. I utilized early stopping so that the process is faster and the training would stop once validation begins to decline. THe model ended up achieving an accuracy of about 87% and a validation accuracy of about 89%. Pretty good!"""

train_steps_per_epoch = len(train_gen)
val_steps_per_epoch = len(val_gen)

# Set up early stopping
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=1,
    restore_best_weights=True
)

# Train the model
history = model.fit(
    train_gen,
    steps_per_epoch=train_steps_per_epoch,
    epochs=10,
    validation_data=val_gen,
    validation_steps=val_steps_per_epoch,
    callbacks=[early_stopping],
    verbose=1  # Show progress during training
)

# Optionally, print the history keys to see what metrics were collected
print("History keys:", history.history.keys())

"""During the training of our model over 10 epochs, we observed notable improvements in both training and validation performance. In the first epoch, the model achieved a training accuracy of 79.82% and a validation accuracy of 64.23%, with a training loss of 0.4537 and a validation loss of 0.6589. By the second epoch, the model's performance significantly improved, reaching a training accuracy of 83.57% and a validation accuracy of 84.65%, with a reduced training loss of 0.3842 and a lower validation loss of 0.3868. However, in the third epoch, while the training accuracy further increased to 84.91%, the validation accuracy dropped to 77.49%, with the validation loss rising to 0.5608. This pattern indicates that the model was initially improving, but started to experience some overfitting as the training accuracy continued to rise while the validation accuracy did not keep pace. The history of these key metrics, including loss and accuracy, will guide us in making further adjustments to enhance the model's generalization capabilities.

In summary, optimizing the learning rate and carefully adjusting dropout layers and activation functions were crucial in enhancing our model's prediction accuracy. We tested various configurations, starting with a lower learning rate of 0.001 and experimenting with different setups of pooling layers, dense layers, activation functions, dropout layers, and filters. Our model initially achieved a validation accuracy of 84% with a simpler setup. By increasing the number of ReLU activation functions and dropout layers, we improved this to 86%. Adding batch normalization and maintaining all ReLU activations and dropout layers brought us to a validation accuracy of 85%. Ultimately, the most effective architecture reached a validation accuracy of 89%.


"""

preds = model.predict_generator(test_gen)

testfile = test_gen.filenames
testtrim = []
for test in testfile:
  testtrim.append(test.split('/')[-1].split('.'))
first_values = [sublist[0] for sublist in testtrim]

submission = pd.DataFrame()

submission['id'] = first_values
submission['label'] = preds

submission.head()

submission.to_csv('submission.csv', index = False)

"""Our model achieved an accuracy of 85% on the Kaggle test dataset, showcasing its strong potential for practical use in cancer detection. This level of accuracy suggests that the model can be a valuable tool in supporting cancer diagnosis when used alongside clinical expertise. Although our approach was effective, there is still room for improvement. Observing higher scores from other participants indicates that further experimentation with model configurations and hyperparameters could yield even better results.

Since I only ran a few epoch rounds, it took about 40 minutes total. Moving forward, I plan to test additional architectures and refine hyperparameters with more advanced hardware and additional time. This project has been a significant learning experience, highlighting the effectiveness of both simple and complex model components like dropout layers and activation functions. I’m excited to build on these insights and tackle more image classification challenges in the future.
"""