import pandas as pd
import re
from google.cloud import vision

def vision_ocr(image_uri: str):
    # image_uri = 'gs://cloud-vision-codelab/otter_crossing.jpg'

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_uri

    response = client.text_detection(image=image)

    returnText = []

    for idx, text in enumerate(response.text_annotations):
        if (idx != 0  ):
            # print('=' * 30)
            # print(text.description)
            # print(text)
            vertices = ['(%s,%s)' % (v.x, v.y) for v in text.bounding_poly.vertices]
            # print('bounds:', ",".join(vertices))
            returnText.append({
                "text": text.description,
                "bounds": vertices,
                })

    # for text in response.text_annotations:
    #     print('=' * 30)
    #     print(text.description)
    #     vertices = ['(%s,%s)' % (v.x, v.y) for v in text.bounding_poly.vertices]
    #     print('bounds:', ",".join(vertices))

    return returnText

# Post Process
def vision_read_plate (data,width):
    if len(data) == 0:
        text_result = None

    else:
        
        df_result = dataframe(data) #put result into dataframe
        df_result = df_result[df_result['text']!=''].reset_index(drop=True)

        #separate number and alphabet
        list_text, list_x1, list_x2, list_x3, list_x4, list_y1, list_y2, list_y3, list_y4 = [], [], [], [], [], [], [], [], []
        for i in range(0, df_result.shape[0]):
            str = df_result.loc[i,'text']
            digit=re.findall(r'\d+',str)
            if len(digit)>0:
                list_text = list_text + [a for a in digit]
                for j in range(0,len(digit)):
                    list_x1.append(df_result.loc[i,'x1'])
                    list_x2.append(df_result.loc[i,'x2'])
                    list_x3.append(df_result.loc[i,'x3'])
                    list_x4.append(df_result.loc[i,'x4'])
                    list_y1.append(df_result.loc[i,'y1'])
                    list_y2.append(df_result.loc[i,'y2'])
                    list_y3.append(df_result.loc[i,'y3'])
                    list_y4.append(df_result.loc[i,'y4'])
            alphabet=re.findall(r'[a-zA-Z]+',str)
            if len(alphabet)>0:
                list_text = list_text + [b for b in alphabet]
                for j in range(0,len(alphabet)):
                    list_x1.append(df_result.loc[i,'x1'])
                    list_x2.append(df_result.loc[i,'x2'])
                    list_x3.append(df_result.loc[i,'x3'])
                    list_x4.append(df_result.loc[i,'x4'])
                    list_y1.append(df_result.loc[i,'y1'])
                    list_y2.append(df_result.loc[i,'y2'])
                    list_y3.append(df_result.loc[i,'y3'])
                    list_y4.append(df_result.loc[i,'y4'])
        
        df_result = pd.DataFrame()
        df_result['text'] = list_text
        df_result['x1'], df_result['x2'], df_result['x3'], df_result['x4'] = list_x1, list_x2, list_x3, list_x4
        df_result['y1'], df_result['y2'], df_result['y3'], df_result['y4'] = list_y1, list_y2, list_y3, list_y4

        x1 = [min(x) for x in df_result[['x1','x2','x3','x4']].values.tolist()]
        x2 = [max(x) for x in df_result[['x1','x2','x3','x4']].values.tolist()]
        y1 = [min(y) for y in df_result[['y1','y2','y3','y4']].values.tolist()]
        y2 = [max(y) for y in df_result[['y1','y2','y3','y4']].values.tolist()]
        df_result['x1'], df_result['x2'] = x1,x2
        df_result['y1'], df_result['y2'] = y1,y2
        df_result = df_result[['text','x1','x2','y1','y2']]

        #search & group boxes close to each other
        df = df_result.copy()
        k = 50
        x1 = [x-k if x-k > 0 else 0 for x in df['x1'].values.tolist()]
        x3 = [x+k if x+k < width else width for x in df['x2'].values.tolist()]
        df['x1'] = x1
        df['x2'] = x2
        df_box = grouped_box_loop(df[['y1', 'x1', 'y2', 'x2']].values.tolist()) #grouped box coordinate
        df_box = df_box.sort_values('y1',ascending=True).reset_index(drop=True) #grup pertama yang paling atas
        df_result = grouped_result(df_result,df_box) #grouping result

        # print(df_result)
        # print()

        # looping through result group
        value = []
        for i in range(0,df_result['group'].max()):
            df_group = df_result[df_result['group']==i+1].reset_index(drop=True)
            shape = df_group.shape[0]
            
            if df_group.empty:
                text_result = None
            else:
                df_group = df_group.sort_values('x1').reset_index(drop=True)
                if df_group.loc[0,'text'] == '8' or df_group.loc[0,'text'] == '3':
                    df_group.loc[0,'text'] = 'B'


                df_group['text_length'] = df_group['text'].str.len()
                df_group['is_alphabet'] = df_group['text'].str.isalpha()
                df_group['is_digit'] = df_group['text'].str.isdigit()
                count = 1

                #first code (area)
                try:
                    index = df_group.index[(df_group['text_length'] > 0) & (df_group['text_length'] <= 2) & (df_group['is_alphabet'] == True)][0] #max 2 character alphabet
                    df_group.loc[index,'order'] = count
                    count = count + 1
                except:
                    pass

                #number code
                try:
                    index = df_group.index[(df_group['text_length'] >= 1) & (df_group['is_digit'] == True)][0] #number more than 2 digit
                    df_group.loc[index,'order'] = count
                    count = count + 1
                except:
                    pass

                #last code
                try:
                    index = df_group.index[(df_group['text_length'] > 0) & (df_group['text_length'] <= 3) & (df_group['is_alphabet'] == True)][1] #max 3 character alphabet
                    df_group.loc[index,'order'] = count
                    count = count + 1
                except:
                    if count != 1:
                        df_group.loc[df_group.index[-1],'order'] = count
                        count = count + 1
                    else:
                        pass
                df_group = df_group.dropna()

                if 'order' in df_group:
                    # uniting result
                    df_group = df_group.sort_values('order').reset_index(drop=True)
                    val = [' '.join(df_group['text']), df_group.shape[0], shape]
                    value.append(val)
        
        if len(value)>0:
            df = pd.DataFrame(value,columns=['text','count', 'size_group'])
            try:
                df1 = df[(df['count']==3)].sort_values('size_group').reset_index(drop=True)
                text_result = df1.loc[0,'text'].upper()
            except:
                try:
                    df1 = df[(df['count']>=1) & (df['count']<=3)].sort_values('count',ascending = False).reset_index(drop=True)
                    text_result = df1.loc[0,'text'].upper()
                except:
                    text_result = None
        else:
            text_result = None
    
    return text_result


# put result into dataframe
def dataframe(data):
    #put result into dataframe
    # data = json.loads(r.text)['text']
    df = pd.json_normalize(data)
    df['text'] = df['text'].str.strip() #remove space right, left
    df['text'] = df['text'].str.replace('[^a-zA-Z0-9]', '', regex=True) #remove non alpha numeric

    #separate points
    df[['point1','point2','point3','point4']] = pd.DataFrame(df.bounds.tolist(), index= df.index)
    x1 = []
    y1 = []
    for text in df.point1.values.tolist():
        list_ = [int(s) for s in text.replace('(','').replace(')','').replace('[','').replace(']','').split(',')]
        x1.append(list_[0])
        y1.append(list_[1])
    x2 = []
    y2 = []
    for text in df.point2.values.tolist():
        list_ = [int(s) for s in text.replace('(','').replace(')','').replace('[','').replace(']','').split(',')]
        x2.append(list_[0])
        y2.append(list_[1])
    x3 = []
    y3 = []
    for text in df.point3.values.tolist():
        list_ = [int(s) for s in text.replace('(','').replace(')','').replace('[','').replace(']','').split(',')]
        x3.append(list_[0])
        y3.append(list_[1])
    x4 = []
    y4 = []
    for text in df.point4.values.tolist():
        list_ = [int(s) for s in text.replace('(','').replace(')','').replace('[','').replace(']','').split(',')]
        x4.append(list_[0])
        y4.append(list_[1])
    df['x1'] = x1
    df['x2'] = x2
    df['x3'] = x3
    df['x4'] = x4
    df['y1'] = y1
    df['y2'] = y2
    df['y3'] = y3
    df['y4'] = y4
    df = df[['text','x1','y1','x2','y2','x3','y3','x4','y4']]

    return df

# search overlapping boxes

# Returns true if two rectangles overlap
def overlap(box1,box2):
    ymin,xmin,ymax,xmax = box1
    Ymin,Xmin,Ymax,Xmax = box2
    
    # if rectangle has area 0, no overlap
    if (xmin == xmax or ymin == ymax or Xmin == Xmax or Ymin == Ymax):
        return False
    
    # If one rectangle is on left side of other
    if(xmin > Xmax or Xmin > xmax):
        return False

    # If one rectangle is above other
    if(ymin > Ymax or Ymin > ymax):
        return False

    return True

# returns all overlapping boxes
def getAllOverlaps(boxes, bounds, index):
    overlaps = []
    for a in range(len(boxes)):
        if a != index:
            if overlap(bounds, boxes[a]):
                overlaps.append(a)
    return overlaps

# returns coordinate grouped box

def grouped_box(coordinate_list):
    df_box = pd.DataFrame(coordinate_list,columns=['y1', 'x1', 'y2', 'x2'])
    df_box2 = df_box.copy()
    box_testing = df_box2[['y1', 'x1', 'y2', 'x2']].copy().values.tolist()

    box_before = len(box_testing)
    list_overlap = []
    for i in range(0,len(box_testing)):
        list_overlap.append(getAllOverlaps(box_testing, box_testing[i], i))
    
    group = []
    exclude = []
    j = 0
    for i in range(0,len(list_overlap)):
        if len(set(list_overlap[i])-set(exclude)) > 0:
            group.append([i] + list((set(list_overlap[i]) - set(exclude))))
            group[j].sort()
            exclude = (exclude + list((set(group[j]) - set(exclude))))
            exclude.sort()
            j = j+1
        if i not in exclude and len(set(list_overlap[i])-set(exclude)) == 0:
            group.append([i])
            exclude = exclude + [i]
            exclude.sort()
            j = j+1
    
    box_testing = []
    for i in range(0,len(group)):
        box_testing.append([df_box2.loc[group[i],['y1']].min()[0], df_box2.loc[group[i],['x1']].min()[0], \
                            df_box2.loc[group[i],['y2']].max()[0], df_box2.loc[group[i],['x2']].max()[0]])
    df_box2 = pd.DataFrame(box_testing,columns=['y1', 'x1', 'y2', 'x2'])
    df_box2['y2'] = df_box2['y2']+25
    # df_box2 = df_box2.sort_values('y2').reset_index(drop=True)
    return df_box2

def grouped_box_loop(coordinate_list):
    df_box = pd.DataFrame(coordinate_list,columns=['y1', 'x1', 'y2', 'x2'])
    df_box2 = df_box.copy()
    box_testing = df_box2[['y1', 'x1', 'y2', 'x2']].copy().values.tolist()

    while True:
        box_before = len(box_testing)
        list_overlap = []
        for i in range(0,len(box_testing)):
            list_overlap.append(getAllOverlaps(box_testing, box_testing[i], i))
        
        group = []
        exclude = []
        j = 0
        for i in range(0,len(list_overlap)):
            if len(set(list_overlap[i])-set(exclude)) > 0:
                group.append([i] + list((set(list_overlap[i]) - set(exclude))))
                group[j].sort()
                exclude = (exclude + list((set(group[j]) - set(exclude))))
                exclude.sort()
                j = j+1
            if i not in exclude and len(set(list_overlap[i])-set(exclude)) == 0:
                group.append([i])
                exclude = exclude + [i]
                exclude.sort()
                j = j+1
        
        box_testing = []
        for i in range(0,len(group)):
            box_testing.append([df_box2.loc[group[i],['y1']].min()[0], df_box2.loc[group[i],['x1']].min()[0], \
                                df_box2.loc[group[i],['y2']].max()[0], df_box2.loc[group[i],['x2']].max()[0]])
        df_box2 = pd.DataFrame(box_testing,columns=['y1', 'x1', 'y2', 'x2'])
        box_after = len(box_testing)
        
        if box_after == box_before:
            break

    # df_box2 = df_box2.sort_values('y1').reset_index(drop=True)
    return df_box2

# grouping result
def grouped_result(df_result,df_box):
    ind = []
    index_overlap = 0
    for i in range(0,df_result.shape[0]):
        smaller_box = df_result.loc[i,'y1'], df_result.loc[i,'x1'], df_result.loc[i,'y2'], df_result.loc[i,'x2']
        for j in range(0,df_box.shape[0]):
            bigger_box = df_box.loc[j,:].values.tolist()
            if overlap(bigger_box, smaller_box):
                index_overlap = j+1
        ind.append(index_overlap)
    df_result['group'] = ind

    return df_result
