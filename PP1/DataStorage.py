import time
import json
import os
import logging
from typing import Union

class DataStorage():
    """A class for data storage

    Attributes:
        __file_ext (tuple): Includes the supported file formats
        storage (bool): Activates data storage
    """
    __file_ext = ('.csv', '.json') # supported file formats

    def __init__(self, storage : bool = True) -> None:
        """
        Args:
            storage (bool): Enable (True) or disable (False) data storage. Default value: enabled (True).
        """
        self._data = {} 
        self._data_prepared = []
        self._storage = storage

    def add_data(self, key : (str), value : Union[int, float]) -> None:
        """
        Args:
            key (str): key of value
            value (int, float): value of the key
        """
        if self._storage:
            if key not in self._data:
                self._data[key] = [(time.time(), value)]
            else:
                self._data[key].append((time.time(), value))
    
    def get_data(self) -> dict:
        """
        Returns:
            dict: all saved data
        """
        return self._data

    def get_keys(self) -> tuple:
        """
        Returns:
            tuple: all existing keys
        """
        return tuple(self._data.keys())
    
    def clear_data(self) -> None:
        """Deletes all previously stored data
        """
        self._data = {}
        self._data_prepared = []
    
    def _data_preparation(self) -> None:
        """Preparing the data for further processing (saving it to a file)
        """
        self._data_prepared = []
        for k, v in self._data.items():
            for t in v:
                self._data_prepared.append({"data_key" : k, "data_time" : t[0], "data_measurement_value" : t[1]})
        if len(self._data_prepared) > 1:
            self._data_prepared.sort(key = lambda x: x['data_time'])

    def _data_to_csv(self) -> str:
        """Converts the data to csv format

            Returns:
                str: data in csv format
        """
        self._data_preparation()
        print(self._data_prepared)
        print(self.get_keys())
        datakeys = self.get_keys()
        linehead = [f"{i}" for i in datakeys]
        linehead = 'time,' + ','.join(linehead)
        linescsv = ''
 
        for data in self._data_prepared:
            if linescsv:
                linescsv += '\n'
            linescsv += f"{data['data_time']}"
            for dk in datakeys:
                if dk in data['data_key']:
                    linescsv += f",{data['data_measurement_value']}"
                else:
                    linescsv += ',NaN'
        if not datakeys:
            return ""
        else:
            return linehead + '\n' + linescsv
        
    def _save_data_json(self, path : str) -> int:
        """Saves the data to a file in json format and returns -1 in case of an error

            Args:
                path (str): File path

            Returns:
                int: 0 (storage successful)
                    -1 (storage failed)
        """
        self._data_preparation()
        try:
            with open(path, 'w', encoding = 'utf-8') as jf:
                json.dump(self._data_prepared, jf, ensure_ascii=False, indent=2)
        except:
            return -1
        return 0
    
    def _save_data_csv(self, path):
        """Saves the data to a file in csv format and returns -1 in case of an error

            Args:
                path (str): File path

            Returns:
                int: 0 (storage successful)
                    -1 (storage failed)
        """
        try:
            with open(path, 'w', encoding = 'utf-8') as csvf:
                csvf.write(self._data_to_csv())
        except:
            return -1
        return 0

    def save_data(self, path, format : str = '' , overwrite : bool = False) -> int:
        """Saves the data to a file and returns -1 and returns detailed information

            Args:
                path (str): File path
                overwrite (bool): 

            Returns:
                int: 0 (Storage successful)
                    -1 (The filename was not specified)
                    -2 (The directory does not exist)
                    -3 (The file format is not supported)
                    -4 (The file already exists)
                    -5 (An error occurred while writing the file)
                    -6 (Unknown error (please contact support))
        """
        folder = os.path.dirname(path)
        filename = os.path.basename(path)
        name, ext = os.path.splitext(filename)
        ext2 = ''
        if filename == '':
            return -1 # The filename was not specified

        if not os.path.isdir(folder):
            return -2 # The directory does not exist
        elif not format: 
            # There is no specified file format
            if ext == '':
                # ?-File -> .csv
                ext2 = self.__file_ext[0]
            elif ext.lower() == self.__file_ext[0]:
                # csv-File -> .csv
                ext2 = self.__file_ext[0]
            elif ext.lower() == self.__file_ext[1]:
                # json-File -> .json
                ext2 = self.__file_ext[1]
            else:
                return -3 # The file format is not supported
        else:
            # the file format is predefined
            if format.lower() == self.__file_ext[0]:
                # csv-File -> .csv
                ext2 = self.__file_ext[0]
            elif format.lower() == self.__file_ext[1]:
                # json-File
                ext2 = self.__file_ext[1]
            else:
                return -3 # The file format is not supported
            
        timestamp = ''
        counterstr = ''
        counter = 0
        if not overwrite:
            # Append timestamps to filenames
            timestamp = time.strftime("_%Y-%m-%d_%H-%M-%S")
            while os.path.exists(os.path.join(folder,name + timestamp + counterstr + ext2)) and counter < 10000:
                counterstr = f'_{counter:04}'
                counter += 1
            if counter > 9999:
                return -4 # The file already exists
        if ext2 == self.__file_ext[0]:
            r = self._save_data_csv(os.path.join(folder,name + timestamp + counterstr + ext2))
            if r < 0:
                return -5 # An error occurred while writing the file
        elif ext2 == self.__file_ext[1]:
            r = self._save_data_json(os.path.join(folder,name + timestamp + counterstr + ext2))
            if r < 0:
                return -5 # An error occurred while writing the file
        else:
            return -6 # Unknown error (please contact support)

    @property
    def storage(self) -> bool:
        """Query the data storage state
        Returns:
            bool: True  (Data storage is active)
                  False (Data storage is not active. Therefore, no data is being recorded)
        """
        return self._storage
    
    @storage.setter
    def storage(self, x : bool) -> None:
        """Changes the state of data storage (True  (Data storage is active), False (Data storage is not active. Therefore, no data is being recorded))
        """
        self._storage = x

if __name__ == '__main__':
    x = DataStorage()
    x.add_data("Test", 9)
    x.add_data("Test", 10)
    x.save_data('./tt.csv')
    pass