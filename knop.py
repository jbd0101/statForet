import glob,csv,re
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import polyfit
plt.rcParams.update({'font.size': 22})

# Get current size
fig_size = plt.rcParams["figure.figsize"]

# Prints: [8.0, 6.0]

# Set figure width to 12 and height to 9
fig_size[0] = 12
fig_size[1] = 9
plt.rcParams["figure.figsize"] = fig_size

csv_files = glob.glob("knop/*.csv")
start = 5
response = []
ligne = 0
datas = {}
ids = []
kinds = []
headers = ["S1","S2","S3","S4"]
for file in csv_files:
  with open(file, newline='\n') as csvfile:
    response = []
    ligne = 0
    kind = file.replace("knop/","")
    for h in headers:
      kinds.append(kind+h)

    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
      ligne +=1
      for n in range(start,len(row),2):
        if(len(row[n])>0 and len(row[n+1])>0):
          match = re.search(r'^[A-Za-z\-]',row[n+1])
          if match:
            # print("Donne texte detecte ")
            continue
          else:
            if("rand" not in row[n] and "rij" != row[n] and '?' not in row[n]):
              weeks = list(str(row[n+1]))
              for w in range(len(weeks)):
                subkind = str(kind)+headers[w]
                week = weeks[w]
                id = (str(ligne)+"-"+str(n)+"-"+str(row[n])).upper()
                try:
                  data = float(week.replace(",","."))
                except ValueError:
                  # print("Erreur avec la donnee "+row[n+1])

                  data = week.replace(",",".")
                  data = re.sub(r'[a-zA-Z()]*',"",data)
                  data = float(data)
                # response.append([id,ligne,n,row[n],data])
                if id not in datas:
                  ids.append(id)
                  datas[id] = {}
                  datas[id]["datas"] = {subkind: data}
                  datas[id]["category"] = row[n].upper()
                  datas[id]["cols"] = [subkind]
                else:
                  datas[id]["datas"][subkind] = (data)
                  datas[id]["cols"].append(subkind)
#   myFile = open('output/inline-'+file.replace("data/",""), 'w')
#   with myFile:
#     writer = csv.writer(myFile)
#     writer.writerows(response)
# print(datas)
header = ["id","category"]
header.extend(kinds)
output=[header]
dataByCategory = {}
categories = []
for id in ids:
  tmp = [id,datas[id]["category"]]
  cat = datas[id]["category"]
  if cat not in dataByCategory:
    dataByCategory[cat]=[]
    categories.append(cat)
  temporary_datas =[]
  for kind in kinds:
    if(kind not in datas[id]["datas"]):
      tmp.append('')
      temporary_datas.append(np.nan)
    else:
      tmp.append(datas[id]['datas'][kind])
      temporary_datas.append(datas[id]['datas'][kind])
  dataByCategory[cat].append(temporary_datas)
  output.append(tmp)
myFile = open('output-knops-data.csv', 'w')
with myFile:
  writer = csv.writer(myFile)
  writer.writerows(output)


print("-------- Analyse par Cateorie-----------")
print(kinds)
#je veux la taille moyenne, mediane, perecentile 70, percentile 30
calcByCategory = {}
for category in categories:
  # print(dataByCategory[category])
  calc = {}
  data = np.array(dataByCategory[category], dtype=np.float)
  meanvalues = np.nanmean(data,axis=0)
  medianvalues = np.nanmedian(data,axis=0)
  sdvalues = np.nanstd(data, axis=0)
  varvalues = np.nanvar(data, axis=0)
  minvalues = np.nanmin(data, axis=0)
  maxvalues = np.nanmax(data, axis=0)
  percentile25values=np.nanpercentile(data, 25,axis=0)
  percentile75values=np.nanpercentile(data, 75,axis=0)
  lengthvalues = np.count_nonzero(~np.isnan(data),axis=0)
  for i  in range(len(kinds)):
    calc["mean-"+kinds[i]] =meanvalues[i]
    calc["median-"+kinds[i]] =medianvalues[i]
    calc["sd-"+kinds[i]] =sdvalues[i]
    calc["var-"+kinds[i]] =varvalues[i]
    calc["min-"+kinds[i]] =minvalues[i]
    calc["max-"+kinds[i]] =maxvalues[i]
    calc["percentile25-"+kinds[i]] =percentile25values[i]
    calc["percentile75-"+kinds[i]] =percentile75values[i]
    calc["length-"+kinds[i]] =lengthvalues[i]
  calcByCategory[category] = calc

# print(calcByCategory)
header = ["category","type","mean","median","percentile 25",
"percentile 75","ecart type","variance","min","max","length"]
output = [header]
for category in categories:
  d = calcByCategory[category]
  tmp = []
  for kind in kinds:
    tmp = [category,kind,d["mean-"+kind],d["median-"+kind],
    d["percentile25-"+kind],d["percentile75-"+kind],
    d['sd-'+kind],d["var-"+kind],d["min-"+kind],d["max-"+kind],d["length-"+kind]]
    output.append(tmp)

myFile = open('processed-data-knop.csv', 'w')
with myFile:
  writer = csv.writer(myFile)
  writer.writerows(output)

print("Creation du graphique")
x_data = ["week 1","week 2","week 3","week 4"]
y_datas = []
# print(categories)

for c in range(len(categories)):
  d= calcByCategory[categories[c]]
  y_datas.append([d["mean-Knopuitloop.csvS1"],d["mean-Knopuitloop.csvS2"],d["mean-Knopuitloop.csvS3"],d["mean-Knopuitloop.csvS4"]])

# fig, ax = plt.subplots()
plt.figure()
for c in range(len(categories)):
  print(y_datas[c])
  plt.plot(x_data,y_datas[c],'o-',label=categories[c])
plt.xlabel("week")
plt.title("Evolutie knopuitloop")
plt.ylabel("knoppels")
legend = plt.legend(loc='upper center', shadow=True, fontsize='x-large')

# Put a nicer background color on the legend.
# legend.get_frame().set_facecolor('C0')

plt.show()
