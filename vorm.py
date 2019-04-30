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

csv_files = glob.glob("vorm/*.csv")
start = 5
response = []
ligne = 0
datas = {}
ids = []
kinds = []
# dubbeletop
# vorm
# zware zijtak
# algemene takkigheid
# takhoek
# wortelopslag
headers = ["dt","vorm","ztak","algtak","takhoek","opslag"]
for file in csv_files:
  with open(file, newline='\n') as csvfile:
    response = []
    ligne = 0
    kind = file.replace("vorm/","")
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
            if("rand" not in row[n] and "rij" not in row[n] and '?' not in row[n]):
              weeks = str(row[n+1]).split("-")
              if len(weeks) != 6:
                print(row[n+1])
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
myFile = open('output-vorm-data.csv', 'w')
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
  totaldt = np.nansum(data,axis=0)
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
    calc["sum-"+kinds[i]] =totaldt[i]
    calc["length-"+kinds[i]] =lengthvalues[i]
  calcByCategory[category] = calc

# print(calcByCategory)
header = ["category","type","mean","median","percentile 25",
"percentile 75","ecart type","variance","min","max","sum" ,"length"]
output = [header]
for category in categories:
  d = calcByCategory[category]
  tmp = []
  for kind in kinds:
    tmp = [category,kind,d["mean-"+kind],d["median-"+kind],
    d["percentile25-"+kind],d["percentile75-"+kind],
    d['sd-'+kind],d["var-"+kind],d["min-"+kind],d["max-"+kind],
    d["sum-"+kind],d["length-"+kind]]
    output.append(tmp)

myFile = open('processed-data-vorm.csv', 'w')
with myFile:
  writer = csv.writer(myFile)
  writer.writerows(output)


print("-------- creation des graphiques --------")

print("Graphique #1 ")
objects = categories
y_pos = np.arange(len(objects))
graph_data_sum = []
graph_data_mean = []
errors_bars_1 = []
errors_bars_2 = []
for category in categories:
  d = calcByCategory[category]
  graph_data_sum.append(np.array(d["sum-vormscore.csvdt"],dtype=np.float32)/np.array(d["length-vormscore.csvdt"],dtype=np.float32)*100.0)

plt.bar(y_pos, graph_data_sum, align='center', alpha=0.5)
# plt.errorbar(y_pos, graph_data,yerr=errors_bars,fmt='o',capsize=5)

plt.xticks(y_pos, objects)
plt.ylabel('Percentage bomen met dubbele top')
plt.title('Percentage bomen met dubbele top per herkomst')
plt.show()


print("Graphique #2")
objects = categories
y_pos = np.arange(len(objects))
graph_data = []
errors_bars = []
for category in categories:
  d = calcByCategory[category]
  graph_data.append(d["mean-vormscore.csvvorm"])
  # errors_bars.append(d["sd-vormscore.csvvorm"])
plt.bar(y_pos, graph_data, align='center', alpha=0.5)
# plt.errorbar(y_pos, graph_data,yerr=errors_bars,fmt='o',capsize=5)

plt.xticks(y_pos, objects)
plt.ylabel('Gemiddelde vormscore')
plt.title('Gemiddelde vormscore per herkomst')
plt.show()

print("Graphique #3")
objects = categories
y_pos = np.arange(len(objects))
graph_data = []
errors_bars = []
for category in categories:
  d = calcByCategory[category]
  graph_data.append(np.array(d["sum-vormscore.csvztak"],dtype=np.float32)/np.array(d["length-vormscore.csvztak"],dtype=np.float32)*100.0)

plt.bar(y_pos, graph_data, align='center', alpha=0.5)

plt.xticks(y_pos, objects)
plt.ylabel('Percentage aanwezigheid zware zijtak dichtbij de grond')
plt.title('Percentage aanwezigheid zware zijtak dichtbij de grond per herkomst')
plt.show()

print("Graphique #4 ")

objects = categories
y_pos = np.arange(len(objects))
y_data_1 = []
y_data_2 = []
y_data_3 = []
for i in range(1,len(categories)+1):
    cat = categories[i-1]
    d = dataByCategory[cat]
    data_x_position = kinds.index("vormscore.csvalgtak")
    data = np.array(d, dtype=np.float)
    data = data[:, data_x_position]
    y_data_1.append((np.count_nonzero(data == 1)/len(data))*100.0)
    y_data_2.append((np.count_nonzero(data == 2)/len(data))*100.0)
    y_data_3.append((np.count_nonzero(data == 3)/len(data))*100.0)
fig, ax = plt.subplots()
bar_width = 0.17
opacity = 0.8
rects1 = plt.bar(y_pos, y_data_1, bar_width,
alpha=opacity,
color='r',
label='weinig')
rects2 = plt.bar(y_pos + bar_width, y_data_2, bar_width,
alpha=opacity,
color='g',
label='gemiddeld')
rects3 = plt.bar(y_pos + 2*bar_width, y_data_3, bar_width,
alpha=opacity,
color='b',
label='veel')

plt.xlabel('herkomst')
plt.ylabel('Proportie bomen met weinig - gemiddeld - veel takken')
plt.title('Proportie bomen met weinig - gemiddeld - veel takken per herkomst ')
plt.xticks(y_pos + 2*bar_width, objects)
plt.legend()

plt.tight_layout()
plt.show()

print("Graphique #5")
objects = categories
y_pos = np.arange(len(objects))
y_data_1 = []
y_data_2 = []
y_data_3 = []
for i in range(1,len(categories)+1):
    cat = categories[i-1]
    d = dataByCategory[cat]
    data_x_position = kinds.index("vormscore.csvtakhoek")
    data = np.array(d, dtype=np.float)
    data = data[:, data_x_position]
    y_data_1.append((np.count_nonzero(data == 1)/len(data))*100.0)
    y_data_2.append((np.count_nonzero(data == 2)/len(data))*100.0)
    y_data_3.append((np.count_nonzero(data == 3)/len(data))*100.0)
fig, ax = plt.subplots()
bar_width = 0.17
opacity = 0.8
rects1 = plt.bar(y_pos, y_data_1, bar_width,
alpha=opacity,
color='r',
label='Horizontaal')
rects2 = plt.bar(y_pos + bar_width, y_data_2, bar_width,
alpha=opacity,
color='g',
label='+/- 45°')
rects3 = plt.bar(y_pos + 2*bar_width, y_data_3, bar_width,
alpha=opacity,
color='b',
label='vrij vertikaal')

plt.xlabel('herkomst')
plt.ylabel('Proportie bomen met Horizontale - 45° - vrij vertikale takken')
plt.title('Proportie bomen met  Horizontale - 45° - vrij vertikale takken per herkomst ')
plt.xticks(y_pos + 2*bar_width, objects)
plt.legend()

plt.tight_layout()
plt.show()

print("Graphique #6")
objects = categories
y_pos = np.arange(len(objects))
y_data_1 = []
y_data_2 = []
y_data_3 = []
for i in range(1,len(categories)+1):
    cat = categories[i-1]
    d = dataByCategory[cat]
    data_x_position = kinds.index("vormscore.csvopslag")
    data = np.array(d, dtype=np.float)
    data = data[:, data_x_position]
    y_data_1.append((np.count_nonzero(data == 1)/len(data))*100.0)
    y_data_2.append((np.count_nonzero(data == 2)/len(data))*100.0)
    y_data_3.append((np.count_nonzero(data == 3)/len(data))*100.0)
fig, ax = plt.subplots()
bar_width = 0.17
opacity = 0.8
rects1 = plt.bar(y_pos, y_data_1, bar_width,
alpha=opacity,
color='r',
label='Veel wortelopslag')
rects2 = plt.bar(y_pos + bar_width, y_data_2, bar_width,
alpha=opacity,
color='g',
label='Een beetje wortelopslag')
rects3 = plt.bar(y_pos + 2*bar_width, y_data_3, bar_width,
alpha=opacity,
color='b',
label='Geen wortelopslag')

plt.xlabel('herkomst')
plt.ylabel('Proportie bomen met veel - een beetje - geen wortelopslag')
plt.title('Proportie bomen met veel - een beeje - geen wortelopslagper herkomst ')
plt.xticks(y_pos + 2*bar_width, objects)
plt.legend()

plt.tight_layout()
plt.show()


