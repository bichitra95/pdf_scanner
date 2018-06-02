import pandas as pd
import os
import tabula


def read_pdf():
    # Please change the folder name before run this script
    pdf_folder = '/home/bichitra/Desktop/project/pdf/'

    for file_name in os.listdir(pdf_folder):
        areas = []
        if '.pdf' not in file_name:
            continue
        if file_name == 'EICHERMOT.pdf':
            areas = [(180.443, 305.079, 280.152, 549.886), (248.156, 54.319, 353.817, 299.126)]
        if file_name == '1c1edeee-a13e-4b2e-90be-eb1dd03c3384.pdf':
            areas = [(363.444,45.384,423.708,546.096)]
        if file_name == 'd9f8e6d9-660b-4505-86f9-952e45ca6da0.pdf':
            areas = [(341.193,58.044,446.862,526.858)]
        if file_name == 'a6b29367-f3b7-4fb1-a2d0-077477eac1d9.pdf':
            areas = [(423.566,64.706,482.322,526.575)]
        csv_path = os.path.join(pdf_folder, file_name.replace('.pdf', ''))
        for index, area in enumerate(areas):
            filepath = pdf_folder + file_name
            csv = tabula.read_pdf(filepath, area=area, encoding='latin1', nospreadsheet=True, pages=1, guess=False)
            csv = pre_process(csv)
            csv.to_csv(path_or_buf=csv_path + f'_{index}.csv', sep=",", index=False)

    return


def pre_process(dataframe):
    nan_index = pd.isnull(dataframe).any(1).nonzero()[0]
    column_index = 0
    exact_index = None
    row_index = None
    for index in nan_index:
        if index == column_index:
            column_name = dataframe.columns
            new_column_name = list(map(str.__add__, column_name + ' ', dataframe.iloc[index].fillna('')))
            dataframe.columns = new_column_name
            column_index +=1
        else:
            if row_index == index - 1:
                new_value = list(map(str.__add__, dataframe.loc[exact_index-1] + ' ', dataframe.loc[index].fillna('')))
                dataframe.loc[exact_index-1] = new_value
                row_index +=1
            else:
                new_value = list(map(str.__add__, dataframe.loc[index - 1] + ' ', dataframe.loc[index].fillna('')))
                dataframe.loc[index - 1] = new_value
                exact_index = row_index = index

    dataframe.drop(dataframe.index[[nan_index]], inplace=True)
    dataframe.reset_index(inplace=True, drop=True)
    return dataframe


if __name__ == '__main__':
    read_pdf()
    print('Csv file generated successfully')