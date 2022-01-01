from bs4 import BeautifulSoup
import requests
import json
import sys

from pyvis.network import Network

url = ["https://www.youtube.com/watch?v=N4PSLV3EpH4"]
profondeur = 10
nombreRecomendation = 2
nom_fichier_data = "data.csv"
#permet le calcul de l'evolution
def taille_reponse(star,prof,reco):
  recomendation = star
  reponse = 0
  for i in range(prof):
    a = recomendation * reco
    reponse += a
    recomendation = a
  return reponse
toto_reco = taille_reponse(len(url),profondeur,nombreRecomendation)
print("il y a " + str(toto_reco) + " video a scraper")
#array contenant toute les doner d scrapping
data_reponse = []
url_deja_scraper = []

def fichierData(data):
    global nom_fichier_data
    
    id_source = str(data["id_source"])
    name_source = data["name_source"]
    try:
      category_source = data["category_source"]
    except:
      category_source = "#FFFFFF"
    url_source = data["url_source"]

    try:
      id_target = data["id_target"]
      name_target = data["name_target"]
      url_target = data["url_target"]
    except:
      id_target = "noTarget"
      name_target = "noName"
      url_target = "noUrl"
    value_node = 1

    with open(nom_fichier_data, "a") as file:
      file.write(str(f"{id_source},{name_source},{category_source},{url_source},{id_target},{name_target},{url_target},{value_node}".encode(sys.stdout.encoding, errors='replace'))[2:-1].replace('\\xe2\\x80\\x93'," ")+"\n")


def definir_category(liste_keyword):
  reponse = ""
  if 'Music' == liste_keyword:
    reponse = "#f78080"
  
  elif "Film & Animation" == liste_keyword:
    reponse = "#f7cf80"
  
  elif "Pets & Animals" == liste_keyword:
    reponse = "#d8f780"
  
  elif "Sports" == liste_keyword:
    reponse = "#80f5f7"
     
  elif "Travel & Events" == liste_keyword:
    reponse = "#80a8f7"
  
  elif "Gaming" == liste_keyword:
    reponse = "#a880f7"
  
  elif "People & Blogs" == liste_keyword:
    reponse = "#e780f7"
   
  elif "Comedy" == liste_keyword:
    reponse = "#f780c8"
      
  elif "Entertainment" == liste_keyword:
    reponse = "#f60000"
  
  elif "News & Politics" == liste_keyword:
    reponse = "#eff600"
  
  elif "Science & Technology" == liste_keyword:
    reponse = "#8af600"
  
  elif "Autos & Vehicles" == liste_keyword:
    reponse = "#00f60f"
  
  elif "Nonprofits & Activism" == liste_keyword:
    reponse = "#00f6ba"
  
  elif "Education" == liste_keyword:
    reponse = "#007bf6"
  
  elif "Howto & Style" == liste_keyword:
    reponse = "#c900f6"
      
  if reponse == "":
    return "#c4c4c4"
  else:
    return reponse
    

def rechercheProduit(url):
  response = requests.get(url)
  if response.ok:
    soup = BeautifulSoup(response.content, "html.parser")
    scrip= soup.findAll("script")
    #traitement video actuelle
    videoActuelle = str(scrip[19].text)
    reponseActuelle = json.loads(videoActuelle[30:-1])
    video_actuelle_titre = reponseActuelle["videoDetails"]["title"]
    video_actuelle_id = reponseActuelle["videoDetails"]["videoId"]
    video_actuelle_category = reponseActuelle["microformat"]["playerMicroformatRenderer"]["category"]
    #traitement video sugestion
    miseEnForme = str(scrip[40].text)
    reponse = json.loads(miseEnForme[19:len(miseEnForme)-1])
    return [reponse['contents']['twoColumnWatchNextResults']["secondaryResults"]["secondaryResults"]["results"],video_actuelle_titre, video_actuelle_id, video_actuelle_category]

  else:
    return "False"

def mise_en_forme_data(url,nb_recomendation):
  url_a_scaner = []
  data = rechercheProduit(url)
  if data == "False":
    return url_a_scaner

  name_video_actualy = str(data[1])
  id_video_actualy = str(data[2])
  category_video_actualy = data[3]
  info_sugest = data[0]

  i = 0
  erreur = 0

  while i < nb_recomendation + erreur:
    i += 1
    try: #enregistrement des datas
      name_sugest = str(info_sugest[i]["compactVideoRenderer"]["accessibility"]["accessibilityData"]["label"])
      id_sugest = str(info_sugest[i]["compactVideoRenderer"]["navigationEndpoint"]["watchEndpoint"]["videoId"])
      url_sugest = "https://www.youtube.com" + str(info_sugest[i]["compactVideoRenderer"]["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"])
      url_a_scaner.append(url_sugest)
      global data_reponse
      global toto_reco
      fichierData({
                           "name_source": str(name_video_actualy),
                           "id_source": str(id_video_actualy),
                           "url_source": str(url),
                           "category_source": str(category_video_actualy),
                           "name_target": str(name_sugest),
                           "id_target": str(id_sugest),
                           "url_target": str(url_sugest)
      })

      data_reponse.append([
                           name_video_actualy,
                           id_video_actualy,
                           url,
                           category_video_actualy,
                           name_sugest,
                           id_sugest,
                           url_sugest
      ])
      print(str(round((len(data_reponse)/toto_reco)*100)) + "% " + str(len(data_reponse)) + "/"+str(toto_reco))
      #print("id actualy : " + id_video_actualy + "\n" + "name actualy : " + name_video_actualy + "\n" + "name sugest : " + name_sugest + "\n" + "id sugest : " + id_sugest + "\n" + "url sugest: " + url_sugest + "\n\n")
    except:
      erreur += 1
    if(erreur > 3):
      break
  return url_a_scaner
    
def scan_adresse(url,prof,nb_reco):
  global data_reponse
  global url_deja_scraper
  url_a_scanner = [url]

  for i in range(prof):
    url_a_scanner.append([])
    for u in url_a_scanner[i]:
      url_deja_scraper.append(u)
      [url_a_scanner[i+1].append(n) for n in mise_en_forme_data(u,nb_reco)]

  reste_a_craper = len(url_a_scanner[len(url_a_scanner)-1])
  count =0
  print("il reste encore " + str(reste_a_craper) + " video a scrapper" )
  for u in url_a_scanner[len(url_a_scanner)-1]:
    if u in url_deja_scraper:
      count += 1
      continue
    url_deja_scraper.append(u)
    response = requests.get(u)
    if response.ok:
      soup = BeautifulSoup(response.content, "html.parser")
      scrip= soup.findAll("script")
      #traitement video actuelle
      videoActuelle = str(scrip[19].text)
      reponseActuelle = json.loads(videoActuelle[30:len(videoActuelle)-1])
      
      name_video_actualy = str(reponseActuelle["videoDetails"]["title"])
      id_video_actualy = str(reponseActuelle["videoDetails"]["videoId"])
      category_video_actualy = reponseActuelle["microformat"]["playerMicroformatRenderer"]["category"]

      fichierData({
                           "name_source": str(name_video_actualy),
                           "id_source": str(id_video_actualy),
                           "url_source": str(u),
                           "category_source": str(category_video_actualy)
      })
      data_reponse.append([name_video_actualy,id_video_actualy,u,category_video_actualy])
    print(str(round((count/reste_a_craper)*100))+"% " + str(count) + "/" + str(reste_a_craper) )
    count += 1

#lancement du scan et ouverture du fichier a ecrire
with open(nom_fichier_data, "w") as file:
    file.write("id_source,name_source,category_source,url_source,id_target,name_target,url_target,value_node\n")

scan_adresse(url,profondeur,nombreRecomendation)




net = Network(notebook=True, height="100%", width="100%", bgcolor='#222222', font_color='white')
net.barnes_hut()


for i in data_reponse:

  net.add_node(i[1], label=i[0][0:10], title='<p>Video : <a style="text-decoration:none;color:black" href ="'+i[2]+'">'+i[0][0:20]+'</a><br><br> Categorie :' + str(i[3]) + "</p>",value=1, color=definir_category(i[3]))
  #net.add_node(i[5], label=i[4][0:10], title='<a style="text-decoration:none;color:black" href ="'+i[6]+'">'+i[4][0:20]+'</a>',value=1)

for i in data_reponse:
    if len(i)>4:
      net.add_edge(i[1], i[5], value=1, color= 'black')

net.show('graphique_network.html')
