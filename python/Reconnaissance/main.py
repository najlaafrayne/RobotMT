import ReconnaissanceV2 as RV2
import serial
from time import sleep

(category_index,image_tensor,detection_boxes,detection_scores,detection_classes,num_detections,sess)=RV2.load_model()

L=RV2.Detection(category_index,image_tensor,detection_boxes,detection_scores,detection_classes,num_detections,sess)



#Configuration du port série :
S = serial.Serial("/dev/ttyS0",9600)


for j in range (len(L)):
	if L[j][0]=='laptop':
		data='VtsM 50 50'
		S.write(data.encode('ascii'))
		receive=S.readline(len(data1))
		print(receive.decode("utf-8"))
		sleep(1)
		data='Stop'
		S.write(data.encode('ascii'))
		receive=S.readline(len(data))
		print(receive.decode("utf-8"))


S.close()
