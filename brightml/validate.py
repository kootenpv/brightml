from xtoy import Toy
from brightml.utils import get_training_data

d = get_training_data()

X, y = d.iloc[:, :-1], d.iloc[:, -1]

toy = Toy()
toy.fit(X, y)

toy.best_features_(n=100, aggregation=None)
