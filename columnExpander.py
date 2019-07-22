import ast
import numpy as np
from sklearn.base import TransformerMixin
from scipy.sparse import lil_matrix
from abc import abstractmethod

class BaseExpander:
    def __init__(self, extraction_col, delim = "_"):
        self.extraction_col = extraction_col
        self._fit = False
        self.delim = delim

    @abstractmethod
    def _set_column_names(self):
        '''Should set self.full_columns and self.slim_columns as list of column names'''
        # self.full_columns = []
        # self.slim_columns = []
        pass
    
    @abstractmethod
    def _pull_attributes(self):
        pass

    @abstractmethod
    def fit(self, X, y = None):
        '''Must return self, and have .attributes_ established'''
        try:
            col_1 = X[self.extraction_col]
            if y:
                col_2 = y[self.extraction_col]
            else:
                col_2 = []
        except Exception as e:
            raise e
        self._fit = True
        self._pull_attributes(np.concatenate([col_1,col_2]))
        self._set_column_names()
        return self

    @abstractmethod
    def transform(self, X):
        '''Returns a sparse array with attributes'''
        if not self._fit:
            raise ValueError("Transformer must be .fit() first")

    def get_feature_names(self, drop_first = False):
        if drop_first:
            return self.slim_columns
        else:
            return self.full_columns
    
    def _create_col_names(self, key, vals):
        if type(vals) != list:
            vals = [vals]
        return ["{}{}{}".format(key, self.delim, val) for val in vals] 

    def fit_transform(self, X, y = None, drop_first = False, verbose = False):
        self.fit(X, y)
        return self.transform(X, drop_first, verbose)
        

class DictColumnExpander(BaseExpander,TransformerMixin):
    def __init__(self, extraction_col, delim = "_"):
        super().__init__(extraction_col, delim)
    
    def fit(self, X, y = None):
        super().fit(X, y)
        return self

    def transform(self, X, drop_first = False, verbose = False):
        '''Returns a sparse array with attributes one-hot encoded'''
        super().transform(X)
         # Get attribute column
        try:
            dict_list = X[self.extraction_col]
        except Exception as e:
            raise e

        if drop_first:
            l = len(self.slim_columns)
            col_names = self.slim_columns
        else:
            l = len(self.full_columns)
            col_names = self.full_columns

        out = lil_matrix((X.shape[0],l))
            
        if verbose:
            print("Starting transformation:")
            total = len(dict_list)
        # loop through each row
        for i, dic in enumerate(dict_list):
            if verbose and i % round(total * .1) == 0: # every 10%
                print("{:.2%} Completed".format(i/total))
            if not dic:
                continue
            for key, val in dic.items():
                val = self._extract_values(key, ast.literal_eval(val))
                potential_col_names = self._create_col_names(key, val)
                
                indeces = [col_names.index(pcn) for pcn in potential_col_names if pcn in col_names]
                out[i, indeces] = 1
        if verbose:
            print("Transformation Complete")
        return out

    def _set_column_names(self):
        self.full_columns = []
        self.slim_columns = []
        
        for key, val in self.attributes_.items():
            for i, inner_val in enumerate(val):
                col_name = self._create_col_names(key, inner_val)[0]
                if i != 0:
                    self.slim_columns.append(col_name)
                self.full_columns.append(col_name)
    
    def _extract_values(self, key, val):
        '''extracts values and returns the value or if a dict a list of concatonated names'''
        if type(val) == dict:
            return list(val.keys())
        return val

    def _pull_attributes(self, dict_list):
        '''Deep dictionary extraction'''
        out = {}
        for dic in dict_list:
            if not dic:
                if not out.get(key):
                    out[key] = set()
                out[key].add(dic)
                continue
            for key, val in dic.items():
                if not out.get(key):
                    out[key] = set()
                val = self._extract_values(key, ast.literal_eval(val))
                if type(val) == list:
                    out[key].update(val)
                else:
                    out[key].add(val)
        self.attributes_ = out

class ListColumnExpander(BaseExpander,TransformerMixin):
    def __init__(self, extraction_col, delim = "_"):
        super().__init__(extraction_col, delim)        

    def _pull_attributes(self, cat_list):
        '''Shallow list extraction'''
        out = set()
        for cat in cat_list:
            out.update([name.strip() for name in cat.split(",")])
        self.attributes_ = out
    
    def fit(self, X, y = None):
        super().fit(X, y)
        return self
    
    def _set_column_names(self):
        self.full_columns = [self._create_col_names(self.extraction_col, name)[0] for name in self.attributes_]
        self.slim_columns = self.full_columns[1:]
    
    def transform(self, X, drop_first = False, verbose = False):
        super().transform(X)
        '''Returns a sparse array with attributes one-hot encoded'''
        # Get attribute column
        try:
            cat_list = X[self.extraction_col]
        except Exception as e:
            raise e
        l = len(self.full_columns)
        col_names = self.attributes_
        if drop_first:
            l -= 1
            col_names = list(col_names)[1:] 

        out = lil_matrix((X.shape[0],l))
    
        if verbose:
            print("Starting transformation:")
            total = len(col_names)
        for i, cat in enumerate(col_names):
            if verbose and i % round(total * .1) == 0: # every 10%
                print("{:.2%} Completed".format(i/total))
            indeces = cat_list[cat_list.map(lambda cat_list: cat in cat_list)].index
            out[indeces, i] = 1
        if verbose:
            print("Transformation Complete")
        return out