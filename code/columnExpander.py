import numpy as np
from sklearn.base import TransformerMixin
from scipy.sparse import lil_matrix
from abc import abstractmethod

class BaseExpander:
    """Base class for column expanders
    Provides abstract framework for other expander classes designed to dummify
    compressed data columns into the appropriate dummy columns.

    Parameters
    ----------
    This abstract class is not meant to be initialized directly.

    Notes
    -----
    Inherited classes must define the following abstract methods:

    ._get_column_names(): 
        returns the fitted dummy column names
    ._pull_attributes():
        parses dummy column names from compressed data
    .fit(): optional
        fits the model to the given data 
    .transform():
        transforms the given data using fitted information
    ._create_col_names():
        responsible for column name formatting
    """

    def __init__(self, extraction_cols, delim = "_"):
        self.extraction_cols = extraction_cols if type(extraction_cols) == list else [extraction_cols]
        self._fit = False
        self.delim = delim

    @abstractmethod
    def _get_column_names(self, extraction_col, attributes):
        pass
    
    @abstractmethod
    def _pull_attributes(self):
        pass

    @abstractmethod
    def fit(self, X, y = None):
        '''Must return self, and have .attributes_ established'''
        self.attributes_  = {}
        self.full_columns = []
        self.slim_columns = []
        for extraction_col in self.extraction_cols:
            try:
                col_1 = X[extraction_col]
                if y:
                    col_2 = y[extraction_col]
                else:
                    col_2 = []
            except Exception as e:
                raise e
            attributes         = self._pull_attributes(np.concatenate([col_1,col_2]))
            full_col, slim_col = self._get_column_names(extraction_col, attributes)
            self.attributes_[extraction_col] = (attributes)
            self.full_columns.extend(full_col)
            self.slim_columns.extend(slim_col)
        self._fit = True
        return self

    @abstractmethod
    def transform(self, X):
        '''Returns a sparse array with attributes'''
        if not self._fit:
            raise ValueError("Transformer must be .fit() first")

    def get_feature_names(self, drop_first = False):
        return self.slim_columns if drop_first else self.full_columns
    
    def _create_col_names(self, key, vals):
        if type(vals) != list:
            vals = [vals]
        return ["{}{}{}".format(key, self.delim, val) for val in vals] 

    def fit_transform(self, X, y = None, drop_first = False, verbose = False):
        self.fit(X, y)
        return self.transform(X, drop_first, verbose)

class ListColumnExpander(BaseExpander,TransformerMixin):
    """Expands columns using list-style compressed data column 

    Parameters
    ----------
    extraction_cols : list
        String names for list-style compressed columns

    delim : str, default = "_"
        Delimiter for dummy column naming

    Examples
    --------
    >>> from columnExpander import ListColumnExpander
    >>>
    >>> train_data = ... # Pandas DataFrame
    >>> test_data  = ... # Pandas DataFrame    
    >>> lce = ListColumnExpander(["categories"])
    >>>
    >>> dummy_train_data = lce.fit_transform(train_data)
    >>> dummy_test_data = lce.transform(test_data)
    """
    def __init__(self, extraction_cols, delim = "_"):
        super().__init__(extraction_cols, delim)

    def _pull_attributes(self, cat_list):
        '''Shallow list extraction'''
        out = set()
        for cat in cat_list:
            out.update([name.strip() for name in cat.split(",")])
        return out
    
    def fit(self, X, y = None):
        super().fit(X, y)
        return self
    
    def _get_column_names(self, extraction_col, attributes):
        full_cols = [self._create_col_names(extraction_col, name)[0] for name in attributes]
        return (full_cols, full_cols[1:])
    
    def transform(self, X, drop_first = False, verbose = False):
        super().transform(X)
        '''Returns a sparse array with attributes one-hot encoded'''
        row_n = X.shape[0]
        col_n = len(self.slim_columns if drop_first else self.full_columns)
        out = lil_matrix((row_n,col_n))
        i = 0 
        for extraction_col in self.extraction_cols:
            # Get attribute column
            try:
                extracted_col = X[extraction_col]
            except Exception as e:
                raise e
            category_names = list(self.attributes_[extraction_col])

            if drop_first:
                category_names = category_names[1:] 

            if verbose:
                print("Starting transformation:")
            
            for category in category_names:
                row_indeces = [y for y, x in enumerate(extracted_col.map(lambda row: category in row)) if x]
                out[row_indeces, i] = 1 # problem with row indeces not matching nth row position
                i += 1

            if verbose:
                print("Transformation Complete")
        return out