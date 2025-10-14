import os

from databaseTable import Item

def delete_files_in_directory(directory_path):
    """
    Deletes all files within a specified directory.
    Subdirectories and their contents are not affected.
    """
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        return
    
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a directory.")
        return

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        # Slicing of the ".png" at the end of filename
        image_title = filename[:-4]

        # if image_title is in Item.itemNameUnformatted
        usableItems = Item.query(Item.itemNameUnformatted, Item.itemName).filter_by(usedInCrafting='TRUE');
        """
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")
        else:
            print(f"Skipped (not a file): {file_path}")
        """

def main():
    

if __name__ == "__main__":
    main() # Call the main function when the script is run directly