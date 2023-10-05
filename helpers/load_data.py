import os
import pandas as pd

# Function to process a single recording folder
def process_recording(directory):
    """
    Process a single recording folder and return a single DataFrame

    Args:
        directory (str): Path to the recording folder

    Returns:    
        merged_data (DataFrame): A single DataFrame containing all sensor data from the recording
    """
    # Specify files of interest
    files = ['Accelerometer.csv', 'Gyroscope.csv', 'Gravity.csv']

    # Create an empty list to store DataFrames from each CSV file
    dataframes = []

    # Loop through the files in the directory and read each CSV file into a DataFrame
    for filename in os.listdir(directory):
        if filename in files:
            filepath = os.path.join(directory, filename)
            try:
                df = pd.read_csv(filepath)
                if not df.empty:
                    if 'time' in df.columns:
                        # Only keep 'time' column in the first DataFrame
                        if not dataframes:
                            dataframes.append(df)
                        else:
                            dataframes.append(df.drop(columns='seconds_elapsed'))
            except pd.errors.EmptyDataError:
                print(f"Skipping empty file: {filename}")

    # Merge the DataFrames using the 'time' column as the key
    merged_data = dataframes[0].set_index('time')

    for i, df in enumerate(dataframes[1:], start=2):
        if 'time' in df.columns:
            # Specify custom suffixes for columns to avoid duplicates
            suffix = f'_{i}'
            merged_data = pd.merge_asof(merged_data, df.set_index('time'), on='time', suffixes=('', suffix))

    # Reset the index
    #merged_data.reset_index(inplace=True)

    # Columns to be normalized
    sensor_columns = merged_data.columns[3:]

    # Normalize the specified sensor data columns in place using .loc
    merged_data.loc[:, sensor_columns] = (merged_data[sensor_columns] - merged_data[sensor_columns].mean()) / merged_data[sensor_columns].std()

    return merged_data

# Function to combine multiple processed recordings
def batch_process_recordings(directory):
    """
    Process all recordings in the specified directory and return a single DataFrame

    Args:
        directory (str): Path to the directory containing the recording folders

    
    Returns:
        data_merged (DataFrame): A single DataFrame containing all processed recordings
    """

    # Create an empty list to store processed DataFrames for each recording
    processed_dataframes = []

    # Iterate through the recording folders and process each one
    for user_folder in os.listdir(directory):
        print(f"Processing user: {user_folder}")
        user_path = os.path.join(directory, user_folder)
        if os.path.isdir(user_path):
            for recording_folder in os.listdir(user_path):
                recording_path = os.path.join(user_path, recording_folder)
                if os.path.isdir(recording_path):
                    processed_df = process_recording(recording_path)
                    processed_dataframes.append(processed_df)

    # Concatenate processed DataFrames vertically to create `data_merged`
    data_merged = pd.concat(processed_dataframes, keys=os.listdir(directory))

    return data_merged