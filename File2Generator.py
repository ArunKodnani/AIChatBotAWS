import json
import boto3
import requests
import time
import csv

if __name__ == '__main__':
    count0=0
    count1=0
    with open("/Users/rahulkeswani/Downloads/AIChatBotAWS-master/File1.csv", 'r') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        file2 = open("/Users/rahulkeswani/Downloads/AIChatBotAWS-master/File2.csv", 'a')
        for row in readCSV:
            #print(row[2])
            #print(row[1])
            if(int(row[1])>400 and float(row[2])>=3.5 and count1<=1000):
                recommendation = 1;
                file2List = [row[0], row[1], row[2],row[3],recommendation]
                count1= count1+1
                writer = csv.writer(file2)
                writer.writerow(file2List)
                file2.flush()

            elif(int(row[1])<400 and float(row[2])<3.5 and count0<=1000):
                recommendation = 0;
                file2List = [row[0], row[1], row[2],row[3], recommendation]
                count0 = count0+1
                writer = csv.writer(file2)
                writer.writerow(file2List)
                file2.flush()

        file2.close()
    csvfile.close()

    # file2 = open("C:/Users/sgaur/Desktop/Cloud/AIChatBotAWS-master/File2.csv", 'a')
    # file2List = [business['id'], business['review_count'], business['rating'], term.split(" ")[0]]
    # with file2:
    #     writer = csv.writer(file2)
    #     writer.writerow(file2List)
    #     file2.flush()
    # file2.close()