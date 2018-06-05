
import pandas as pd
import os

import re
import requests
import tabula
from bs4 import BeautifulSoup
from io import BytesIO, StringIO

from pdfminer.converter import TextConverter, HTMLConverter, XMLConverter, PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed


def read_pdf():
    # Please change the folder name before run this script
    pdf_folder = '/home/bichitra/Desktop/project/pdf/'

    for file_name in os.listdir(pdf_folder):
        areas = []
        if '.pdf' not in file_name:
            continue
        if file_name == 'EICHERMOT.pdf':
            areas = get_area(file_name)
            # script_file = open(script_dir + 'tabula-' + file_name[:-4] + '.sh', 'r')
            # area_lines = script_file.readlines()
            # areas = []
            # for line in area_lines:
            #     area = re.findall(r'-a(.*)-p', line)
            #     area = tuple(area[0].strip().split(","))
            #     areas.append(area)
            # areas = [(180.443, 305.079, 280.152, 549.886), (248.156, 54.319, 353.817, 299.126)]
        if file_name == '1c1edeee-a13e-4b2e-90be-eb1dd03c3384.pdf':
            areas = get_area(file_name)
            # areas = [(363.444,45.384,423.708,546.096)]
        if file_name == 'd9f8e6d9-660b-4505-86f9-952e45ca6da0.pdf':
            areas = get_area(file_name)
            # areas = [(341.193,58.044,446.862,526.858)]
        if file_name == 'a6b29367-f3b7-4fb1-a2d0-077477eac1d9.pdf':
            areas = get_area(file_name)
            # areas = [(423.566,64.706,482.322,526.575)]
        csv_path = os.path.join(pdf_folder, file_name.replace('.pdf', ''))
        for index, area in enumerate(areas):
            filepath = pdf_folder + file_name
            csv = tabula.read_pdf(filepath, encoding='utf-8', stream=True, pages=1, guess=False, area=area)
            # csv = tabula.read_pdf(filepath, multiple_tables=False, pages=1, stream=True, lattice=True,
            #                       guess=False, area=area)
            csv = pre_process(csv)
            # for i, file in enumerate(csv):
            csv.to_csv(path_or_buf=csv_path + f'_{index}_{0}.csv', sep=",", index=False)

    return


def get_area(file_name):
    script_dir = '/home/bichitra/Desktop/project/sh_file/'
    script_file = open(script_dir + 'tabula-' + file_name[:-4] + '.sh', 'r')
    area_lines = script_file.readlines()
    areas = []
    for line in area_lines:
        area = re.findall(r'-a(.*)-p', line)
        area = tuple(area[0].strip().split(","))
        areas.append(area)
    return areas


def pre_process(dataframe):
    nan_index = pd.isnull(dataframe).any(1).nonzero()[0]
    dataframe = dataframe.fillna('')
    dataframe = dataframe.astype(str)
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
                row_index += 1
            else:
                new_value = list(map(str.__add__, dataframe.loc[index - 1] + ' ', dataframe.loc[index].fillna('')))
                dataframe.loc[index - 1] = new_value
                exact_index = row_index = index

    dataframe.drop(dataframe.index[[nan_index]], inplace=True)
    dataframe.reset_index(inplace=True, drop=True)
    return dataframe


def html_convert():
    pdf_folder = '/home/bichitra/Desktop/project/pdf/'
    for file_name in os.listdir(pdf_folder):
        if file_name == 'EICHERMOT.pdf':
            file_name = pdf_folder + 'EICHERMOT'
            htmlfile = open(file_name + '.html', 'w+')
            files = {'f': (file_name + '.pdf', open(file_name + '.pdf', 'rb'))}
            response = requests.post('https://pdftables.com/api?key=r4i5cvh74tvn', files=files)
            response.raise_for_status()  # ensure we notice bad responses
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    htmlfile.write(chunk)
                htmlfile.flush()
            htmlfile.close()
            htmldata = ''
            with open(file_name + '.html', 'r') as htmlfile:
                htmldata = htmldata + htmlfile.read()
            print(htmldata)
            soup = BeautifulSoup(htmldata, 'html.parser')


def pdfminer_use():
    pdf_folder = '/home/bichitra/Desktop/project/pdf/'
    file_name = pdf_folder + 'EICHERMOT.pdf'
    fp = open(file_name, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    print(document.get_outlines())

    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    # Create a PDF device object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        layout = device.get_result()
        print(layout)


def check():
    from pdfminer.pdfinterp import PDFResourceManager
    from pdfminer.converter import HTMLConverter, TextConverter
    from pdfminer.layout import LAParams
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    converter = HTMLConverter if format == 'html' else TextConverter
    device = converter(rsrcmgr, out_file, codec='utf-8', laparams=laparams)
    process_pdf(rsrcmgr, device, in_file, pagenos=[1], maxpages=1)

    # https://github.com/scraperwiki/scraperwiki-python/blob/master/scraperwiki/utils.py
    with contextlib.closing(tempfile.NamedTemporaryFile(mode='r', suffix='.xml')) as xmlin:
        cmd = 'pdftohtml -xml -nodrm -zoom 1.5 -enc UTF-8 -noframes "%s" "%s"' % (
            pdf_filename, xmlin.name.rpartition('.')[0])
        os.system(cmd + " >/dev/null 2>&1")
        result = xmlin.read().decode('utf-8')


def convert_pdf(format='html', codec='utf-8', password=''):
    pdf_folder = '/home/bichitra/Desktop/project/pdf/'
    file_name = '1c1edeee-a13e-4b2e-90be-eb1dd03c3384.pdf'
    # file_name = 'EICHERMOT.pdf'
    file_name = pdf_folder + file_name
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
    if format == 'text':
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    fp = open(file_name, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()
    soup = BeautifulSoup(text, 'html.parser')
    htmlfile = open(file_name + '.html', 'w+')
    htmlfile.write(str(soup))
    htmlfile.flush()
    htmlfile.close()
    return soup


if __name__ == '__main__':
    # print(convert_pdf())
    # pdfminer_use()
    # html_convert()
    read_pdf()
    print('Csv file generated successfully')