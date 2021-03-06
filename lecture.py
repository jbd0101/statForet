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

csv_files = glob.glob("data/*.csv")
start = 5
response = []
ligne = 0
datas = {}
ids = []
kinds = []
for file in csv_files:
  with open(file, newline='\n') as csvfile:
    response = []
    ligne = 0
    kind = file.replace("data/","")
    kinds.append(kind)
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
              id = (str(ligne)+"-"+str(n)+"-"+str(row[n])).upper()
              try:
                data = float(row[n+1].replace(",","."))
              except ValueError:
                # print("Erreur avec la donnee "+row[n+1])

                data = row[n+1].replace(",",".")
                data = re.sub(r'[a-zA-Z()]*',"",data)
                data = float(data)
              # response.append([id,ligne,n,row[n],data])
              if id not in datas:
                ids.append(id)
                datas[id] = {}
                datas[id]["datas"] = {kind: data}
                datas[id]["category"] = row[n].upper()
                datas[id]["cols"] = [kind]
              else:
                datas[id]["datas"][kind] = (data)
                datas[id]["cols"].append(kind)
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
myFile = open('output-data.csv', 'w')
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

myFile = open('processed-data.csv', 'w')
with myFile:
  writer = csv.writer(myFile)
  writer.writerows(output)


print("-------- creation des graphiques --------")

# print("Graphique #1 : Taille sur un histogramme seul / categorie")
# objects = categories
# y_pos = np.arange(len(objects))
# graph_data = []
# errors_bars = []
# for category in categories:
#   d = calcByCategory[category]
#   graph_data.append(d["mean-tailles.csv"])
#   errors_bars.append(d["sd-tailles.csv"])
# plt.bar(y_pos, graph_data, align='center', alpha=0.5,color='g')
# plt.errorbar(y_pos, graph_data,yerr=errors_bars,fmt='o',capsize=5)

# plt.xticks(y_pos, objects)
# plt.ylabel('Gemiddelde hoogte (cm)')
# plt.title('Gemiddelde hoogte per herkomst')
# plt.savefig('charts/Taille_bar.png')




# print("Graphique #2 : dikte1 et dikte2 / categorie")
# objects = categories
# y_pos = np.arange(len(objects))
# graph_data_dikte1 = []
# graph_data_dikte10 = []
# errors_bars_1 = []
# errors_bars_2 = []
# for category in categories:
#   d = calcByCategory[category]
#   graph_data_dikte10.append(d["mean-Dikte10cm.csv"])
#   graph_data_dikte1.append(d["mean-Dikte1m.csv"])
#   errors_bars_1.append(d["sd-Dikte10cm.csv"])
#   errors_bars_2.append(d["sd-Dikte1m.csv"])


# fig, ax = plt.subplots()
# bar_width = 0.35
# opacity = 0.8
# rects1 = plt.bar(y_pos, graph_data_dikte10, bar_width,
# alpha=opacity,
# color='b',
# label='Omtrek op 10cm')
# rects2 = plt.bar(y_pos + bar_width, graph_data_dikte1, bar_width,
# alpha=opacity,
# color='g',
# label='Omtrek op 1m')
# plt.errorbar(y_pos, graph_data_dikte10,yerr=errors_bars_1,fmt='o',capsize=5)
# plt.errorbar(y_pos+bar_width, graph_data_dikte1,yerr=errors_bars_2,fmt='o',capsize=5)

# plt.xlabel('herkomst')
# plt.ylabel('hoogte ( cm ) ')
# plt.title('Gemiddelde omtrek per herkomst ')
# plt.xticks(y_pos + bar_width, objects)
# plt.legend()

# plt.tight_layout()
# plt.savefig('charts/dikte.png')


print("graph #3 , Par arbre , par catégorie, sa taille en fonction du perimetre à 10cm")

fig=plt.figure(figsize=(20, 20))
columns = 3
rows = 4
h=5
w=5
residus = []
residu_cat = []
for i in range(1,len(categories)+1):
    x_data = []
    y_data= []
    cat = categories[i-1]
    d = dataByCategory[cat]
    data_x_position = kinds.index("Dikte1m.csv")
    data_y_position = kinds.index("tailles.csv")
    data = np.array(d, dtype=np.float)
    data_x_y = data[:, [data_x_position,data_y_position]]
    for point in data_x_y:
      if( not np.isnan(point[0]) and not np.isnan(point[1])):
        x_data.append(point[0])
        y_data.append(point[1])
    fig.add_subplot(rows, columns, i)
    plt.xlabel("Omtrek van  "+cat+" in cm")
    plt.ylabel("Hoogte in cm")
    plt.yscale('linear')
    plt.title("Hoogte in functie van de omtrek |  "+cat)
    b, m = polyfit(x_data, y_data, 1)
    residu = np.sum((np.polyval(np.polyfit(x_data, y_data, 2), x_data) - y_data)**2)
    # error_rate = np.polyfit(x_data, y_data, 2), x_data) - y_data)**2)
    x_data = np.array(x_data,dtype=np.float32)
    valeur_theorique = (x_data*m+b)
    print(valeur_theorique)
    valeur_reels = (y_data)
    print(y_data)
    erreurs = (valeur_theorique -valeur_reels)/valeur_reels
    # print(erreur)
    # residus.append(residu)
    residus.append(np.nanmean(erreurs))
    residu_cat.append(cat)
    plt.plot(x_data, b + m * np.array(x_data,dtype=np.float), '-')
    plt.plot(x_data, y_data, 'ro')
    plt.xlim([0,14])
    plt.ylim([100,500])

    # plt.axis([0, 6, 0, 20])
    # plt.show()
plt.show()
list1,list2 = (list(t) for t in zip(*sorted(zip(residus, residu_cat))))
print(list1)
print(list2)
