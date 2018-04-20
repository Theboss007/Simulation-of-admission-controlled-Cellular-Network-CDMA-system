import numpy as np
"""The base station is assumed to be in the centre of the circle(0,0). Separate functions for fadinf,
pathloss, getting user's distance, getting the location of user in a 10m X 10m box, to retreieve RSL values and SINR values,
conditions for getting connected and condiitons for getting reconnected are written"""
def fading():
    """returns fading values in DB, which change every second"""
    fdng=np.random.rayleigh()
    fdng_db=20*np.log10(fdng)
    return fdng_db

def pathloss(coordinates):
    """returns pathloss that remains same for a defined user untill he moves away from that place
    pathloss formula is separated into three parts for avoding confusion in the calculation """
    pl1=46.3+33.9*np.log10(fc)-13.82*np.log10(h)
    pl21=(44.9-6.55*np.log10(h))
    pl22=np.log10(get_distance(coordinates))
    pl2=pl21*pl22
    pl=pl1+pl2
    return pl

def get_distance(coordinates):
    """return the distance of the user from the basestation
    this is the same value as the r value, where we genearated the user coordinates,
    for easy acces inside the dicitonary, we calculate it again"""
    x2= coordinates[0] **2
    y2= coordinates[1] **2
    return np.sqrt(x2+y2)

def get_user_box(coordinates):
    """return the box in which the user is present for calculationg the shadowing values
    first converts the user location to meters then rounds up the decimal values and the rounds to the teth place
    and returns a x and y value which form box of side 10X10m"""
    x_in_meters= coordinates[0] * 1000
    y_in_meters= coordinates[1] * 1000
    x_rounded=int(x_in_meters)
    y_rounded=int(y_in_meters)
    x_coor=int(np.ceil(x_rounded/ 10.0) * 10)
    y_coor=int(np.ceil(y_rounded/ 10.0) * 10)
    dist_coordinates=(x_coor,y_coor)
    return dist_coordinates
    
def get_rsl(coordinates,user_dist):
    """returns RSL value by going through control flow statements for given condtions
    admission control system is implemented by setting the lower and upper channel limits"""
    global eirp, channels_available
    if channels_available>cd:
        eirp-=0.5
    elif channels_available<ci:
        eirp+=0.5
    if eirp < 30:
        eirp=30
        rsl=30-pathloss(coordinates)+shadow[user_dist]+fading()
    else:
        rsl=eirp-pathloss(coordinates)+shadow[user_dist]+fading()#RSl value if there is going to be no admission control
    return rsl

def checking_for_reconnection(coordinates):
    """function to check the reconnection part of the program(both for low rsl and SINR values)
    if equal to three,then maximum attempts have been reached so all the flags are nullified and
    the counter for calls blocked due to signal strength is increased"""
    #returns none functions, changes just the user flags
    global calls_blocked_due_to_signal_strenth
    if user_dict[coordinates]["Reconnect"] >= 3: 
        user_dict[coordinates]["Reconnect"]=0
        user_dict[coordinates]["RSL"]=0
        user_dict[coordinates]["Talking time"]=0
        user_dict[coordinates]["Status"]=""
        calls_blocked_due_to_signal_strenth+=1 
    return
    
def conditons_for_getting_connected(coordinates,current_time):
    """function executed when the user has the probability to call and to check if he has sufficient RSl and channel capacity
        if RSL is less than it will call the checking_for_reconnection() to check whether the maximum attempts have been reached for reconnection
        if RSl is more than the sufficient value, then we check whether a channel is available or not, if available, we allocate channel and
        the user_dict flags are changed accordingly, and if channel is not avilable then the call is blocked
        and the counter calls_blocked_due_to_channel_capacity is increased by 1"""
    #return nothing, function to change only the user flags
    global channels_available,user_dict,calls_blocked_due_to_channel_capacity
    if user_dict[coordinates]["RSL"] < -107:
        user_dict[coordinates]["Reconnect"]+=1
        checking_for_reconnection(coordinates)
        return
    
    else:
        if channels_available > 0:#if available,then aallots a channel, gives a random talk time for user, change sthe status to active and also makes reconnect to 0
            channels_available=channels_available-1
            user_dict[coordinates]["Talking time"]=current_time+np.random.exponential(60)
            user_dict[coordinates]["Status"]="Active"
            user_dict[coordinates]["Reconnect"]=0
            return
        else:#if no channel available
            #The call is blocked due to channel capacity
            calls_blocked_due_to_channel_capacity+=1
            return
        
def get_sinr(coordinates):
    """return SINR value in DB, and does the calculation for the signal level, interference level and noise level,
    the active users is calculated here and maintained as a global variable,
    the intereference is set to zero if the number of active users is less than or equal to one"""
    global channels_available,active_users
    signal_level=user_dict[coordinates]["RSL"]+pg
    active_users=56-channels_available #to track active users,made global so that in admission control gives a very easy access for cheking the current value
    if active_users <=1:
        interference_level =0# to avoid the 
    else:
        interference_level=10**((user_dict[coordinates]["RSL"]+10*np.log10(active_users-1))/10)
    noise_level=10**((-110)/10)
    inr_level=interference_level+noise_level
    inr_level_db=10*np.log10(inr_level)
    return(signal_level-inr_level_db)


""" ##########################################################MAIN######PROGRAM####STARTS###########################################################################"""
#Given values
bstn_ptx=42 #Basetation maximum transmitter power
loss=2.1 #Line and Connector loss
Ga=12.1 #Antenna Gain
fc=1900 #carrie frequency
h=50 #basetation height
channels_available=56 
pg=20 #Processor Gain
minimum_sinr=6 #Minimum SINR for the call to get connected
cd=20#upper limit for the admission control
ci=15#lower limit for the admission control
number_of_users=10000 #Total number of users in the cell
shadow={}#dicitonary to store the shadowing values of 4 million boxes(explained below)




"""variables initialized, so that they can be accesed later  """
active_users = 0
calls_attempted_without_retries=0
Total_calls_attempted=0
print_counter=0
successful_calls=0
dropped_calls=0
calls_blocked_due_to_signal_strenth = 0
calls_blocked_due_to_channel_capacity = 0
dist_list=[]



#calculation of eirp
eirp=bstn_ptx-loss+Ga


#calculation of shadowing for 4 million boxes(with sides = 10m) formed inside a single, 20km X 20km box
for x in range(-10000,10000,10):
    for y in range(-10000,10000,10):
        shadow[(x,y)]=np.random.normal(0,2)

        
"""snippet for creatinf specified number of users with given distribution
and finally gives the list of tuptles with x and y coordinates of each user """        
t = np.random.uniform(0.0, 2.0*np.pi,number_of_users)
r = np.sqrt(np.random.uniform(0.0, 100,number_of_users))
x = list(r * np.cos(t))     #length is 1000
y = list(r * np.sin(t)      )#length is 1000
user_coordinates=list(zip(x,y))



"""user_dict is the master where the staus of all the users are maintained globally and
accesed across the functions just by passing coordinates across the functions """
user_dict=dict((i,{"Status":"","Reconnect":0,"RSL":0,"Talking time":0}) for i in user_coordinates)




""" the below loop executes 7200 times simulating 2 hours for each second considered as a loop"""

for j in range(7200):
    """The below loww executes for every user in a cell """
    for i in user_coordinates:
        """Checks whether the user is Active or not
            if not active(during the first time, obviously), checks for the probability of user connecting to the call
            if active, gets new rsl value, as fading changes with time and
            conditons_for_getting_connected() functions"""
        if user_dict[i]["Status"] is not "Active": 
            if user_dict[i]["Reconnect"] == 0:
                probability=np.random.choice(range(1,601))#probability of choosing a user
                if probability == 1:#user makes a call
                    """if the user is probable to make a call the user_dict
                        for the particular user's RSL is updated,total calls attempted and number of calls without retries ia also updated"""
                    shadowing_box=get_user_box(i)
                    user_dict[i]["RSL"] = get_rsl(i,shadowing_box)
                    Total_calls_attempted+=1
                    calls_attempted_without_retries+=1
                    conditons_for_getting_connected(i,j)
            else :
                shadowing_box=get_user_box(i)
                user_dict[i]["RSL"] = get_rsl(i,shadowing_box)
                Total_calls_attempted+=1
                conditons_for_getting_connected(i,j)     
        else:
            #User is now active

            dist_list.append(get_distance(i))
            cell_radius=max(dist_list)
            
            if j < user_dict[i]["Talking time"]:
                """user is still talking, so the talking time is reduced by 1 second
                and SINR value is calculated and checked whether it has crossed the minimum value"""
                user_dict[i]["Talking time"]-=1
                sinr=get_sinr(i)
                if sinr < minimum_sinr:
                    """CALLS getting dropped because of LOW SINR
                    so, calls the reconnection function to check whsther the maximum connections are reached, if reached then resets the value
                    increases dropped calls and makes one channel free for next user"""
                    user_dict[i]["Reconnect"]+=1
                    checking_for_reconnection(i)
                    if user_dict[i]["Status"] is not "Active":
                        dropped_calls+=1
                        channels_available+=1
                        
                    
            else:
                """user is done with the call,all values are reset, successfull calls count is updated"""
                successful_calls+=1
                user_dict[i]["Talking time"]=0
                user_dict[i]["RSL"]=0
                user_dict[i]["Status"]=""
                channels_available+=1


                
 #For reporting every 2 minutes               
    print_counter+=1
    if print_counter == 120:
        print_counter=0
        print("Number of calls attempted not counting retries",calls_attempted_without_retries)
        print("Number of calls attempted including retries",Total_calls_attempted)
        print("Number of dropped calls",dropped_calls)
        print("Number of blocked calls due to signal strength",calls_blocked_due_to_signal_strenth)
        print("Number of blocked calls due to channel capacity",calls_blocked_due_to_channel_capacity)
        print("Number of successfully completed calls",successful_calls)
        print("Number of calls in progress at any given time",active_users)
        print("Number of failed calls",dropped_calls+calls_blocked_due_to_signal_strenth+calls_blocked_due_to_channel_capacity)
        print("Current cell radius",cell_radius,"Kilometers")

                

     
                                 
                
                
    





