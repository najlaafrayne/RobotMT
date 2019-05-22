import ReconnaissanceV2 as RV2
import serial
import UART
import constantes
import ObjetReconnu
from time import sleep

NOMBRE_DE_PASSE = 10 #Nombre de consigne à envoyer

nomObjetASuivre = "laptop"
nomObjetAFuir = "sac"

(category_index,image_tensor,detection_boxes,detection_scores,detection_classes,num_detections,sess)=RV2.load_model()

#Configuration du port série :
portSerie = serial.Serial("/dev/ttyS0",baudrate)

for p in range(NOMBRE_DE_PASSE):

	#Acquisition des objets reconnues
	Liste_Objets_Reconnues=RV2.Detection(category_index,image_tensor,detection_boxes,detection_scores,detection_classes,num_detections,sess)
	#Liste_Objets_Reconnues est un tableau de liste formattées comme suit:
	#Liste_Objets_Reconnues[i] = (nom, probabilité, y_min, x_min, y_max, x_max)

	for i in range(len(Liste_Objets_Reconnues)): #on scan tous les objets reconnues
		if Liste_Objets_Reconnues[j][0] == nomObjetASuivre or Liste_Objets_Reconnues[j][0] == nomObjetAFuir :
			Objet_Tracke = ObjetReconnu( #On crée un objet à partir de la liste recupérée de tensorflow
				Liste_Objets_Reconnues[j][0],
				Liste_Objets_Reconnues[j][1],
				Liste_Objets_Reconnues[j][2],
				Liste_Objets_Reconnues[j][3],
				Liste_Objets_Reconnues[j][4],
				Liste_Objets_Reconnues[j][5],
				Liste_Objets_Reconnues[j][6]
				)
			alignement = Asserv_V2.aligner_robot(Objet_Tracke, portSerie)
			if alignement == 1: #Si le robot est correctement aligné, on corrige sa position
				if Objet_Tracke.nom == nomObjetASuivre :
					ordre = "suivre"
				else : #si ce n'est pas l'objet à suivre, c'est l'objet à suivre au vu d'un if precedent
					ordre = "fuir"
				position = Asserv_V2.positioner_robot(Objet_Tracke, ordre, portSerie)

portSerie.close()