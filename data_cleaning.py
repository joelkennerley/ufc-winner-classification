import pandas as pd


def height_ft_inches_to_cm(height_series):
    """
    :param height_series: each entry looks like \"5' 7\"\"
    :return: float of height in cm
    """
    # removes " & ' characters
    height_series = height_series.str.replace('"', '').str.replace("'", '')

    # split into ft and inches and handle empty vals like '--'
    split_height = height_series.str.split()
    feet = pd.to_numeric(split_height.str[0], errors='coerce')
    inches = pd.to_numeric(split_height.str[1], errors='coerce')
    return feet * 30.48 + inches * 2.54

def main():
    raw_features = pd.read_csv('raw_features.csv')
    data = raw_features.drop(['method', 'time', 'ref', 'f1_id', 'f1_name', 'f2_id', 'f2_name'], axis=1)
    data['f1_height'] = height_ft_inches_to_cm(data['f1_height'])
    data['f2_height'] = height_ft_inches_to_cm(data['f2_height'])

    print(data['f2_height'])

    # print(raw_features.columns.tolist())

if __name__ == "__main__":
    main()



