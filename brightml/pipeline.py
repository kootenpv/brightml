import numpy as np
import pandas as pd
from sklearn.pipeline import TransformerMixin
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor

from brightml.utils import get_training_data


class DataFrameImputer(TransformerMixin):
    """
    Credits http://stackoverflow.com/a/25562948/1575066
    """

    def __init__(self):
        """Impute missing values.

        Columns of dtype object are imputed with the most frequent value
        in column.

        Columns of other types are imputed with mean of column.

        """
        self.fill = None

    @staticmethod
    def most_frequent(col):
        try:
            return col.value_counts().index[0]
        except IndexError:
            return 0

    @staticmethod
    def get_impute_val(col):
        if col.dtype == np.dtype('O'):
            val = ""
        elif col.dtype == np.dtype(float):
            val = col.mean()
        else:
            val = col.median()
        if isinstance(val, float) and np.isnan(val):
            val = 0
        return val

    def fit(self, X, y=None):
        self.fill = pd.Series([self.get_impute_val(X[c]) for c in X], index=X.columns)
        return self

    def transform(self, X, y=None):
        return X.fillna(self.fill, inplace=False)


class Labelizer(TransformerMixin):
    def __init__(self):
        self.labels = {}

    def get_label(self, x):
        if x not in self.labels:
            # adding +100 makes the columns easier to spot
            self.labels[x] = len(self.labels) + 100
        return self.labels[x]

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        for x in X:
            X[x] = [self.get_label(y) if X[x].dtype == np.object else y for y in X[x]]
        return X


class SelectLast(TransformerMixin):
    def __init__(self, groupby=("ambient_light", "display_window_name", "datetime_date")):
        self.groupby = groupby
        self.cols = None

    def fit(self, X, y=None):
        self.cols = X.columns
        return self

    def transform(self, X, y=None):
        X = X.groupby(self.groupby).last().reset_index()
        X = X.reindex_axis(self.cols, axis=1)
        X = X.fillna(0)
        return X


def get_pipeline(X):
    return make_pipeline(
        DataFrameImputer(),
        Labelizer(),
        SelectLast(),
        OneHotEncoder(handle_unknown="ignore",
                      categorical_features=X.dtypes == np.object, sparse=False)
    )


def prune(data):
    sl = SelectLast()
    return sl.fit_transform(data)


def get_classifier_pipeline(path=None, clf=KNeighborsRegressor(1)):
    data = get_training_data(path)
    if data is None:
        return None, None
    data.drop("datetime_timezone", axis=1, inplace=True)
    pipeline = get_pipeline(data)
    data = pipeline.fit_transform(data)
    X, y = data[:, :-1], data[:, -1]
    print("train.shape", X.shape)
    clf.fit(X, y)
    return pipeline, clf
