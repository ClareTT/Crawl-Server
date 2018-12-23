# -*- coding: utf-8 -*-
"""
Created on Thu Dec  6 21:04:54 2018

@author: llwang
"""


import requests
import time
import pandas as pd
import csv


def get_dataframeprocessing(webContent):
    """
    content为网页中获取的全部去冗余信息
    该函数将其按照换行和空格分解为一个DataFrame，并返回该DataFrame
    
    """
    contentList = webContent.split('\n')
    
    dataframeProcessing = pd.DataFrame()
    for i in range(len(contentList) - 1):
        decomposedSingleRowData = contentList[i].split(' ')
        
        serialNum = int(decomposedSingleRowData[0][0:6])
        deviceName = decomposedSingleRowData[1]
        longitude = decomposedSingleRowData[2]
        latitude = decomposedSingleRowData[3]
        altitude = decomposedSingleRowData[4]
        star = decomposedSingleRowData[5]
        date = decomposedSingleRowData[6]
        time = decomposedSingleRowData[7][0:8]
    
        dataframeProcessing = dataframeProcessing.append(pd.Series([serialNum, 
                                                                    deviceName, 
                                                                    longitude, 
                                                                    latitude, 
                                                                    altitude, 
                                                                    star, 
                                                                    date, 
                                                                    time]), 
                                                        ignore_index = True)
    
    return dataframeProcessing




if __name__ == '__main__':
    
    try:
        requests.packages.urllib3.disable_warnings()
        url = 'https://yun.steering.ai/zh-hans/fatigue/table/gps/'
        columnNames = ['serialNum', 
                       'deviceName', 
                       'longitude', 
                       'latitude', 
                       'altitude', 
                       'star', 
                       'date', 
                       'time']
        csvFileName = input('键入将存入的.csv文件名（若不在当前路径下，请键入全部路径）') + '.csv'
        
        try:
            existingData = pd.read_csv(csvFileName, sep = ',', encoding = 'utf_8_sig')
            theLastSerialNum = int(existingData.iat[-1, 0])
        except:
            theLastSerialNum = 1
            with open(csvFileName, 'w+', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(columnNames)
        
        numberOfAttempts = 0
        while True:
            try:
                r = requests.get(url, verify = False)
                webContent = r.content
                webContent = webContent.decode()
                
                dataframeProcessing = get_dataframeprocessing(webContent)
                totalLength = len(dataframeProcessing)
                difference = dataframeProcessing.iat[-1, 0] - theLastSerialNum
                if difference > totalLength:
                    difference = totalLength
                if difference:
                    appendData = dataframeProcessing.iloc[(totalLength-difference):totalLength]
                    appendData.to_csv(csvFileName, header = False, index = False, 
                                sep = ',', mode = 'a+', encoding = 'utf_8_sig')
            
                theLastSerialNum = dataframeProcessing.iat[-1, 0]
                
                numberOfAttempts = numberOfAttempts + 1
                print(str(numberOfAttempts) + 
                      ' times trying...  ' + 
                      str(int(difference)) + 
                      ' rows of data has been appended.' + 
                      '\nPress Ctrl+C to terminate search.')
                time.sleep(6) 
                
            except Exception as e:
                print(Exception,':',e)
                print('''\nA problem exists, 
check the error information above to find out what is happening!''')
                break
    except KeyboardInterrupt:
        print('See you next time!')


