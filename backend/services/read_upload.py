import pandas as pd


def type_check(file):
    """
    Checks the type of uploaded file.
    Args:
        file: The uploaded file object.
    Returns:
        The type - 'xlsx' or 'csv'.
    """
    if file.name.endswith('.xlsx'):
        return 'xlsx'
    elif file.name.endswith('.csv'):
        return 'csv'
    else:
        raise ValueError("Unsupported file type. Please upload a .xlsx or .csv file.")


def read_upload(file):
    """
    Reads an uploaded file and returns a DataFrame.
    Args:
        file: The uploaded file object.
    Returns:
        A DataFrame containing the data from the uploaded file.
    """
    file_type = type_check(file)
    try:
        # Read the uploaded file into a DataFrame
        if file_type == 'xlsx':
            df = pd.read_excel(file)
        elif file_type == 'csv':
            df = pd.read_csv(file)

        return df

    except Exception as e:
        print(f"Error reading uploaded file: {e}")
        return None


def determine_columns(df):
    """
    Determines the relevant columns in the DataFrame for item code / item name, and item quantity.
    Args:
        df: The DataFrame to analyze.
    Returns:
        df with column names
    """
    col1, col2 = df.columns[:2]  # Get the first two columns
