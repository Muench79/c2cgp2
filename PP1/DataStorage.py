import time
import json
import os
import logging
from typing import Union

# Create logger
logger = logging.getLogger(__name__)

def log_message(level, message, **kwargs):
    # Format and generate log message
    param_str = " | ".join(f"{key}={value}" for key, value in kwargs.items())
    full_message = f"{message} | {param_str}" if param_str else message


    if level == "DEBUG":
        logger.debug(full_message)
    elif level == "INFO":
        logger.info(full_message)
    elif level == "WARNING":
        logger.warning(full_message)
    elif level == "ERROR":
        logger.error(full_message)
    elif level == "CRITICAL":
        logger.critical(full_message)
    else:
        logger.info(f"Unbekannter Loglevel '{level}': {full_message}")


class DataStorage():
    """A class for data storage

    Attributes:
        __file_ext (tuple): Includes the supported file formats
        storage (bool): Activates data storage
    """
    __file_ext = ('.csv', '.json') # supported file formats
    
    def __init__(self, storage : bool = True) -> None:
        """Initializes the data storage
        Args:
            storage (bool, optional): Whether data storage should be enabled.
                True (default) - Enable data storage
                False          - Disable data storage
        """
        log_message("DEBUG", 'Create DataStorage object')
        self._data = {} 
        self._data_prepared = []
        self._storage = storage

    def add_data(self, key : (str), value : Union[int, float], timestamp : (float) = None) -> None:
        """Adds data to the data store.
        Args:
            key (str): key of value
            value (int, float): value of the key
        """
        if not timestamp:
            timestamp = time.time()
        
        if self._storage:
            if key not in self._data:
                self._data[key] = [(timestamp, value)]
                log_message("DEBUG", 'Add data (new key): ', Key = key, Data = (timestamp, value))
            else:
                self._data[key].append((timestamp, value))
                log_message("DEBUG", 'Add data: ', Key = key, Data = (timestamp, value))
    
    def get_data(self) -> dict:
        """
        Returns:
            dict: all saved data
        """
        log_message("DEBUG", 'get_data(): Return self._data', data = self._data)
        return self._data

    def get_keys(self) -> tuple:
        """
        Returns:
            tuple: all existing keys
        """
        log_message("DEBUG", 'get_keys(): Return self._data.keys())', keys = self._data.keys())
        return tuple(self._data.keys())
    
    def clear_data(self) -> None:
        """Deletes all previously stored data
        """
        logging.debug('Clear data')
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
        log_message("DEBUG", '_data_preparation(): ', data_count = len(self._data_prepared))
        
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
            log_message("DEBUG", '_data_to_csv(): ', data_count = len(linescsv))
            return ""
        else:
            log_message("DEBUG", '_data_to_csv(): ', data_count = len(linescsv))
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
        log_message("DEBUG", '_save_data_json(): ', pathname = path)
        try:
            with open(path, 'w', encoding = 'utf-8') as jf:
                json.dump(self._data_prepared, jf, ensure_ascii=False, indent=2)
        except Exception as e:
            log_message("ERROR", '_save_data_json(): ', pathname = path, info = e)
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
        log_message("DEBUG", '_save_data_csv(): ', pathname = path)
        try:
            with open(path, 'w', encoding = 'utf-8') as csvf:
                csvf.write(self._data_to_csv())
        except Exception as e:
            log_message("ERROR", '_save_data_csv(): ', pathname = path, info = e)
            return -1
        return 0

    def save_data(self, path, format : str = '' , overwrite : bool = False) -> int:
        """Saves the data to a file and returns -1 and returns detailed information

            Args:
                path (str): File path
                overwrite (bool): True (The file will be overwritten if it already exists), False (The file will not be overwritten. The filename is appended with a timestamp.)

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
            log_message("ERROR", 'save_data(): The filename was not specified', path = path, format = format, overwrite = overwrite)
            return -1 # The filename was not specified
        if not os.path.isdir(folder):
            log_message("ERROR", 'save_data(): The directory does not exist', path = path, format = format, overwrite = overwrite)
            return -2 # The directory does not exist
        if not format: 
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
                log_message("ERROR", 'save_data(): The file format is not supported', path = path, format = format, overwrite = overwrite)
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
                log_message("ERROR", 'save_data(): The file format is not supported', path = path, format = format, overwrite = overwrite)
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
                log_message("ERROR", 'save_data(): The file already exists', path = path, format = format, overwrite = overwrite)
                return -4 # The file already exists
        if ext2 == self.__file_ext[0]:
            r = self._save_data_csv(os.path.join(folder,name + timestamp + counterstr + ext2))
            if r < 0:
                log_message("ERROR", 'save_data(): An error occurred while writing the file', path = path, format = format, overwrite = overwrite)
                return -5 # An error occurred while writing the file
        elif ext2 == self.__file_ext[1]:
            r = self._save_data_json(os.path.join(folder,name + timestamp + counterstr + ext2))
            if r < 0:
                log_message("ERROR", 'save_data(): An error occurred while writing the file', path = path, format = format, overwrite = overwrite)
                return -5 # An error occurred while writing the file
        else:
            log_message("ERROR", 'save_data(): Unknown error (please contact support)', path = path, format = format, overwrite = overwrite)
            return -6 # Unknown error (please contact support)

    @property
    def storage(self) -> bool:
        """Query the data storage state
        Returns:
            bool: True  (Data storage is active)
                  False (Data storage is not active. Therefore, no data is being recorded)
        """
        log_message("DEBUG", 'storage (getter): Return self._storage)', storage = self._storage)
        return self._storage
    
    @storage.setter
    def storage(self, x : bool) -> None:
        """Changes the state of data storage (True  (Data storage is active), False (Data storage is not active. Therefore, no data is being recorded))
        """
        self._storage = x
        log_message("DEBUG", 'storage (setter): Set self._storage)', storage = self._storage)

if __name__ == '__main__':
    help(DataStorage)
    x = DataStorage()
    x.add_data("Test", 9)
    x.add_data("Test", 10)
    x.save_data('tt.json')
    pass