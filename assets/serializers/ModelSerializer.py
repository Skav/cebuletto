from assets.enums.DatabaseEnums import ColumnTypes


class ModelSerializer:
    def __init__(self, required: dict, data: dict, exemption=list):
        """Checks data has required keys, values and data types, exemption hold variables which can be empty
           required should have key name with data type for this key, exemption is optional and should be a list"""
        self.__required = required
        self.__initial_data = data
        self.__exemptions = exemption
        self.data = None
        self.errors = None
        self.__valid = True

        if 'row_id' in data.keys():
            self.__required['row_id'] = ColumnTypes.INT

        self.__check_is_parameters_correct()
        if self.__valid:
            self.__serialize_data()

    def __check_is_parameters_correct(self):
        if not self.__required or type(self.__required) != dict:
            self.__set_error('Invalid value for required!')
        if not self.__initial_data or type(self.__required) != dict:
            self.__set_error('Invalid value for data!')

        if type(self.__exemptions) != list:
            self.__set_error("exemption is not a list!")
            return False

        not_string_exemptions_values = [x for x in self.__exemptions if type(x) != str]
        if not_string_exemptions_values:
            self.__set_error(f"exemptions have not string values: {not_string_exemptions_values}")
            return False

    def __serialize_data(self):
        filtered_data = {k: v for k, v in self.__initial_data.items() if k in self.__required.keys()}
        missing_variables = [x for x in self.__required.keys() if x not in filtered_data.keys() and x not in self.__exemptions]
        if missing_variables:
            self.__set_error(f"{missing_variables} are require!")
            return False

        empty_values = [k for k, v in filtered_data.items() if v is None and k not in self.__exemptions]
        if empty_values:
            self.__set_error(f"{empty_values} are empty!")
            return False

        incorrect_data_types = [k for k, v in filtered_data.items() if type(v) != self.__required[k].value]
        if incorrect_data_types:
            self.__set_error(f"{incorrect_data_types} have incorrect data type!")
            return False

        for k, v in filtered_data.items():
            if type(v) == ColumnTypes.BOOL.value:
                filtered_data[k] = v*1

        self.data = {k: str(v) for k, v in filtered_data.items()}

    def __set_error(self, message: str):
        self.errors = f"{self.errors}; {message}" if self.errors else f"{message}"
        self.__valid = False

    def is_valid(self):
        return self.__valid

