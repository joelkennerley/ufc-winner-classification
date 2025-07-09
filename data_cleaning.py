import pandas as pd
from datetime import datetime

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
    return round(feet * 30.48 + inches * 2.54, 2)

def weight_to_kg(weight_series):
    """
    :param weight_series: series where each weight is measured in lbs
    :return: series where each weight in kg
    """
    split_weight = weight_series.str.split()
    weight = pd.to_numeric(split_weight.str[0], errors='coerce')
    return round(weight / 2.205,2)

def reach_to_cm(reach_series):
    """
    :param reach_series: series where each fighters reach is in inches
    :return: series where reach is measured in cm
    """
    reach_cm = pd.to_numeric(reach_series.str.strip('"'), errors='coerce')
    return round(reach_cm * 2.54, 2)

def dob_to_datetime(dob_series):
    """
    :param dob_series: series which has each fighters d.o.b in form (Jan 21, 1997)
    :return: series which now has dob as a datetime
    """
    return pd.to_datetime(dob_series, format='%b %d, %Y', errors='coerce')

def convert_percentages(percentage_series):
    """
    :param percentage_series: series where each entry is a %
    :return: series where each entry is a proportion
    """
    numerator = pd.to_numeric(percentage_series.str.strip('%'), errors='coerce')
    return numerator/100

def main():
    raw_features = pd.read_csv('raw_features.csv')
    # remove unnecessary columns
    data = raw_features.drop(['method', 'time', 'ref', 'f1_id', 'f1_name', 'f2_id', 'f2_name'], axis=1)
    # replace spaces with _
    data.columns = data.columns.str.replace(' ', '_')

    data['f1_height'] = height_ft_inches_to_cm(data['f1_height'])
    data['f2_height'] = height_ft_inches_to_cm(data['f2_height'])

    data['f1_weight'] = weight_to_kg(data['f1_weight'])
    data['f2_weight'] = weight_to_kg(data['f2_weight'])

    data['f1_reach'] = reach_to_cm(data['f1_reach'])
    data['f2_reach'] = reach_to_cm(data['f2_reach'])

    data['f1_dob'] = dob_to_datetime(data['f1_dob'])
    data['f2_dob'] = dob_to_datetime(data['f2_dob'])

    data['f1_str_acc'] = convert_percentages(data['f1_str_acc'])
    data['f2_str_acc'] = convert_percentages(data['f2_str_acc'])

    data['f1_str_def'] = convert_percentages(data['f1_str_def'])
    data['f2_str_def'] = convert_percentages(data['f2_str_def'])

    data['f1_td_acc'] = convert_percentages(data['f1_td_acc'])
    data['f2_td_acc'] = convert_percentages(data['f2_td_acc'])

    data['f1_td_def'] = convert_percentages(data['f1_td_def'])
    data['f2_td_def'] = convert_percentages(data['f2_td_def'])

    data.to_csv('cleaned_data.csv', index=False)

if __name__ == "__main__":
    main()



