# Travelling-Salesman-Problem

#### This problem is part of the assignment of course CS-551 (Elements of Artificial Intelligence) taught by Prof. David Crandall. This code was created in collaboration with Raksha Rank and Sreekar Chigurupati.

**Problem Statement:**
It’s not too early to start planning a post-pandemic road trip!  If you stop and think about it, finding the
shortest driving route between two distant places — say, one on the east coast and one on the west coast of
the U.S. — is extremely complicated.  There are over 4 million miles of roads in the U.S. alone, and trying
all possible paths between two places would be nearly impossible.  So how can mapping software like Google
Maps find routes nearly instantly?    
We’ve prepared a dataset of major highway segments of the United States (and parts of southern Canada
and  northern  Mexico),  including  highway  names,  distances,  and  speed  limits;  you  can  visualize  this  as  a
graph  with  nodes  as  towns  and  highway  segments  as  edges.   We’ve  also  prepared  a  dataset  of  cities  and
towns with corresponding latitude-longitude positions.  Find good driving directions between
pairs of cities given by the user.


**Search space**: data and data_gps dataframe
**Successor function**: fetching all the neighbors of the current city, that is checking if the current city is present in column “city_1” or “city_2” assuming that the edges are undirected.

**Segment cost function:**
Here, we need to find a path from start city to end city such that we traverse through the minimum number of segments, i.e cover the minimum number of cities.

Approach:
We are using the Breadth First Search approach. 

Successor function: returns all the neighbours of the current city. For that we traverse through both city_1 and city_2 and check if a direct segment is present between them.
 
For the optimal route based on the number of segments, we are inputting all the neighbours of the current city into the Queue, and pop the neighbouring cities, calculating the path every time, and appending the least path to the final path. 

**Distance cost function:**
Here, we need to find a path from start city to end city such that we cover the minimum distance.

_Approach 1:_
Used the Dijkstra algorithm to find the shortest path from the start city to the end city by maintaining the minimum distance it takes to reach the current city. 
Maintaining a dictionary for visited cities, and assuming the cost for distance of each city from the start city as infinity. Once we visit the city, add it to the visited dictionary and update its distance if it is less than the distance already present. 

_Approach 2:_
Adding a heuristic function to estimate which neighbour to travel next on the basis of the minimum haversine distance from the current city to the end city. 
Whichever neighbour has the least haversine distance to the end city would come up in priority in the Priority queue and that would be selected. 

**Time cost function:**
Here, we use a similar approach as the distance function and optimise the time taken by prioritising on the curr_time.

For minimising the time, we use the same haversine distance heuristic but divide the distance by the speed limit to get it in time format. 

**Delivery cost function:**
Here, we need to find a shortest route in expectation with a certain driver. If the speed limit of the highway is >= 50mph, there is p probability of the package falling. In that case we need to drive to the end of the road and return to the start city and start over. This adds an extra penalty of 2* (troad+ttrip) where ttrip is the time it took to reach from the start till the parent city and troad is the time it takes to travel from parent city to the current city. 

For minimising the delivery time, we use the same haversine distance heuristic but divide the distance by the speed limit to get it in time format. 

While updating the delivery time, we check if the speed limit for that highway is >=50 , we add the penalty time to the original time it would take while travelling through that path. 

**Heuristic function:**
We are using the Haversine  function to estimate the distance between the current city and the end city. Haversine function determines the great circle distance between 2 points given their lat long.

If f(s) is the function that calculates the total distance, g(s) is the total distance travelled till the current city and h(s) will be the expected distance based on our heuristic between the current city and the end city.

_f(s)=g(s)+h(s)_

**Accurate gps:**
When the gps(long lat coords) are missing for any particular city, we would run the accurate gps function and take the gps of its nearest city.
If it happens so that even the nearest city’s gps is not available, we would make it [0,0].


**Problem Statement:** Implement an additional cost-function:statetourshould find the shortest route from thestart city to the end city, but that passes through at least one city in each of the 48 contiguous U.S. states.

**Approach:**
The approach of this problem is similar to travelling politician problem which is also a NP Hard problem. 
Our implementation: 

- From the start city, calculated the destination next state based on the gps coordinates.

- Implemented eline algorithm to find the shortest route between start and the end city. [Reference: https://www.mdpi.com/2220-9964/7/3/115]
- From the 48 states, selected the best city from each state based on the minimal cost.
- Using tsp library, found the path from start city to end city.
- Traced the route using Dijkstra algorithm with the haversine heuristic implementation to return the path travelled, number of segments, distance travelled, time taken and delivery time taken.
