###################################
#price safety fuel economy
###################################
import requests
from bs4 import BeautifulSoup
make = ["ford","hyundai","honda","toyota"]
model = ["escape","santa-fe","cr-v","rav4"]
f= open("car_psf.csv","w+")
f.write("car, price, safety rating, fuel economy\n")
for i in range(4):
    url='https://www.thecarconnection.com/overview/'+make[i]+'_'+model[i]+"_2019"
    rw=make[i]+" " + model[i]

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    rw=rw + "," + soup.find("div", {"class":"trim-msrp"}).text.replace(",","")
    flg=0
    for link in soup.findAll("td"):
        if (flg == 1):
            rw=rw +","+ link.text
            flg=0
        if (link.text == 'Safety' or link.text == 'Fuel Economy'):
            flg=1
    f.write(rw+"\n")
f.close()

######################################
#Resale score
######################################
make = ["ford","hyundai","honda","toyota"]
model = ["escape","santa-fe","cr-v","rav4"]
f= open("car_resale.csv","w+")
f.write("car,resale score out of 100\n")
for i in range(4):
    url='https://www.jdpower.com/cars/2019/'+make[i]+'/'+model[i]
    rw=make[i]+" " + model[i]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    flg=0
    blk=soup.find("div", {"class":"grid small-ratings"})
    b=blk.text.replace(" ","").replace("\n"," ")
    c=b.find("Resale")
    d=b[c+6:99+5].replace(" ","")
    rw=rw+","+d
    f.write(rw+"\n")
f.close()

##########################################
# Maintenance score
##########################################
import requests
from bs4 import BeautifulSoup
make = ["ford","hyundai","honda","toyota"]
model = ["escape","santa+fe","cr-v","rav4"]
f=open("car_maintenance.csv","w+")
f.write("car,yearly maintenance cost")
for i in range(4):
    url='https://repairpal.com/'+make[i]+'/'+model[i]
    rw=make[i]+" " + model[i]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.findAll("div", {"class": "prh h2"}) :
        rw=rw+","+link.text
        f.write(rw+"\n")
f.close()

########################################
#insurance rate
########################################
import requests
make = ["ford","hyundai","honda","toyota"]
model = ["escape","santa-fe","cr-v","rav4"]
f=open("car_insur.csv","w+")
f.write("car,yearly insurance cost\n")
for i in range(4):
    url='https://www.thezebra.com/auto-insurance/vehicles/'+make[i]+'/'+model[i]
    rw=make[i]+" " + model[i]
    response = requests.get(url)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.findAll("div", {"class": "infotile-item"}) :
        if (link.text.find("Average Cost to Insure Per Year") != -1):
            rw=rw+","+(link.text[link.text.find("$")+1:]).replace(",","")
            f.write(rw+"\n")
            break
f.close()

##################################################
#creates combined file with weights added
##################################################
import pandas as pd
df1=pd.read_csv("car_psf.csv")
df2=pd.read_csv("car_resale.csv")
df3=pd.read_csv("car_maintenance.csv")
df4=pd.read_csv("car_insur.csv")
#merge/join files to get columns added vertically
df12 = pd.merge(df1,
                 df2,
                 on='car', 
                 how='inner')
df34 =  pd.merge(df3,
                 df4,
                 on='car', 
                 how='inner')
result =  pd.merge(df12,
                 df34,
                 on='car', 
                 how='inner')
#function to convert $amount to int
def money_to_int(money_str):
    return int(money_str.replace("$","").replace(",",""))
#applying function and calculation to get weighted score
result['PriceScore'] = result[' price'].apply(money_to_int)*10/25750
result['MaintenanceScore'] = result['yearly maintenance cost'].apply(money_to_int)*10/569
result['ResaleScore'] = result['resale score out of 100']/10
result['InsuranceScore'] = result['yearly insurance cost']*10/1369
result['CompanyWeights'] = (result[' safety rating']*10 + result['PriceScore']*7 + result['MaintenanceScore']*5)/30
result['MyWeights'] = (result[' fuel economy']*4 + result['InsuranceScore']*3 + result['ResaleScore']*3)/30
result['CombinedWeights'] = result['CompanyWeights'] + result['MyWeights']
#writing file to csv
result.to_csv('AnalysisFile.csv')
#creating company criteria(criteria 1) file
Criteria1 = result[['car', ' price', ' safety rating', ' fuel economy',
       'resale score out of 100', 'yearly maintenance cost',
       'yearly insurance cost', 'PriceScore', 'MaintenanceScore',
       'ResaleScore', 'InsuranceScore', 'CompanyWeights']]
Criteria1.to_csv('Criteria1.csv')
#creating my criteria (criteria 2) file
Criteria2 = result[['car', ' price', ' safety rating', ' fuel economy',
       'resale score out of 100', 'yearly maintenance cost',
       'yearly insurance cost', 'PriceScore', 'MaintenanceScore',
       'ResaleScore', 'InsuranceScore', 'MyWeights']]
Criteria2.to_csv('Criteria2.csv')
