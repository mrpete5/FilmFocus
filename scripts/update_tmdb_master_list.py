import json
import requests
import os
import datetime
import gzip

def update_tmdb_master_list():
    # Define the URL for downloading the TMDB master movie list
    today = datetime.date.today().strftime("%m_%d_%Y")  # Get today's date in "MM_DD_YYYY" format
    download_url = f"http://files.tmdb.org/p/exports/movie_ids_{today}.json.gz"

    # Specify the file paths
    download_file_path = "tmdb_movie_master_list.json.gz"
    output_file_path = "webapp/data/tmdb_master_movie_list.json"

    # Download the TMDB master movie list
    response = requests.get(download_url)

    # Check if the download was successful
    if response.status_code == 200:
        # Save the downloaded file
        with open(download_file_path, 'wb') as download_file:
            download_file.write(response.content)

        print("Download completed. File saved as:", download_file_path)

        # Decompress the downloaded file
        with gzip.open(download_file_path, 'rb') as compressed_file:
            # Read the decompressed data
            data = compressed_file.readlines()

        # Initialize list to store the converted data
        converted_data = []

        # Process each line of data
        for line in data:
            # Parse JSON from each line
            movie_data = json.loads(line)

            # Extract relevant fields and create a dictionary
            movie_entry = {
                "original_title": movie_data["original_title"],
                "id": movie_data["id"]
            }

            # Append the dictionary to the list
            converted_data.append(movie_entry)

        # Write the converted data to the output file
        with open(output_file_path, 'w') as output_file:
            json.dump(converted_data, output_file, indent=4)

        print("Processing completed. Output file saved as:", output_file_path)

        # Delete the downloaded file to clean up
        os.remove(download_file_path)
    else:
        print("Failed to download the TMDB master movie list.")

if __name__ == "__main__":
    update_tmdb_master_list()