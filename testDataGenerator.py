import pandas as pd

df1 = pd.read_csv("/Users/rahulkeswani/Downloads/AIChatBotAWS-master/File1.csv")
df2 = pd.read_csv("/Users/rahulkeswani/Downloads/AIChatBotAWS-master/File2.csv")

df1.columns = ['RestaurantID', 'NumberOfReviews', 'Rating', 'Cuisine']

print(len(df1))
print(len(df2))

#Removing the 400 training rows from File1.csv to make the Test Data
df3 = df1.append(df2)
df3 = df3.drop_duplicates(subset=['RestaurantID'], keep=False)
df3 = df3.reset_index(drop=True)
df3 = df3.drop(['Recommended'],axis=1)
columnTitles = ['RestaurantID', 'NumberOfReviews', 'Rating', 'Cuisine']
df3=df3.reindex(columns=columnTitles)
df3 = df3.reset_index(drop=True)
print(len(df3))

#Writing the newly generated dataframe to CSV file
df3.to_csv("/Users/rahulkeswani/Downloads/AIChatBotAWS-master/File3.csv",sep=",")

