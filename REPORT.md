Langauge: Python
Version: 3.13

| **n** | **m** | **comparisons** | **wall time (s)** | **output tuples** |
|------:|------:|----------------:|------------------:|------------------:|
| 1,000  | 1,000  | 1,000,000     | 0.6196    | 1,000  |
| 2,000  | 2,000  | 4,000,000     | 2.5286    | 2,000  |
| 4,000  | 4,000  | 16,000,000    | 11.3385   | 4,000  |
| 8,000  | 8,000  | 64,000,000    | 44.1906   | 8,000  |
| 16,000 | 16,000 | 256,000,000   | 175.4136  | 16,000 |
| 32,000 | 32,000 | 1,024,000,000 | 703.4049  | 32,000 |
| 64,000 | 64,000 | 4,096,000,000 | 2664.9322 | 64,000 |


1. The relationshop between n and m and the comparison count is clearly defined as:
Comparisons = n * m. For example 1000 x 1000 = 1,000,000 comparisons. This relationship is linear and can be observed in the table above.

This happens becaise the join implemention comapres every tuple in relation R with every tuple in relation S. Therefore, the number of comparisons is equal to the product of the sizes of the two relations.

2. Plotting the time against n on a log-log axis gives a slope of approximately 2, more speicfically 2.014.
This tells use that the running time grows quadratically, and therefore the algorithim has a time complexity of O(n^2), which matches what we see in comparisons.  It also shows that everytime size doubles of both n and m, the time taken increases by a factor of 4, which is consistent with quadratic growth.


3. 
select[b>=0](R)
| n     | comparisons | wall time (s) | output tuples |
|------:|------------:|--------------:|--------------:|
| 1000  | 1000        | 0.0005        | 1000          |
| 2000  | 2000        | 0.0010        | 2000          |
| 4000  | 4000        | 0.0022        | 4000          |
| 8000  | 8000        | 0.0039        | 8000          |
| 16000 | 16000       | 0.0080        | 16000         |
| 32000 | 32000       | 0.0154        | 32000         |
| 64000 | 64000       | 0.0314        | 64000         |

project[a](R)
| n     | wall time (s) | output tuples |
|------:|--------------:|--------------:|
| 1000  | 0.0022        | 1000          |
| 2000  | 0.0005        | 2000          |
| 4000  | 0.0007        | 4000          |
| 8000  | 0.0017        | 8000          |
| 16000 | 0.0048        | 16000         |
| 32000 | 0.0146        | 32000         |
| 64000 | 0.0169        | 64000         |

After ploting this it seems that the running time of select and project is linear. This is different then join due to the passes over each relation once, while join requires a nested loop over each relation as it has to compare every tuple in R with every tuple in S.

4. 
At 64k tuples the join took 2664.9322 seconds. 
To calculate the time to do 1 million joins we can calulcate it as the following:
1000000 / 64000 = 15.625, since growing time is about n^2, 15.625^2 = 244.140625. To find the new time we can do:
2664.9322 * 244.140625 = 650618.2129 seconds.

Convertint this to hours is 180.7272814 hours, or about 7.53 days.


5.
running new matches:
match=0  comps=32000000  time=20.3567  out=0
match=1  comps=32000000  time=20.4459  out=4000
match=2  comps=32000000  time=21.0358  out=8000

This shows that as match rate increases, the number of comparisons stays the same but as the output tuples increases, so does the time. The comparisons stay the same because as the nested loop in join still coimpares every tuple in R with every tuple in S, whether it is a match or not.

Wall time did slightly increase as match rate increased, which does make sense as the system must now store more tuples in memory in the output after completing the join, adding time while the amount of comparisons stays the same.

6. To make a million tuple join feasible, we would need to optimize the join algorithm to reduce the number of comparisons or make it more efficient. One idea I can across while researching is to use a hash join, that would help deal with large unsorted datasets, making us go from a O(n^2) to a O(n) time complexity, which would be a massive improvement, taking us from 7.5 days to a few hours at max.
