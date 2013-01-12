def parse_list(ga_list):
    comp_dict={}
    temp_list=[]
    #Parse the initial variables.
    comp_dict['GETACTION']=ga_list[0]
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
    comp_dict['TIMEBANK']=ga_list[len(ga_list)-1]
    #Return organized dictionary.
    return comp_dict
