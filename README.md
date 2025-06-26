# Network Security ML Project

## Project Overview

This project is a machine learning application designed to detect potential network security threats, such as phishing attempts. It utilizes a FastAPI backend to serve a trained model that can predict whether a given network activity or data point (e.g., from a CSV file) is malicious. The project includes a full MLOps pipeline for data ingestion, validation, transformation, model training, and prediction.

**Key Technologies:**

*   **Python:** Core programming language.
*   **FastAPI:** For building the RESTful API.
*   **Scikit-learn:** For machine learning tasks (model training, preprocessing).
*   **MongoDB:** As a database for data ingestion (though interaction details are abstracted via environment variables).
*   **Docker:** For containerizing the application (Dockerfile present).
*   **Uvicorn:** As an ASGI server to run the FastAPI application.

## Features

*   **ML Model Training:** A complete pipeline to train a network security model.
*   **Prediction API:** Exposes a `/predict` endpoint to get predictions from the trained model for new data.
*   **Training API:** Exposes a `/train` endpoint to re-trigger the model training pipeline.
*   **Data Validation:** Includes steps for validating incoming data against a defined schema.
*   **Modular Design:** The project is structured into logical components for different MLOps stages.

## Project Structure

The project is organized as follows:

```
.
├── .github/workflows/main.yml  # GitHub Actions workflow for CI/CD (if applicable)
├── .gitignore                  # Specifies intentionally untracked files that Git should ignore
├── Dockerfile                  # For building the Docker container
├── NetworkSecurity.egg-info/   # Build metadata for the networksecurity package
├── Network_Data/
│   └── phisingData.csv         # Sample data (likely for training/testing)
├── README.md                   # This file
├── app.py                      # FastAPI application exposing /train and /predict endpoints
├── data_schema/
│   └── schema.yaml             # Defines the schema for input data validation
├── final_model/
│   ├── model.pkl               # Serialized trained machine learning model
│   └── preprocessor.pkl        # Serialized preprocessing object
├── logs/                       # Directory for storing application logs
├── main.py                     # Script to run the training pipeline stages manually
├── networksecurity/            # Core Python package for the project
│   ├── __init__.py
│   ├── cloud/                  # Utilities for cloud interactions (e.g., S3 syncer)
│   ├── components/             # Core MLOps pipeline components
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   ├── data_validation.py
│   │   └── model_trainer.py
│   ├── constant/               # Project constants, including training pipeline configurations
│   ├── entity/                 # Defines data structures (configs, artifacts)
│   ├── exception/              # Custom exception handling
│   ├── logging/                # Logging setup
│   ├── pipeline/               # Defines the training and prediction pipelines
│   └── utils/                  # Utility functions (main utilities, ML utilities)
├── prediction_output/
│   └── output.csv              # Stores the output of the last prediction request
├── push_data.py                # Script likely used to push initial data to MongoDB
├── requirements.txt            # Python package dependencies
├── setup.py                    # Script for packaging the `networksecurity` module
├── templates/
│   └── table.html              # HTML template for displaying prediction results
└── valid_data/                 # Directory likely storing validated data splits (e.g., test.csv)
```

Key components:

*   **`app.py`**: Entry point for the FastAPI application. Handles API requests for training and prediction.
*   **`main.py`**: Allows manual execution of the different stages of the MLOps training pipeline.
*   **`networksecurity/`**: This directory forms the core Python package.
    *   **`components/`**: Contains modules for each step of the ML pipeline (Data Ingestion, Data Validation, Data Transformation, Model Trainer).
    *   **`pipeline/`**: Orchestrates the steps defined in `components/` to form a cohesive training pipeline.
    *   **`entity/`**: Defines Python dataclasses for configuration objects (e.g., `DataIngestionConfig`) and artifacts produced by pipeline steps.
    *   **`constant/`**: Stores global constants and configurations for the training pipeline.
    *   **`utils/`**: Provides helper functions used across the project.
*   **`data_schema/schema.yaml`**: Defines the expected structure, data types, and constraints for the input data.
*   **`final_model/`**: Stores the serialized trained model (`model.pkl`) and the preprocessor (`preprocessor.pkl`) for inference.
*   **`Dockerfile`**: Instructions to build a Docker image for the application.
*   **`requirements.txt`**: Lists all Python dependencies.

## Setup and Installation

Follow these steps to set up and run the project locally:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```
    (Replace `https://github.com/your-username/your-repository-name.git` and `your-repository-name` with the actual URL and project directory name.)

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    This project requires a MongoDB connection string. Create a `.env` file in the root directory of the project and add your MongoDB URI:
    ```env
    MONGODB_URL_KEY="your_mongodb_connection_string_here"
    ```
    The application uses `python-dotenv` to load this variable.

5.  **Prepare Initial Data (if necessary):**
    The project uses data from a MongoDB collection. The `push_data.py` script can be used to populate this data if it's not already present. You might need to inspect this script and adjust it for your MongoDB instance and data source (`Network_Data/phisingData.csv`).
    *   Ensure your MongoDB server is running and accessible.
    *   Run the script (you might need to configure it first):
        ```bash
        python push_data.py
        ```
    *(Note: This step assumes `push_data.py` is configured to connect to the MongoDB instance specified in your `.env` file and upload the data from `Network_Data/phisingData.csv` to the correct database and collection, as defined in `networksecurity/constant/training_pipeline/__init__.py`.)*

6.  **Run the Application:**
    The FastAPI application can be started using Uvicorn:
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    ```
    The application will be available at `http://localhost:8000`. The API documentation will be available at `http://localhost:8000/docs`.

7.  **Using Docker (Alternative):**
    If you have Docker installed, you can build and run the application using the provided `Dockerfile`:
    ```bash
    # Build the Docker image
    docker build -t network-security-app .

    # Run the Docker container
    # Make sure to pass the MONGODB_URL_KEY environment variable
    docker run -e MONGODB_URL_KEY="your_mongodb_connection_string_here" -p 8000:8000 network-security-app
    ```
    The application will be available at `http://localhost:8000`.

## API Endpoints

The application provides the following API endpoints. You can also explore these interactively via the Swagger UI at `http://localhost:8000/docs` or ReDoc at `http://localhost:8000/redoc` when the application is running.

### 1. Train Model

*   **Endpoint:** `/train`
*   **Method:** `GET`
*   **Description:** Triggers the machine learning model training pipeline. This process involves data ingestion, validation, transformation, and model training.
*   **Request Body:** None
*   **Response:**
    *   `200 OK`: "Training is successful" if the pipeline runs without errors.
    *   `500 Internal Server Error`: If an exception occurs during the training process.

    **Example using cURL:**
    ```bash
    curl -X GET http://localhost:8000/train
    ```

### 2. Predict

*   **Endpoint:** `/predict`
*   **Method:** `POST`
*   **Description:** Accepts a CSV file, performs predictions using the trained model, and returns the predictions along with the input data in an HTML table format. The predictions are also saved to `prediction_output/output.csv` on the server.
*   **Request Body:**
    *   `multipart/form-data`
    *   `file`: The CSV file containing the data to be predicted. The CSV should conform to the schema expected by the model (see `data_schema/schema.yaml`).
*   **Response:**
    *   `200 OK`: An HTML page displaying a table with the original data and an added `predicted_column`.
    *   `500 Internal Server Error`: If an exception occurs during the prediction process.

    **Example using cURL:**
    ```bash
    curl -X POST -F "file=@/path/to/your/input_data.csv" http://localhost:8000/predict
    ```
    (Replace `/path/to/your/input_data.csv` with the actual path to your CSV file.)

## Training Pipeline

The project includes a comprehensive MLOps training pipeline that can be executed manually or triggered via the `/train` API endpoint.

### Running the Pipeline Manually

You can run the entire pipeline or individual components using `main.py`. This is useful for development, debugging, or when you need finer control over the pipeline stages.

```bash
python main.py
```

This script will execute the following stages in sequence:

1.  **Data Ingestion:**
    *   Fetches data from the configured MongoDB source (defined by `DATA_INGESTION_DATABASE_NAME` and `DATA_INGESTION_COLLECTION_NAME` in constants).
    *   Splits the data into training and testing sets.
    *   Stores the raw data and the splits in the artifact directory (usually `artifacts/data_ingestion`).

2.  **Data Validation:**
    *   Validates the ingested data (e.g., `train.csv`, `test.csv`) against the schema defined in `data_schema/schema.yaml`.
    *   Checks for data drift and other potential issues.
    *   Produces validation reports and stores validated data in `valid_data/`.

3.  **Data Transformation:**
    *   Applies preprocessing steps to the validated data. This typically includes:
        *   Handling categorical and numerical features.
        *   Scaling/Normalization.
        *   Encoding.
    *   Saves the preprocessing object (e.g., a scikit-learn Pipeline or ColumnTransformer) to be used for transforming new data during inference.
    *   Stores the transformed data and the preprocessor in the artifact directory.

4.  **Model Training:**
    *   Trains a machine learning model using the transformed training data.
    *   The specific model and hyperparameters are configured within the `ModelTrainer` component.
    *   Evaluates the model on the transformed test data.
    *   Saves the trained model (`model.pkl`) and the preprocessor (`preprocessor.pkl`) to the `final_model/` directory for later use by the prediction service.
    *   May also log metrics and artifacts if experiment tracking (e.g., MLflow) is integrated.

### Triggering via API

As mentioned in the API Endpoints section, sending a `GET` request to the `/train` endpoint will execute this entire training pipeline.

```bash
curl -X GET http://localhost:8000/train
```

## How to Contribute

Contributions are welcome! If you'd like to contribute to this project, please follow these general guidelines:

1.  **Fork the Repository:** Start by forking the project to your own GitHub account.
2.  **Create a Branch:** Create a new branch for your feature or bug fix.
    ```bash
    git checkout -b feature/your-feature-name
    ```
    or
    ```bash
    git checkout -b fix/issue-number
    ```
3.  **Make Changes:** Implement your changes, ensuring you follow any existing coding styles and conventions.
4.  **Test Your Changes:** Ensure your changes don't break existing functionality. If applicable, add new tests for your features.
5.  **Commit Your Changes:** Write clear and concise commit messages.
    ```bash
    git commit -m "feat: Add new feature X"
    git commit -m "fix: Resolve issue Y"
    ```
6.  **Push to Your Fork:**
    ```bash
    git push origin feature/your-feature-name
    ```
7.  **Create a Pull Request:** Open a pull request from your forked repository to the main project repository. Provide a clear description of your changes and why they are needed.

## License

This project is currently not licensed. Please add a license if you intend to distribute or share this project. Common choices include MIT, Apache 2.0, or GPL.
