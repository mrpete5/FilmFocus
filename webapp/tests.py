"""
Name of code artifact: tests.py
Brief description: Contains all tests and testing logic for the FilmFocus web application, 
                    including multiple edge cases, logging, documentation. Made to be very 
                    adaptive and easy to understand.
Programmer’s name: Mark
Date the code was created: 10/02/2023
Dates the code was revised: 10/06/2023
Brief description of each revision & author: Initialized code and basic structure (Mark).
Preconditions: Django environment must be set up correctly, and necessary environment variables (API keys) must be available.
Acceptable and unacceptable input values or types: Functions expect specific types as documented in their respective comments.
Postconditions: Functions return values or modify the database as per their documentation.
Return values or types: Varies based on the function.
Error and exception condition values or types that can occur: Errors can occur if API limits are reached or if there are issues with the database.
Side effects: Some functions modify the database.
Invariants: None.
Any known faults: None.
"""

"""
    # TODO: Write your tests here.
            - Logging:
                - Add logging so failures display to the console.
                - Add logging so results of the full test are written to a new file.
                - Output file format should be:
                    - Format: "output_MM_DD_YYYY_HH_mm_ss.txt" with the date and time. (Allow for 24 hour clock).
                    - Example: output_10_02_2023_17_30_07.txt (Default, or something similar.)
            - Documentation:
            - Edge cases:
            - Write some tests that you would like to test.
            - Write some edge cases that you would like to test.
            
"""

import os
from django.test import TestCase
import time
import datetime

# Constant variables and other starter variables/functions.
OUTPUT_DIR = '/webapp/outputs/'


# Create your tests here.
class Test():
    
    def __init__(self) -> None:
        ''' Constructor for the Test class. '''
        # TODO: Implement the constructor for the Test class.
        
        self.input_file_name = 'test_input_file_v1.txt' # Initialize the input file name.
        self.output_file_name = 'test_output_v1.txt'    # Initialize the output file name.
        self.is_input_valid = False                     # Initialize the input file name validity flag.
        self.file_data = []                             # Initialize the file data list. Optionally, change the data structre.
    
    def run(self) -> None:
        ''' Runs the test. '''
        # TODO: Implement the run function for the Test class.
        
        print(f"Test started.")
        
        # self.test_display()               # Run the test display function.
        self.verify_input_file()            # Run the test verify_input_file function.
        
        print(f"Test output file name: /webapp/outputs/{self.output_file_name}")
        print(f"Test completed successfully.")
    
    def read_from_file(self) -> None:
        ''' Read the test file. '''
        # TODO: Implement the read_file function within the Test class.
        
        # Read the file.
        if self.is_input_valid: 
            with open(self.input_file_name, 'r') as file:
                for line in file.readlines():
                    # print(line)
                    self.file_data = line.strip() # Strip the newline character from the file data.

    def write_to_file(self) -> None:
        ''' Write the test file. '''
        # TODO: Implement the write_to_file function within the Test class.
        
        self.generate_output_file_name()
        
        # Include the output directory in the output file name.
        self.output_file_name = str(OUTPUT_DIR + self.output_file_name)
        
        # Write the output file.
        with open(self.output_file_name, 'w', newline='\n') as file:
            # TODO: Finish implementation of the write_to_file function.
            
            # file.write(self.file_data)            # Test version
            file.writelines(self.file_data)

    def verify_input_file(self) -> None:
        ''' Verify the input file name and type. '''
        # TODO: Implement the verify_input_file_name and type function within the Test class.
        
        if not os.path.isfile(self.input_file_name):
            print(f"The input file name '{self.input_file_name}' does not exist in the directory.")
            print(f"Creating: the input file name '{self.input_file_name}' in the directory.")
            self.is_input_valid = False     # False, because the newly created input file needs to be verified.
            self.create_file(file_function="input_file")
            return
        else:
            self.is_input_valid = True
            # print(f"The input file name '{self.input_file_name}' is valid.") # Test version, remove later.

    def create_file(self, file_function="input_file") -> None:
        """ Create a new file name. """
        # TODO: Implement the create_file function within the Test class.
        
        self.input_file_name = f'{OUTPUT_DIR}/test_input_file_v1.txt'
        print(f'Test remove: {self.input_file_name}')
        file1 = open(self.input_file_name,"a")
        
        print(file1.read())                     # Test version, remove later.
        
        if file_function == "input_file":
            file1.write(self.file_data)
        elif file_function == "output_file":
            new_outFile = f"test_output_file_v1_{datetime.datetime.now}.txt"
            self.output_file_name = new_outFile
        else:
            print(f"The file function '{file_function}' is invalid.")
            return
        file1.close()

    def generate_output_file_name(self) -> None:
        ''' Generate the output file name. '''
        # TODO: Implement the generate_output_file function within the Test class.
        
        date_time_format = "%MM/%DD/%YYYY_%HH_%mm:%ss"
        date_time_value = date_time_format  # TODO: Temporary fix. Remove later.
        
        # TODO: finish implementation of the date_time_value.
        # date_time_value = None
                
        self.output_file_name = f"output_{date_time_value}.txt"
        pass    # 'pass' is a reserved word in Python to skip the function.

    def test_display(self) -> None:
        ''' Display the test page. '''
        # TODO: Implement the test_display function within the Test class.
       
        pass

def main():
    my_test = Test()    # Create a new instance of the Test class.
    my_test.run()       # Run the test.
    
if __name__ == "__main__":
    main()




# # tests.py

# import unittest 
# from services import MovieService

# class TestMovieService(unittest.TestCase):

#     def test_search_success(self):
#         service = MovieService()
#         results = service.search_movies('The Matrix')
        
#         self.assertGreater(len(results), 0)
#         self.assertEqual(results[0].title, 'The Matrix')
        
#     def test_search_no_results(self):
#         service = MovieService()
#         results = service.search_movies('asdfasdfasdf')
        
#         self.assertEqual(len(results), 0)
        
#     def test_get_popular(self):
#         service = MovieService()
#         results = service.get_popular_movies(page=1)
        
#         self.assertGreater(len(results), 0)
#         self.assertIsInstance(results[0], Movie)
        

# if __name__ == '__main__':
#     unittest.main()