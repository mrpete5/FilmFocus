""" 

documentation.py
Summary: This script helps developers document their code and provide a better 
            understanding of how to use it with other developers.       
Developed By: Mark, Bill, Traizen, John, and Aaron
Date Created: 10/03/2023
Last Modified: 10/03/2023
Version: 1.0

"""

OUTPUT_DIR = 'help_documentation/'

class Documentation():
    
    def __init__(self) -> None:
        ''' Constructor for the Documentation class. '''
        # TODO: Implement the constructor for the Documentation class.
        
        self.topic = None               # Topic of documentation.
        self.output_filename = None     # File name of the output.
        self.doc_build = None           # Build of the documentation skeleton.

    def run(self) -> None:
        ''' Runs the documentation. '''
        # TODO: Implement the run function for the Documentation class.
        
        print(f"Documentation started.")
                
        self.get_output_filename()                  # Get the documentation topic from user.
        self.build_documentation()                  # Build the documentation.
        
        print(f"Documentation(s) completed successfully.")

    def get_output_filename(self) -> str:
        ''' Get the topic of the documentation from the user. '''
        print(f'   Examples: "Django" or "APIs" or "Tests" or "Models"')
        command = input(' > Please enter the topic of the documentation: ')
        self.topic = command
        print(f'\n   Your topic: {self.topic}')
        self.fix_output_filename()
        
        return self.output_filename

    def fix_output_filename(self) -> str:
        ''' Fix the output file name. '''
        self.output_filename = None                     # Flush the output file name.
        self.output_filename = f'{self.topic}_Help.md'  # Update the output file name.
        
        yes_list = ['y', 'yes']
        flag = True

        while flag:
            print(f'   Output file name: {self.output_filename}')
            confirmation = input(' > Confirm output file name [y/n]: ')
            answer = confirmation.lower()
            
            if answer in yes_list:
                flag = False
                self.output_filename = f'{self.topic}_Help.md'
            else:
                print(f'   Examples: "Tests_Help.md" or "APIs_Help.md"')
                self.topic = input(' > Write the topic: ')
                self.fix_output_filename()      # Rerun the fix_output_filename function.
                flag = False                    # Reset flag to False to prevent infinite loop.

        return self.output_filename

    def set_output_filename(self) -> None:
        ''' Set the output file name. '''
        fixed_name = self.fix_output_filename(self)
        self.output_filename = f'{fixed_name}_Help.md'
        print(f'   Output file name: {self.output_filename}')

    def build_documentation(self) -> None:
        ''' Build the documentation skeleton. '''
        # TODO: Implement the build_documentation function for the Documentation class.
        
        pass

# def main():
#     my_documention = Documentation()
#     my_documention.run()

# if __name__ == '__main__':
#     main()
    
    
    

### Test stuff below this line ###


# entering the file names
firstfile = input("Enter the name of first file ")
secondfile = input("Enter the name of second file ")
firstfile = OUTPUT_DIR + firstfile
secondfile = OUTPUT_DIR + secondfile
 
# # opening both files in read only mode to read initial contents
# f1 = open(firstfile, 'r')
# f2 = open(secondfile, 'r')
 
# # printing the contents of the file before appending
# print('content of first file before appending -', f1.read())
# print('content of second file before appending -', f2.read())
 
# # closing the files
# f1.close()
# f2.close()
 
# opening first file in append mode and second file in read mode
f1 = open(firstfile, 'a+')
f2 = open(secondfile, 'r')
 
# appending the contents of the second file to the first file
f1.write(f2.read())
 
# relocating the cursor of the files at the beginning
f1.seek(0)
f2.seek(0)
 
# printing the contents of the files after appendng
print('content of first file after appending -', f1.read())
print('content of second file after appending -', f2.read())
 
# closing the files
f1.close()
f2.close()