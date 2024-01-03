import cv2
import pandas as pd
import re

# ===================================================================================================================

# Preprocess

# apply clahe and bilateral filter into image
def clahe_process (image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #grayscale

    #apply clahe
    clahe = cv2.createCLAHE(clipLimit = 2,tileGridSize=(8,8)) 
    final_img = clahe.apply(gray)
    
    blur = cv2.bilateralFilter(final_img,9,75,75) #bilateral filter

    img = cv2.cvtColor(blur, cv2.COLOR_BGR2RGB) #result

    return img

def crop_image (image):
    h, w, c = image.shape
    crop_img = image[int(0.25*h):h, 0:w]

    return crop_img

# ===================================================================================================================


# ===================================================================================================================

# post process paddle ocr to find plate
def plate_paddle(result,fr_digit,fr_alpha):
    
    boxes = [line[0] for line in result]
    text = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]

    x1, x2, y1, y2 = [], [], [], []
    for i in range(0,len(text)):
        df_box = pd.DataFrame(boxes[i],columns=['x','y'])
        xmin, xmax, ymin, ymax = int(df_box['x'].min()), int(df_box['x'].max()), int(df_box['y'].min()), int(df_box['y'].max())
        x1.append(xmin)
        x2.append(xmax)
        y1.append(ymin)
        y2.append(ymax)

    df_result = pd.DataFrame(x1, columns = ['x1'])
    df_result['y1'] = y1
    df_result['x2'] = x2
    df_result['y2'] = y2
    df_result['cx'] = ((df_result['x1']+df_result['x2'])/2).astype(int)
    df_result['cy'] = ((df_result['y1']+df_result['y2'])/2).astype(int)
    df_result['text'] = text
    df_result['text'] = df_result['text'].str.replace('[^0-9a-zA-Z]', '').str.upper()
    df_result['scores'] = scores
    contalpha, contdigit = [], []
    for text in df_result['text'].values.tolist():
        contalpha.append(any(t.isalpha() for t in text))
        contdigit.append(any(t.isdigit() for t in text))
    alphadigit = [True if a == True and d == True else False for a,d in zip(contalpha, contdigit)]
    df_result['text_length'] = df_result['text'].str.len()
    df_result['contalpha'] = contalpha
    df_result['contdigit'] = contdigit
    df_result['alphadigit'] = alphadigit
    
    # =======================================================================================================
    #Choosing plate value
    sc = []
    for i in range(0,df_result.shape[0]):
        s = 0
        if df_result.loc[i,'text_length'] >= 4 and df_result.loc[i,'text_length'] <= 8:
            if df_result.loc[i,'text_length'] == 4:
                s = s + 1
            else:
                s = s + 2
        if alphadigit[i] == True:
            s = s + 1
        if 'CAMERA'in df_result.loc[i,'text'] or 'CAME'in df_result.loc[i,'text'] or 'CANERA'in df_result.loc[i,'text'] or 'MERA'in df_result.loc[i,'text'] or 'CANE'in df_result.loc[i,'text']:
            s = -1
        sc.append(s)
    df_result['sc'] = sc
    df_result = df_result[df_result['sc']==df_result['sc'].max()]
    df_result = df_result.sort_values('cy', ascending=True).reset_index(drop=True)
    text = re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + " ", df_result.loc[0,'text'])

    # =======================================================================================================
    #Text Optimaztion
    textlist = text.split()
    if df_result.loc[0,'sc'] != -1 and len(textlist) > 1:
        for i in range(0,len(textlist)):
            tex = textlist[i]
            #numeric to alphabet
            if tex.isdigit():
                if i == 0: #numeric first
                    if len(tex) > 4:
                        alpha = tex[0:len(tex)-4]
                        alphanew =''
                        for a in alpha:
                            try:
                                alphanew = alphanew + fr_alpha[fr_digit.index(a)] 
                            except:
                                alphanew = alphanew + a
                        digit = tex[len(tex)-4:]
                        tex = alphanew + digit
                if i == 1 and len(tex) > 4: #numeric last 
                    digit = tex[0:4]
                    alpha = tex[4:]
                    alphanew =''
                    for a in alpha:
                        try:
                            alphanew = alphanew + fr_alpha[fr_digit.index(a)]
                        except:
                            alphanew = alphanew + a
                    tex = digit + alphanew
                if i > 1:
                    alpha = tex
                    alphanew =''
                    for a in alpha:
                        try:
                            alphanew = alphanew + fr_alpha[fr_digit.index(a)] 
                        except:
                            alphanew = alphanew + a
                    tex = alphanew
                
                textlist[i] = tex

        text = ''
        for t in textlist:
            text = text + t
        text = re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + " ", text)
        text = text.strip()
    
    # =======================================================================================================

    if df_result.loc[0,'sc'] == -1:
        plate_result = {'plate': 'no text detected',
                        'scores': 0,
                        'position': []
                    }
    else:
        plate_result = {'plate': text,
                    'scores': float(round(df_result.loc[0,'scores'],2)),
                    'position': str(df_result.loc[0,['x1','y1','x2','y2']].values.tolist())
                }
    
    return plate_result

# ===================================================================================================================
