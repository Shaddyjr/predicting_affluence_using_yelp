import ast
import numpy as np
from sklearn.base import TransformerMixin
from scipy.sparse import lil_matrix

class DictColumnExpander(TransformerMixin):
    def __init__(self, extraction_col, delim = "_"):
        self.extraction_col = extraction_col
        self.__fit = False
        self.delim = delim
    
    def __extract_values(self, key, val):
        '''extracts values and returns the value or if a dict a list of concatonated names'''
        if type(val) == dict:
            return list(val.keys())
        return val

    def __pull_attributes(self, dict_list):
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
                val = self.__extract_values(key, ast.literal_eval(val))
                if type(val) == list:
                    out[key].update(val)
                else:
                    out[key].add(val)
        self.attributes_ = out
    
    def fit(self, X, y = None):
        try:
            col_1 = X[self.extraction_col]
            if y:
                col_2 = y[self.extraction_col]
            else:
                col_2 = []
        except Exception as e:
            raise e
            
        self.__pull_attributes(np.concatenate([col_1,col_2]))
        self.__fit = True
        self.__set_column_names()
        return self
    
    def __set_column_names(self):
        self.full_columns = []
        self.slim_columns = []
        
        for key, val in self.attributes_.items():
            for i, inner_val in enumerate(val):
                col_name = self.__create_col_names(key, inner_val)[0]
                if i != 0:
                    self.slim_columns.append(col_name)
                self.full_columns.append(col_name)
    
    def get_feature_names(self, drop_first = False):
        if drop_first:
            return self.slim_columns
        else:
            return self.full_columns
    
    def __create_col_names(self, key, vals):
        if type(vals) != list:
            vals = [vals]
        return ["{}{}{}".format(key, self.delim, val) for val in vals] 
    

    def fit_transform(self, X, y = None, drop_first = False, verbose = False):
        self.fit(X, y)
        return self.transform(X, drop_first, verbose)

    def transform(self, X, drop_first = False, verbose = False):
        '''Returns a sparse array with attributes one-hot encoded'''
        if not self.__fit:
            raise ValueError("Transformer must be .fit() first")
            
        if drop_first:
            l = len(self.slim_columns)
            col_names = self.slim_columns
        else:
            l = len(self.full_columns)
            col_names = self.full_columns

        out = lil_matrix((X.shape[0],l))
        
        # Get attribute column
        try:
            dict_list = X[self.extraction_col]
        except Exception as e:
            raise e
            
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
                val = self.__extract_values(key, ast.literal_eval(val))
                potential_col_names = self.__create_col_names(key, val)
                
                indeces = [col_names.index(pcn) for pcn in potential_col_names if pcn in col_names]
                out[i, indeces] = 1
        if verbose:
            print("Transformation Complete")
        return out