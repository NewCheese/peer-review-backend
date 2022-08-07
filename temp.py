samp = "7/11/2022"
import datetime 

d = datetime.datetime.strptime(samp, "%m/%d/%Y").date()
print(d)