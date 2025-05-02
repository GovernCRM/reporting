def filter_data(df, **filters):
    for column, value in filters.items():
        if value is not None:
            if isinstance(value, (list, tuple)) and len(value) == 2:  # Handle range filters
                start, end = value
                df = df[(df[column] >= str(start)) & (df[column] <= str(end))]
            elif isinstance(value, str):  # Handle string filters
                df = df[df[column].str.contains(value, case=False, na=False)]
            else:  # Handle exact match filters
                df = df[df[column] == value]
    return df
