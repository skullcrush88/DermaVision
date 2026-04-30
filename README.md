# DermaVision

![GitHub Created At](https://img.shields.io/github/created-at/RanitManik/DermaVision)
![GitHub repo size](https://img.shields.io/github/repo-size/RanitManik/DermaVision)
![GitHub Discussions](https://img.shields.io/github/discussions/RanitManik/DermaVision)
![GitHub License](https://img.shields.io/github/license/RanitManik/DermaVision)
![wakatime](https://wakatime.com/badge/github/RanitManik/DermaVision.svg)

DermaVision is a Flask-based application developed to detect various skin diseases using deep learning models. This project was created as part of a college initiative and features three distinct models, each trained on different datasets using PyTorch to identify 5, 10, and 23 skin diseases, respectively.

## Table of Contents

- [Pre-trained Models](#pre-trained-models)
- [Setup Instructions](#setup-instructions)
    - [Install Dependencies](#install-dependencies)
    - [Running the Application](#running-the-application)
- [Using the Pre-trained Models](#using-the-pre-trained-models)
- [Training the Models](#training-the-models)
- [Project Structure](#project-structure)
- [License](#license)

## Pre-trained Models

The repository includes pre-trained models for skin disease detection:

1. **Model 1**: Detects 5 diseases. Trained on a ~69MB dataset with 98% validation accuracy.
2. **Model 2**: Detects 10 diseases. Trained on a ~2GB dataset with 85% validation accuracy.
3. **Model 3**: Detects 23 diseases. Trained on a ~6GB dataset with 45% validation accuracy.

## Setup Instructions

### Install Dependencies

Each model has its own `requirements.txt` file. To install the dependencies for a specific model, navigate to the respective model directory and run:

```bash
pip install -r requirements.txt
```

### Running the Application

To start the Flask application for a specific model, navigate to its directory and execute:

```bash
python app.py
```

The Flask server will start, and you can access the application at `http://127.0.0.1:5000`. Use the web interface to upload an image and receive disease predictions.

## Using the Pre-trained Models

The pre-trained models are included in the repository, allowing you to use them directly without additional training.

## Training the Models

To train the models from scratch, navigate to the `src` directory of the respective model and run `main.py`. Ensure that you have the dataset in the appropriate directory and adjust the `num_classes` parameter according to your dataset's number of classes.

```bash
python src/main.py
```

> [!NOTE]
>  This project is configured to utilize NVIDIA GPUs for faster training and inference. Make sure you have the necessary NVIDIA drivers, CUDA toolkit, and the GPU version of PyTorch installed. <br/>
> For GPU setup instructions, refer to the [CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide). For PyTorch installation guidance, visit the [PyTorch Installation Page](https://pytorch.org/get-started/locally/).

## Project Structure

Here’s an overview of the project structure:

```
DermaVision/
├── LICENSE
├── README.md
├── model-X/
│   ├── app.py
│   ├── models/
│   │   └── skin_disease_model.pth
│   ├── requirements.txt
│   ├── src/
│   │   └── main.py
│   ├── templates/
│   │   ├── result.html
│   │   └── upload.html
│   └── uploads/
│       └── [user_uploaded_files]
└── [other_files_and_directories]
```

For more details, refer to the [Project Structure Documentation](docs/project%20structure.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


