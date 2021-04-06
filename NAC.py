import cv2
import os,sys, os.path
import numpy as np

#importes para emular precionamento de teclas
from pynput.keyboard import Key, Controller
import pynput
import time
import random

keys = [
    Key.right,                               # DOWN
    Key.left,                               # LEFT
]

#Inicializa o controle 
keyboard = Controller()

image_lower_hsv = np.array([0, 255, 0])  
image_upper_hsv = np.array([0, 255, 255])
posicao = []


def filtro_de_cor(img):
    """ retorna a imagem filtrada"""
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_gray 

def exibir_tela(img):
  """
  ->>> !!!! FECHE A JANELA COM A TECLA ESC !!!! <<<<-
  deve receber a imagem da camera e retornar uma imagems filtrada.
  """  
  image_lower_hsv = np.array([0, 255, 0])  
  image_upper_hsv = np.array([0, 255, 255])
  mask_hsv = cv2.inRange(img, image_lower_hsv, image_upper_hsv)
  contornos, _ = cv2.findContours(mask_hsv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
  mask_rgb = cv2.cvtColor(mask_hsv, cv2.COLOR_GRAY2RGB)
  cv2.drawContours(mask_rgb, contornos, -1, [0, 255, 0], 15);
  
  return mask_rgb,contornos
  
def desenhar_cruz(img, contorno):
  cnt=contorno
  M = cv2.moments(cnt)

  #desenhar a cruz
  num = 0
  size = 20
  color = (255,0,0)
  cX = 0
  cY = 0
  
  
  if M["m00"] != 0:
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
       
    cv2.line(img,(cX - size,cY),(cX + size,cY),color,5)
    cv2.line(img,(cX,cY - size),(cX, cY + size),color,5)
      
    font = cv2.FONT_HERSHEY_SIMPLEX
    origem = (20,50)
    text = cY , cX
    posicao.append([cX,cY])
    cv2.putText(img, str(text), origem, font,1,(255,255,0),2,cv2.LINE_AA)       
  else:
    # se não existe nada para segmentar
    cX, cY = 0, 0
    # Para escrever vamos definir uma fonte 
    texto = 'Não tem nada'
    font = cv2.FONT_HERSHEY_SIMPLEX
    origem = (0,50)
    cv2.putText(img, texto, origem, font,1,(255,255,0),2,cv2.LINE_AA)
    
  return cX,cY, img
  
def controle_teclado(cX, cX2): 
  if cX < cX2:
    print('Tecla: ', keys[0])
    keyboard.press(keys[0])
    time.sleep(0.09)
    keyboard.release(keys[0])
  elif cX > cX2: 
    print('Tecla: ', keys[1])
    keyboard.press(keys[1])
    time.sleep(0.09)
    keyboard.release(keys[1])

def detectar_circulos(img):

  img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
  edges = cv2.Canny(img_gray,50,150)
  circles=cv2.HoughCircles(img_gray,cv2.HOUGH_GRADIENT,dp=3,minDist=150,param1=120,param2=150,minRadius=50,maxRadius=150)

  bordas_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
  output = bordas_rgb

  # Draw circles
  if circles is not None:        
      circles = np.uint16(np.around(circles))
      for i in circles[0,:]:
          # desenha o contorno do circulo
          cv2.circle(output,(i[0],i[1]),i[2],(0,255,0),2)
          # desenha no centro do circulo
          cv2.circle(output,(i[0],i[1]),2,(0,0,255),3)
  return output

def tracar_linha(img,cX,cY,cX2,cY2):
  cv2.line(img, (cX,cY), (cX2,cY2), (255, 0, 0), 5)
  return img

cv2.namedWindow("preview")
# define a entrada de video para webcam
vc = cv2.VideoCapture(0)

#vc = cv2.VideoCapture("video.mp4") # para ler um video mp4 

#configura o tamanho da janela 
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 840)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 680)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
  cX = 0
  cY = 0
  cX2 = 0
  cY2 = 0  
  img = filtro_de_cor(frame) # passa o frame para a função imagem_da_webcam e recebe em img imagem tratada
  img = detectar_circulos(img)
  img,contorno = exibir_tela(img)

  if len(contorno) > 2:
   cX,cY,img = desenhar_cruz(img, contorno[2])
   cX2,cY2,img = desenhar_cruz(img, contorno[1])
   img = tracar_linha(img,cX,cY,cX2,cY2)
   
  
  #mask_rgb = desenha_cruz(contornos[0],mask_rgb,0,50,20,cor)
  cv2.imshow("preview", img)
  cv2.imshow("original", frame)
  rval, frame = vc.read()
  key = cv2.waitKey(20)
  if len(contorno) > 2:
    controle_teclado(cX, cX2) 
  if key == 27: # exit on ESC
    break

cv2.destroyWindow("preview")
vc.release()
