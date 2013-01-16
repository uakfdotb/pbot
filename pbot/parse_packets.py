def parse_ng(data):
    """Parses NEWGAME packet."""
    ng_list=data.split()
    comp_dict={}
    comp_dict['PACKETNAME']=ng_list[0]
    comp_dict['MYNAME']=ng_list[1]
    comp_dict['OPPNAME']=ng_list[2]
    comp_dict['STACKSIZE']=int(ng_list[3])
    comp_dict['BIGBLIND']=int(ng_list[4])
    comp_dict['#HANDS']=int(ng_list[5])
    comp_dict['TIMEBANK']=float(ng_list[6])
    return comp_dict

def parse_nh(data):
    """Parses NEWHAND packet."""
    nh_list=data.split()
    comp_dict={}
    comp_dict['PACKETNAME']=nh_list[0]
    comp_dict['HANDID']=int(nh_list[1])
    comp_dict['BUTTON']=nh_list[2]
    comp_dict['HAND']=[nh_list[3],nh_list[4],nh_list[5]]
    comp_dict['MYBANK']=int(nh_list[6])
    comp_dict['OPPBANK']=int(nh_list[7])
    comp_dict['TIMEBANK']=float(nh_list[8])
    return comp_dict

def parse_ga(data): #<--Vital
    """Parses the GETACTION packet."""
    ga_list=data.split()
    comp_dict={}
    temp_list=[]
    #Parse the initial variables.
    comp_dict['PACKETNAME']=ga_list[0]
    comp_dict['POTSIZE']=int(ga_list[1])
    #Parse the boardcards.
    comp_dict['#BOARDCARDS']=int(ga_list[2])
    x=1
    while x<=comp_dict['#BOARDCARDS']:
        temp_list.append(ga_list[2+x])
        x+=1
    comp_dict['BOARDCARDS']=temp_list
    temp_list=[]
    #Parse last actions.
    index=3+comp_dict['#BOARDCARDS']
    comp_dict['#LASTACTIONS']=int(ga_list[index])
    x=1
    while x<=comp_dict['#LASTACTIONS']:
        temp_list.append(ga_list[index+x])
        x+=1
    comp_dict['LASTACTIONS']=temp_list
    temp_list=[]
    #Parse legal actions.
    index=4+comp_dict['#BOARDCARDS']+comp_dict['#LASTACTIONS']
    comp_dict['#LEGALACTIONS']=int(ga_list[index])
    x=1
    while x<=comp_dict['#LEGALACTIONS']:
        temp_list.append(ga_list[index+x])
        x+=1
    comp_dict['LEGALACTIONS']=temp_list
    #Finally, parse time bank.
    comp_dict['TIMEBANK']=float(ga_list[len(ga_list)-1])
    return comp_dict

def parse_ho(data):
    """Parses the HANDOVER packet."""
    ho_list=data.split()
    comp_dict={}
    temp_list=[]
    #Parse initial variables.
    comp_dict['PACKETNAME']=ho_list[0]
    comp_dict['MYBANK']=int(ho_list[1])
    comp_dict['OPPBANK']=int(ho_list[2])
    #Parse the boardcards.
    comp_dict['#BOARDCARDS']=int(ho_list[3])
    x=1
    while x<=comp_dict['#BOARDCARDS']:
        temp_list.append(ho_list[3+x])
        x+=1
    comp_dict['BOARDCARDS']=temp_list
    temp_list=[]
    #Parse last actions.
    index=4+comp_dict['#BOARDCARDS']
    comp_dict['#LASTACTIONS']=int(ho_list[index])
    x=1
    while x<=comp_dict['#LASTACTIONS']:
        temp_list.append(ho_list[index+x])
        x+=1
    comp_dict['LASTACTIONS']=temp_list
    temp_list=[]
    #Parse time bank.
    comp_dict['TIMEBANK']=float(ho_list[len(ho_list)-1])
    return comp_dict
    
def master_parse(data):
    """Parses any packet."""
    try:
        word=data.split()[0]
    except AttributeError:
        raise Exception('Data must be string.')
    if word=='NEWGAME':
        return parse_ng(data)
    elif word=='NEWHAND':
        return parse_nh(data)
    elif word=='GETACTION':
        return parse_ga(data)
    elif word=='HANDOVER':
        return parse_ho(data)
    else:
        print 'Not a valid packet.'
