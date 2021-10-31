#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: name IU ID
#
# Based on skeleton code by V. Mathur and D. Crandall, January 2021
#


# !/usr/bin/env python3
import sys
import pandas as pd
import heapq
from math import radians, cos, sin, asin, sqrt, tanh

def haversine(lon1, lat1, lon2, lat2): ## stackoverflow https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units. 6371 for kms
    return c * r


data = pd.read_csv("road-segments.txt", header=None, delimiter=r"\s+")
data = data.rename({0: 'city_1', 1: 'city_2', 2: 'length', 3: 'speed_limit', 4: 'highway'}, axis=1)
data = pd.DataFrame(data)

data_gps = pd.read_csv("city-gps.txt", header=None, delimiter=r"\s+")
data_gps = data_gps.rename({0: 'city', 1: 'lat', 2: 'long'}, axis=1)
data_gps = pd.DataFrame(data_gps)


def segment(start, end):
    visited=dict() # making a dictionary for marking visited nodes 
    queue = []
    visited[start] = True
    path = []
    queue.append((start,path,0))
    while(queue):
        curr_city,curr_path,curr_dist = queue.pop(0)
        # print(curr_city)
        # print(curr_path)
        if(curr_city == end):
            return curr_path, curr_dist
            
        cond1 = (data['city_1'] == curr_city)
        cond2 = (data['city_2'] == curr_city)

        for index, row in data[cond1].iterrows():
            #print(row['city_1'], row['city_2'])
            if(row['city_2'] not in visited):
                visited[row['city_2']] = True
                temp_path = curr_path.copy()
               # print("row:", temp_path)
                temp_path.append((row['city_2'], row['highway']))
                queue.append((row['city_2'], temp_path, curr_dist+row['length']))

        for index, row in data[cond2].iterrows():
            #print(row['city_1'], row['city_2'])
            if(row['city_1'] not in visited):
                visited[row['city_1']] = True
                temp_path = curr_path.copy()
             #   print("row:", temp_path)
                temp_path.append((row['city_1'], row['highway']))
                queue.append((row['city_1'], temp_path, curr_dist+row['length']))


def distance(start, end): # if end lat long not available, if mid lat long not available
    visited=dict() # making a dictionary for marking visited nodes 
    dist = dict()
    dist[start] = 0
    queue = []
    path = []
    parent = dict()
    
    #path.append(start)

    cond_gps = (data_gps['city'] == end)
    #end_gps = data_gps[cond_gps]
    end_index = data_gps.index[cond_gps]

    parent[start] = ("-1", "-1")
    heapq.heappush(queue,(0, start))
    while(queue):
        curr_dist, curr_city = heapq.heappop(queue)
        if(curr_city == end):
            break;
        if(curr_city in visited):
            continue
        # print(curr_city) 
        visited[curr_city] = True
            
        cond1 = (data['city_1'] == curr_city)
        cond2 = (data['city_2'] == curr_city)

        for index, row in data[cond1].iterrows():
            #print(row['city_1'], row['city_2'])
            if(row['city_2'] not in dist):
                dist[row['city_2']] = dist[curr_city] + row['length']
                parent[row['city_2']] = (curr_city, row['highway'])
            else:
                if(dist[row['city_2']] > dist[curr_city] + row['length']):
                    dist[row['city_2']] = dist[curr_city] + row['length']
                    parent[row['city_2']] = (curr_city, row['highway'])

            cond1_gps = (data_gps['city'] == row['city_2'])
            index = list(data_gps.index[cond1_gps])
            if index:
                haversine_dist = haversine(float(data_gps['long'][end_index[0]]), float(data_gps['lat'][end_index[0]]), float(data_gps['long'][index[0]]), float(data_gps['lat'][index[0]]))
            else:
                haversine_dist = 0.00
            
            heapq.heappush(queue, (dist[row['city_2']] + haversine_dist, row['city_2'] ) )

        for index, row in data[cond2].iterrows():
            #print(row['city_1'], row['city_2'])
            if(row['city_1'] not in dist):
                dist[row['city_1']] = dist[curr_city] + row['length']
                parent[row['city_1']] = (curr_city, row['highway'])
            else:
                if(dist[row['city_1']] > dist[curr_city] + row['length']):
                    dist[row['city_1']] = dist[curr_city] + row['length']
                    parent[row['city_1']] = (curr_city, row['highway'])
            cond1_gps = (data_gps['city'] == row['city_1'])
            index = list(data_gps.index[cond1_gps])
            if index:
                # if we have the coordinates
                haversine_dist = haversine(float(data_gps['long'][end_index[0]]), float(data_gps['lat'][end_index[0]]), float(data_gps['long'][index[0]]), float(data_gps['lat'][index[0]]))
            else:
                #if no coordinates found
                haversine_dist = 0.00
            
            heapq.heappush(queue, (dist[row['city_1']] + haversine_dist, row['city_1'] ) )
    tmp = end
    curr_path = []
    while(tmp != start):
        tmp1 = tmp;
        tmp, hw = parent[str(tmp)]
        curr_path.append((str(tmp1), hw))
        
    return curr_path[::-1], dist[end]


def time(start, end): 
    visited=dict() # making a dictionary for marking visited nodes 
    dist = dict()
    time = dict()
    time[start] = 0
    dist[start] = 0
    queue = []
    path = []
    parent = dict()
    #path.append(start)

    cond_gps = (data_gps['city'] == end)
    end_index = data_gps.index[cond_gps]

    parent[start] = ("-1", "-1")

    heapq.heappush(queue,(0,start))
    while(queue):
        curr_time, curr_city = heapq.heappop(queue)
        if(curr_city == end):
            break;
        if(curr_city in visited):
            continue
        #print(curr_city) 
        visited[curr_city] = True

            
        cond1 = (data['city_1'] == curr_city)
        cond2 = (data['city_2'] == curr_city)

        for index, row in data[cond1].iterrows():
            #print(row['city_1'], row['city_2'])
            if(row['city_2'] not in time):
                time[row['city_2']] = time[curr_city] + row['length']/row['speed_limit']
                parent[row['city_2']] = (curr_city, row['highway'])
            else:
                if(time[row['city_2']] > time[curr_city] + row['length']/row['speed_limit']):
                    time[row['city_2']] = time[curr_city] + row['length']/row['speed_limit']
                    parent[row['city_2']] = (curr_city, row['highway'])

            cond1_gps = (data_gps['city'] == row['city_2'])
            index = list(data_gps.index[cond1_gps])
            if index:
                haversine_dist = haversine(float(data_gps['long'][end_index[0]]), float(data_gps['lat'][end_index[0]]), float(data_gps['long'][index[0]]), float(data_gps['lat'][index[0]]))
            else:
                haversine_dist = 0.00
           
            heapq.heappush(queue, (time[row['city_2']] + haversine_dist/row['speed_limit'], row['city_2'] ) )

        for index, row in data[cond2].iterrows():
            #print(row['city_1'], row['city_2'])
            if(row['city_1'] not in time):
                time[row['city_1']] = time[curr_city] + row['length']/row['speed_limit']
                parent[row['city_1']] = (curr_city, row['highway'])
            else:
                if(time[row['city_1']] > time[curr_city] + row['length']/row['speed_limit']):
                    time[row['city_1']] = time[curr_city] + row['length']/row['speed_limit']
                    parent[row['city_1']] = (curr_city, row['highway'])
                
            cond1_gps = (data_gps['city'] == row['city_1'])
            index = list(data_gps.index[cond1_gps])
            if index:
                # if we have the coordinates
                haversine_dist = haversine(float(data_gps['long'][end_index[0]]), float(data_gps['lat'][end_index[0]]), float(data_gps['long'][index[0]]), float(data_gps['lat'][index[0]]))
            else:
                #if no coordinates found
                haversine_dist = 0.00

            heapq.heappush(queue, (time[row['city_1']] + haversine_dist/row['speed_limit'], row['city_1'] ) )
    tmp = end
    curr_path = []
    while(tmp != start):
        tmp1 = tmp;
        tmp, hw = parent[str(tmp)]
        curr_path.append((str(tmp1), hw))
        
    return curr_path[::-1], time[end]

def delivery (start, end): 
    visited=dict() # making a dictionary for marking visited nodes 
    dist = dict()
    time = dict()
    time[start] = 0
    dist[start] = 0
    queue = []
    path = []
    parent = dict()
    #path.append(start)

    cond_gps = (data_gps['city'] == end)
    end_index = data_gps.index[cond_gps]

    parent[start] = ("-1", "-1")

    heapq.heappush(queue,(0,start))
    while(queue):
        curr_time, curr_city = heapq.heappop(queue)
        if(curr_city == end):
            break;
        if(curr_city in visited):
            continue
        #print(curr_city) 
        visited[curr_city] = True
  
        cond1 = (data['city_1'] == curr_city)
        cond2 = (data['city_2'] == curr_city)
        
        for index, row in data[cond1].iterrows():
            #print(row['city_1'], row['city_2'])
            if(row['city_2'] not in time):
                time[row['city_2']] = time[curr_city] + row['length']/row['speed_limit']
                if(row['speed_limit']>=50):
                    time[row['city_2']] = time[curr_city] + (tanh(row['length']/1000)*2*(time[curr_city] + row['length']/row['speed_limit']))
                parent[row['city_2']] = (curr_city, row['highway'])
            elif(row['speed_limit']<50):
                if(time[row['city_2']] > time[curr_city] + row['length']/row['speed_limit']):
                    time[row['city_2']] = time[curr_city] + row['length']/row['speed_limit']
                parent[row['city_2']] = (curr_city, row['highway'])
            else:
                if(time[row['city_2']] > time[curr_city] + (tanh(row['length']/1000)*2*(time[curr_city] + row['length']/row['speed_limit']))):
                    time[row['city_2']] = time[curr_city] + (tanh(row['length']/1000)*2*(time[curr_city] + row['length']/row['speed_limit']))

            cond1_gps = (data_gps['city'] == row['city_2'])
            index = list(data_gps.index[cond1_gps])
            if index:
                haversine_dist = haversine(float(data_gps['long'][end_index[0]]), float(data_gps['lat'][end_index[0]]), float(data_gps['long'][index[0]]), float(data_gps['lat'][index[0]]))
            else:
                haversine_dist = 0.00
           
            heapq.heappush(queue, (time[row['city_2']] + haversine_dist/row['speed_limit'], row['city_2'] ) )

        for index, row in data[cond2].iterrows():
            #print(row['city_1'], row['city_2'])
            if(row['city_1'] not in time):
                time[row['city_1']] = time[curr_city] + row['length']/row['speed_limit']
                if(row['speed_limit']>=50):
                    time[row['city_1']] = time[curr_city] + (tanh(row['length']/1000)*2*(time[curr_city] + row['length']/row['speed_limit']))
                parent[row['city_1']] = (curr_city, row['highway'])
            elif(row['speed_limit']<50):
                if(time[row['city_1']] > time[curr_city] + row['length']/row['speed_limit']):
                    time[row['city_1']] = time[curr_city] + row['length']/row['speed_limit']
                parent[row['city_1']] = (curr_city, row['highway'])
            else:
                if(time[row['city_1']] > time[curr_city] + (tanh(row['length']/1000)*2*(time[curr_city] + row['length']/row['speed_limit']))):
                    time[row['city_1']] = time[curr_city] + (tanh(row['length']/1000)*2*(time[curr_city] + row['length']/row['speed_limit']))

            cond1_gps = (data_gps['city'] == row['city_1'])
            index = list(data_gps.index[cond1_gps])
            if index:
                # if we have the coordinates
                haversine_dist = haversine(float(data_gps['long'][end_index[0]]), float(data_gps['lat'][end_index[0]]), float(data_gps['long'][index[0]]), float(data_gps['lat'][index[0]]))
            else:
                #if no coordinates found
                haversine_dist = 0.00

            heapq.heappush(queue, (time[row['city_1']] + haversine_dist/row['speed_limit'], row['city_1'] ) )
    tmp = end
    curr_path = []
    while(tmp != start):
        tmp1 = tmp;
        tmp, hw = parent[str(tmp)]
        curr_path.append((str(tmp1), hw))
        
    return curr_path[::-1], time[end]

def get_route(start, end, cost):
    
    """
    Find shortest driving route between start city and end city
    based on a cost function.

    1. Your function should return a dictionary having the following keys:
        -"route-taken" : a list of pairs of the form (next-stop, segment-info), where
           next-stop is a string giving the next stop in the route, and segment-info is a free-form
           string containing information about the segment that will be displayed to the user.
           (segment-info is not inspected by the automatic testing program).
        -"total-segments": an integer indicating number of segments in the route-taken
        -"total-miles": a float indicating total number of miles in the route-taken
        -"total-hours": a float indicating total amount of time in the route-taken
        -"total-delivery-hours": a float indicating the expected (average) time 
                                   it will take a delivery driver who may need to return to get a new package
    2. Do not add any extra parameters to the get_route() function, or it will break our grading and testing code.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """
    route_taken = []
    total_miles = 0
    total_hours = 0

    if(cost == "segments"):
        route_taken, total_miles = segment(start, end)
    elif(cost == "distance"):
        route_taken, total_miles = distance(start, end)
    elif(cost == "time"):
        route_taken, total_hours = time(start, end)
    elif(cost == 'delivery'):
        route_taken, total_delivery_hours = delivery(start,end)

    # route_taken = [("Martinsville,_Indiana","IN_37 for 19 miles"),
    #                ("Jct_I-465_&_IN_37_S,_Indiana","IN_37 for 25 miles"),
    #                ("Indianapolis,_Indiana","IN_37 for 7 miles")]
    
    return {"total-segments" : len(route_taken), 
            "total-miles" : total_miles, 
            "total-hours" : total_hours, 
            "total-delivery-hours" : 1.1364, 
            "route-taken" : route_taken}


# Please don't modify anything below this line
#
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


