import os
import sys

from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging
from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object,load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data,evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

import mlflow
from urllib.parse import urlparse

import dagshub
dagshub.init(repo_owner='akshatbindal', repo_name='Network-Security-DS-Project', mlflow=True)

# os.environ["MLFLOW_TRACKING_URI"]="https://dagshub.com/akshatbindal/Network-Security-DS-Project.mlflow"
# os.environ["MLFLOW_TRACKING_USERNAME"]="akshatbindal"
# os.environ["MLFLOW_TRACKING_PASSWORD"]="8411fdb23af025fa9f377219a70c2bd3d977d6be"

class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def track_mlflow(self,best_model,classificationmetric):
        # mlflow.set_registry_uri("https://dagshub.com/akshatbindal/Network-Security-DS-Project.mlflow")
        # tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
        with mlflow.start_run():
            f1_score=classificationmetric.f1_score
            precision_score=classificationmetric.precision_score
            recall_score=classificationmetric.recall_score

            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision",precision_score)
            mlflow.log_metric("recall_score",recall_score)
            mlflow.sklearn.log_model(best_model,"model")
            # # Model registry does not work with file store
            # if tracking_url_type_store != "file":
            #     mlflow.sklearn.log_model(best_model, "model", registered_model_name=best_model)
            # else:
            #     mlflow.sklearn.log_model(best_model, "model")

    def train_model(self,X_train,y_train,x_test,y_test):
        models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }
        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy'],
                'splitter': ['best', 'random'],
                'max_features': ['sqrt']
            },
            "Random Forest": {
                'criterion': ['gini', 'entropy'],
                'max_features': ['sqrt', 'log2'],
                'n_estimators': [16, 64, 128]
            },
            "Gradient Boosting": {
                'loss': ['log_loss', 'exponential'],
                'learning_rate': [0.05, 0.1],
                'subsample': [0.7, 0.8, 0.9],
                'criterion': ['squared_error', 'friedman_mse'],
                'max_features': ['sqrt', 'log2'],
                'n_estimators': [16, 64, 128]
            },
            "Logistic Regression": {
                'penalty': ['l1', 'l2'],
                'C': [0.1, 1, 10],
                'max_iter': [1000, 2000, 5000]
            },
            "AdaBoost": {
                'learning_rate': [0.01, 0.1],
                'n_estimators': [16, 64, 128]
            }
        }

        model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=x_test,y_test=y_test,
                                          models=models,param=params)

        best_model_score = max(sorted(model_report.values()))
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]

        y_train_pred=best_model.predict(X_train)
        classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)
        
        self.track_mlflow(best_model,classification_train_metric)

        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)

        self.track_mlflow(best_model,classification_test_metric)

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path,obj=NetworkModel)
        
        save_object("final_model/model.pkl",best_model)
        
        model_trainer_artifact=ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,
                             test_metric_artifact=classification_test_metric
                             )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact

    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)
            return model_trainer_artifact
   
        except Exception as e:
            raise NetworkSecurityException(e,sys)