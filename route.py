#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: Abhijeet Vichare, Raksha Rank, Sreekar Chigurupati 
#
# Based on skeleton code by V. Mathur and D. Crandall, January 2021

# !/usr/bin/env python3
import sys
import pandas as pd
import heapq
from math import radians, cos, sin, asin, sqrt, tanh

def haversine(lon1, lat1, lon2, lat2): ## Reference: Wikipedia https://en.wikipedia.org/wiki/Haversine_formula
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat2 = radians(lat2)
    # haversine formula 
    lon_diff = lon2 - lon1 
    lat_diff = lat2 - lat1 
    hav_theta = sin(lat_diff/2)**2 + cos(lat1) * cos(lat2) * sin(lon_diff/2)**2
    archav = 2 * asin(sqrt(hav_theta)) 
    r = 3958.5
    return archav * r

def cost(dist,time,delivery,row,col_to_cons,curr_city): #calculating the total_miles, total_hours, total_delivery_hours any given city
    dist[row[col_to_cons]] = dist[curr_city] + row['length']
    time[row[col_to_cons]] = time[curr_city] + row['length']/row['speed_limit'] 
    delivery[row[col_to_cons]] = delivery[curr_city] + row['length']/row['speed_limit'] 
    if row['speed_limit']>= 50: #adding penalty if speed limit for the highway greater than 50mph
        delivery[row[col_to_cons]] += (tanh(row['length']/1000)*2*(time[curr_city] + row['length']/row['speed_limit']))
    return (dist,time,delivery)

def get_accurate_gps(city,gps_df,dist_df): # for missing gps values, fetching the nearest city's gps value and if even that doesn't exist, replacing the missing gps values with (0,0)
    gps_cities = set(gps_df.city.unique())
    if city in gps_df.city:
        return gps_df.loc[gps_df.city == city,['long','lat']].values[0]
    else:
        temp = dist_df[(dist_df.city_1 == city) | (dist_df.city_2 == city)].sort_values(['length'])
        for index, row in temp.iterrows():
            near_city_col = 'city_2'
            if row['city_2'] == city:
                near_city_col = 'city_1'
            near_city = row[near_city_col]
            near_dist = row['length']
            if near_city in gps_cities:
                break
    if gps_df.loc[gps_df.city == near_city,['long','lat']].shape[0] < 1:
        return [0,0]
    return gps_df.loc[gps_df.city == near_city,['long','lat']].values[0]

def  segment(start, end,data,data_gps): #function to optimise number of segments traversed from start to end
    visited = dict() # dictionary for marking visited nodes 
    dist = dict({start:0})
    time = dict({start:0})
    delivery = dict({start:0})
    queue = []
    visited[start] = True
    path = []
    queue.append((start,path,0,0,0))
    while(queue):
        curr_city,curr_path,curr_dist,curr_time,curr_delivery = queue.pop(0) # Popping the values from the queue in a level order manner
        if(curr_city == end):
            return curr_path, curr_dist, curr_time, curr_delivery
        cond = (data['city_1'] == curr_city) | (data['city_2'] == curr_city)
        for index, row in data[cond].iterrows():
            col_to_cons = 'city_1'
            if row['city_1'] == curr_city:
                col_to_cons = 'city_2'
            if(row[col_to_cons] not in visited):
                visited[row[col_to_cons]] = True
                temp_path = curr_path.copy()
                temp_path.append((row[col_to_cons], row['highway']))   
                new_dist = curr_dist + row['length']
                new_time =  curr_time +  row['length']/row['speed_limit']
                new_delivery = curr_delivery +  row['length']/row['speed_limit']
                if row['speed_limit']>=50:
                    new_delivery += (tanh(row['length']/1000)*2*(curr_time + row['length']/row['speed_limit']))
                queue.append((row[col_to_cons], temp_path, new_dist,new_time,new_delivery)) # appending the required paramters in the queue

def distance(start, end,data,data_gps): #function to optimise the distance traversed from start to end
    visited = dict() # making a dictionary for marking visited nodes 
    dist = dict({start:0})
    time = dict({start:0})
    delivery = dict({start:0})
    queue = []
    path = []
    parent = dict() # keeping track of parents to traceback for path
    end_coords = get_accurate_gps(end,data_gps,data)
    parent[start] = ("-1", "-1")
    heapq.heappush(queue,(0,0,0, start))
    while(queue):
        curr_dist,curr_time,curr_delivery, curr_city = heapq.heappop(queue) #popping from the priority queue on the basis of curr_dist
        if(curr_city == end):
            break;
        if(curr_city in visited):
            continue
        visited[curr_city] = True  
        cond = (data['city_1'] == curr_city) | (data['city_2'] == curr_city)
        for index, row in data[cond].iterrows():
            col_to_cons = 'city_1'
            if row['city_1'] == curr_city:
                col_to_cons = 'city_2'
            if(row[col_to_cons] not in dist):
                dist,time,delivery = cost(dist,time,delivery,row,col_to_cons,curr_city)
                parent[row[col_to_cons]] = (curr_city, row['highway'])
            else:
                if(dist[row[col_to_cons]] > dist[curr_city] + row['length']):
                    dist,time,delivery = cost(dist,time,delivery,row,col_to_cons,curr_city)
                    parent[row[col_to_cons]] = (curr_city, row['highway'])
            mid_city = row[col_to_cons]
            mid_coords = get_accurate_gps(mid_city,data_gps,data)
            haversine_dist = haversine(end_coords[0],end_coords[1], mid_coords[0],mid_coords[1])
            heapq.heappush(queue, (dist[row[col_to_cons]] + haversine_dist,
                        time[row[col_to_cons]] + haversine_dist/row['speed_limit'],
                        delivery[row[col_to_cons]]+ haversine_dist/row['speed_limit'] ,
                        row[col_to_cons] ) )
    tmp = end
    curr_path = []
    while(tmp != start):
        tmp1 = tmp;
        tmp, hw = parent[str(tmp)]
        curr_path.append((str(tmp1), hw)) #tracing back for the path
        
    return curr_path[::-1],dist[end], time[end], delivery[end]

def time(start, end, data, data_gps): #function to optimise the time traversed from start to end
    visited=dict() # making a dictionary for marking visited nodes 
    dist = dict({start:0})
    time = dict({start:0})
    delivery = dict({start:0})
    queue = []
    path = []
    parent = dict({start:("-1", "-1")})
    end_coords = get_accurate_gps(end,data_gps,data)
    heapq.heappush(queue,(0,0,0,start))
    while(queue):
        curr_time,curr_dist,curr_delivery, curr_city = heapq.heappop(queue) #popping values based on the value of current time
        if(curr_city == end):
            break;
        if(curr_city in visited):
            continue
        visited[curr_city] = True
        cond = (data['city_1'] == curr_city) | (data['city_2'] == curr_city)
        for index, row in data[cond].iterrows():
            col_to_cons = 'city_1'
            if row['city_1'] == curr_city:
                col_to_cons = 'city_2'
            if(row[col_to_cons] not in time):
                dist,time,delivery = cost(dist,time,delivery,row,col_to_cons,curr_city)
                parent[row[col_to_cons]] = (curr_city, row['highway'])
            else:
                if(time[row[col_to_cons]] > time[curr_city] + row['length']/row['speed_limit']):
                    dist,time,delivery = cost(dist,time,delivery,row,col_to_cons,curr_city)
                    parent[row[col_to_cons]] = (curr_city, row['highway'])
            mid_city = row[col_to_cons]
            mid_coords = get_accurate_gps(mid_city,data_gps,data)
            haversine_dist = haversine(end_coords[0],end_coords[1], mid_coords[0],mid_coords[1])
            heapq.heappush(queue, (time[row[col_to_cons]] + haversine_dist/row['speed_limit'] ,
            dist[row[col_to_cons]]+haversine_dist,
            delivery[row[col_to_cons]] + haversine_dist/row['speed_limit'] ,
            row[col_to_cons] ) )
    tmp = end
    curr_path = []
    while(tmp != start):
        tmp1 = tmp;
        tmp, hw = parent[str(tmp)]
        curr_path.append((str(tmp1), hw))
    
    return curr_path[::-1],dist[end], time[end],delivery[end]

def delivery (start, end,data,data_gps): #function to optimise the delivery time traversed from start to end
    visited=dict() # making a dictionary for marking visited nodes 
    dist = dict({start:0})
    time = dict({start:0})
    delivery = dict({start:0})
    queue = []
    path = []
    parent = dict({start:("-1", "-1")})
    end_coords = get_accurate_gps(end,data_gps,data)
    heapq.heappush(queue,(0,0,0,start))
    while(queue):
        curr_delivery,curr_dist,curr_time,curr_city = heapq.heappop(queue)
        if(curr_city == end):
            break;
        if(curr_city in visited):
            continue
        visited[curr_city] = True
        cond = (data['city_1'] == curr_city) | (data['city_2'] == curr_city)
        for index, row in data[cond].iterrows():
            col_to_cons = 'city_1'
            if row['city_1'] == curr_city:
                col_to_cons = 'city_2'
            if(row[col_to_cons] not in delivery):
                dist,time,delivery = cost(dist,time,delivery,row,col_to_cons,curr_city)
                delivery[row[col_to_cons]] = delivery[curr_city] + row['length']/row['speed_limit']
                if(row['speed_limit']>=50): # if speed of the highway is >=50, we add the penalty cost to the delivery time
                    dist,time,delivery = cost(dist,time,delivery,row,col_to_cons,curr_city)
                parent[row[col_to_cons]] = (curr_city, row['highway'])
            else:
                if row['speed_limit']<50 :
                    if(delivery[row[col_to_cons]] > delivery[curr_city] + row['length']/row['speed_limit']):
                        dist,time,delivery = cost(dist,time,delivery,row,col_to_cons,curr_city)
                        delivery[row[col_to_cons]] = delivery[curr_city] + row['length']/row['speed_limit']
                        parent[row[col_to_cons]] = (curr_city, row['highway'])
                else:
                    if(delivery[row[col_to_cons]] > delivery[curr_city] + row['length']/row['speed_limit'] + (tanh(row['length']/1000)*2*(delivery[curr_city] + row['length']/row['speed_limit']))):
                        dist,time,delivery = cost(dist,time,delivery,row,col_to_cons,curr_city)
                        parent[row[col_to_cons]] = (curr_city, row['highway'])

            mid_city = row[col_to_cons]
            mid_coords = get_accurate_gps(mid_city,data_gps,data)
            haversine_dist = haversine(end_coords[0],end_coords[1], mid_coords[0],mid_coords[1])
            
            heapq.heappush(queue, (
                delivery[row[col_to_cons]]+haversine_dist/row['speed_limit'],
                dist[row[col_to_cons]]+haversine_dist,
                time[row[col_to_cons]] + haversine_dist/row['speed_limit'],
                row[col_to_cons] ) )
    tmp = end
    curr_path = []
    while(tmp != start):
        tmp1 = tmp;
        tmp, hw = parent[str(tmp)]
        curr_path.append((str(tmp1), hw))
    return curr_path[::-1],dist[end], time[end],delivery[end]

def get_route(start, end, cost):

    data = pd.read_csv("road-segments.txt", header=None, delimiter=r"\s+")
    data = data.rename({0: 'city_1', 1: 'city_2', 2: 'length', 3: 'speed_limit', 4: 'highway'}, axis=1)
    data = pd.DataFrame(data)

    data_gps = pd.read_csv("city-gps.txt", header=None, delimiter=r"\s+")
    data_gps = data_gps.rename({0: 'city', 1: 'lat', 2: 'long'}, axis=1)
    data_gps = pd.DataFrame(data_gps)
    route_taken = []
    total_miles = 0
    total_hours = 0

    #Depending on the cost function, we are returning values for route_taken, total_miles, total_hours andn total_delivery_hours

    if(cost == "segments"):
        route_taken, total_miles, total_hours, total_delivery_hours = segment(start, end,data,data_gps)
    elif(cost == "distance"):
        route_taken, total_miles, total_hours, total_delivery_hours = distance(start, end,data,data_gps)
    elif(cost == "time"):
        route_taken, total_miles, total_hours, total_delivery_hours = time(start, end,data,data_gps)
    elif(cost == 'delivery'):
        route_taken, total_miles, total_hours, total_delivery_hours = delivery(start, end,data,data_gps)
    
    # route_taken = [("Martinsville,_Indiana","IN_37 for 19 miles"),
    #                ("Jct_I-465_&_IN_37_S,_Indiana","IN_37 for 25 miles"),
    #                ("Indianapolis,_Indiana","IN_37 for 7 miles")]
    
    return {"total-segments" : len(route_taken), 
            "total-miles" : float(total_miles), 
            "total-hours" : total_hours, 
            "total-delivery-hours" : total_delivery_hours, 
            "route-taken" : route_taken}


# Please don't modify anything below this line

if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "delivery"):
        raise(Exception("Error: invalid cost function"))

    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n          Total segments: %4d" % result["total-segments"])
    print("             Total miles: %8.3f" % result["total-miles"])
    print("             Total hours: %8.3f" % result["total-hours"])
    print("Total hours for delivery: %8.3f" % result["total-delivery-hours"])


