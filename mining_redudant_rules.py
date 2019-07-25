import itertools  # For generating all possible subsets
import collections  # For sorting the association rules by descending order of confidence

# Open the file containing the dataset
#setwd("~/data mining/sheet2")

dataset = open("mobile.txt", "r+")
#dataset <- open("~/data mining/lab1/mobile.txt")
#dataset<-open("/home/SS/15PW/15pw09/data mining/lab1/apriori.py","r+")
# Parameters for the association analysis
minsup = 0.03
# minsup=0.03
minconf = 0.4
#minconf=0.5

social_activity=["Meeting","Lecture","Lunch"]
#
# Read the dataset line by line and store the transactions in a dictionary
#
transactions = {}

# Store the set of possible unique items
unique_items = set()

for line in dataset:
    # Remove trailing newline
    line = line.strip()

    # Separate into tid and items
    separated = line.split("\t")

    # Get the list of items in the basket
    if len(separated) == 1:  # Empty transaction
        items = []
    else:
        items = separated[1].split(",")
        for item in items:
            if item not in unique_items:
                unique_items.add(item)

    # Get the Transaction ids
    tid = separated[0]
    # Remove the trailing '.' in tids and make them numeric
    tid = int(tid[0:-1])

    # Insert into the dict
    transactions[tid] = set(sorted(items))

#
# Print input characteristics
#
print("----Unique items: ")
print(unique_items)
print("----Minimum support = " + str(minsup))
print("----Minimum confidence = " + str(minconf))

#
# Start generating and pruning frequent itemsets
# Current stop condition: (level == number of unique items)
# Better stop condition?
#
print("\n\n----------------------------Mining Frequent Itemsets:")
frequent_itemsets = dict()
total_transactions = len(transactions)

# Let 'level' indicate the level of itemset generation
level = 1
# Let this be the list of frequent itemsets in the previous level
# to generate for current level
previous = []

while level <= len(unique_items):
    # In 'level', candidate itemsets containing 'level' items will be generated
    #     from frequent itemsets of previous level
    # Let each itemset be a tuple

    # Maintain candidate frequent itemsets for each level along with their support
    # to find frequent itemsets
    candidates = dict()

    if level == 1:
        # Starting level, no frequent itemsets present
        # Add all single items
        for item in unique_items:
            # Calculate support count by scanning all the transactions
            support = 0
            for tid in transactions:
                if item in transactions[tid]:
                    support = support + 1

            # Calculate support by dividing the support count with the total number of transactions
            support = support / float(total_transactions)

            # Add the item and its support, if support satisfies minsup
            if support >= minsup:
                candidates[(item,)] = support

        # Set the current level's frequent itemsets
        previous = list(candidates.keys())

        # Add the current frequent itemsets to already calculated ones
        for item in candidates:
            frequent_itemsets[item] = candidates[item]
    else:
        # Higher levels, use the frequent itemsets of previous level to generate new itemsets
        if len(previous) == 0:
            # In higher levels, if the previous level had no frequent itemsets,
            # no more frequent itemsets will be generated
            # So stop here
            print("\n\n******************Stopping at level = " + str(level))
            break
        # First (level-1) elements need to be same in order to combine them
        # Consider pairs of frequent itemsets
        for i in range(0, len(previous)):
            for j in range(i + 1, len(previous)):
                if previous[i][0:level - 2] == previous[j][0:level - 2]:
                    # Same n-1 elements, combine them to get level-itemsets
                    temp = list(previous[i][0:level - 2])
                    temp.append(previous[i][-1])
                    temp.append(previous[j][-1])
                    candidates[tuple(sorted(temp))] = 0

        #
        # Prune the candidates
        # Generate all possible subsets, if any subset is not frequent,
        #   do not consider the current candidate for scanning the db
        #
        for candidate in list(candidates.keys()):
            pruned = False
            # Generate subsets of all lengths
            for i in range(1, len(candidate)):
                # Check for already pruned candidate
                if pruned:
                    break
                subsets = list(itertools.combinations(candidate, i))
                for subset in subsets:
                    subset = tuple(sorted(subset))
                    if subset not in frequent_itemsets:
                        # Remove the current candidate from the list of
                        # candidates to be scanned in the transaction db
                        del candidates[candidate]
                        pruned = True
                        print("Candidate " + str(candidate) + " was pruned off " +
                              "because its subset " + str(subset) +
                              " is not frequent")
                        break

        # Now, scan the transaction db to find support
        for candidate in candidates:
            for tid in transactions:
                if set(candidate).issubset(transactions[tid]):
                    candidates[candidate] = candidates[candidate] + 1
            candidates[candidate] = candidates[candidate] / float(total_transactions)

        # Now, add only those candidates who not meet the minsup requirements to the running list of frequent itemsets
        previous = []
        for candidate in candidates:
            if candidates[candidate] >= minsup:
                frequent_itemsets[candidate] = candidates[candidate]
                previous.append(candidate)

    # Increment to next level
    level = level + 1

#
# Pretty print frequent itemsets
#
print("\n\n------------------Frequent itemsets :")
print("----No. of frequent itemsets = " + str(len(frequent_itemsets)))
for freq_itemset in frequent_itemsets:
    output = ""
    for item in freq_itemset:
        output = output + item + ", "
    output = output[0:-2]

    # Also print the support
    output = output + ": (" + str(round(frequent_itemsets[freq_itemset], 2)) + ")"

    print(output)

#
# Mine association rules
#
association_rules = {}
for itemset in frequent_itemsets:
    sitemset = set(itemset)
    # Generate all possible combinations
    for n in range(1, len(sitemset)):
        # Combinations of n items
        combinations = list(itertools.combinations(sitemset, n))
        # For every combination, mine the association rule
        # Find confidence
        # If confidence satisfies minconf, add it to the list of good association rules
        for left in combinations:
            left = tuple(sorted(left))
            right = tuple(sorted(sitemset.difference(left)))
            confidence = frequent_itemsets[itemset] / frequent_itemsets[left]
            if confidence >= minconf:
                association_rules[(left, right)] = confidence

# Sort by decreasing confidence
association_rules = collections.OrderedDict(sorted(association_rules.items(), key=lambda t: t[1], reverse=True))

#
# Pretty print the association rules
#
print("\n\n------------------Association rules in order of decreasing confidence: ")
a_rules=[]
count=0
for rule in association_rules:
    # Left side of the association rules
    output = ""
    out_cpy=""
    for item in rule[0]:
        output = output + item + ", "
    output = output[0:-2]  # Remove the last comma?

    output = output + " --> "
    #print(output)
    # Right side of the association rules
    for item in rule[1]:
        if(item=="reject" or item=="accept" or item=="missed"):
            #output = output + item + ", "
            out_cpy=output+item
            out_cpy = out_cpy + " (" + str(round(association_rules[rule], 2)) + ")"
            count=count+1
    # out_cpy = out_cpy[0:-1]  # Remove the last comma?
    #print(out_cpy)

    # Also print the confidence
    # out_cpy = out_cpy + " (" + str(round(association_rules[rule], 2)) + ")"

    #print(output)
    if(out_cpy!=""):
        #print (out_cpy)
        if(count==1):
            a_rules=[out_cpy]
        else:
            a_rules.append(out_cpy)
            #a_rules=a_rules+out_cpy+"\n"

for i in a_rules:
    print(i)

non_redundant=[]
super1=[]
count1=0
count2=0
subset=[]  #to store the subset that has > than min confidence
for i in a_rules:
    left=i.split("-->")
    if(left[0].__contains__(",")):
        if(count2==0):
            super1=[i]
            count2=count2+1
        else:
            super1.append(i)
    else:
        #print (left)
        v=[left[0],left[1][0:7]]
        if(count1==0):
            non_redundant=[i]
            count1=count1+1
            subset=[v]
        else:
            non_redundant.append(i)
            subset.append(v)

            #subset[0]=subset[0].replace(" ","")
            #subset[1]=subset[1].replace(" ","")
#subset[0]=activity subset[1]=behaviour

#print(len(subset))
print("\n")
print("Non_redundant Rules:\n")
for i in range(len(subset)):
    #subset[0][1])
    subset[i][1]=subset[i][1].replace(" ","")
    
for i in range(len(subset)):
        subset[i][0]=subset[i][0][:-1]

#print(subset)

for i in subset:
    print(i[0]+"-->"+i[1])

if(len(subset)>0):
    set0=""
    set1=[]
    set_2=[]
    count=0
    for i in super1:
        left=i.split("-->")
        set0=left[0].split(",")
        set1=[set0[0],set0[1],left[1][0:7]]
        #if(cpunt==0):
         #   set=[]
        #print(str(left[0].split(","))+(left[1][0:7]))
        if(count==0):
            set_2=[set1]
            count=count+1
        else:
            set_2.append(set1)
    #print(set_2)
    
    final=[]
    count=0
    
    for i in range(len(set_2)):
        set_2[i][0]=set_2[i][0].replace(" ","")
        set_2[i][1]=set_2[i][1].replace(" ","")
        set_2[i][2]=set_2[i][2].replace(" ","")
        
    #print(set_2)
    #print("@@")
    final=[]
    for i in range(len(subset)):
        count=0
        for j in set_2:
            #print(i)
            #print(j)
            if(subset[i][0]==j[0] or subset[i][0]==j[1]):
                if(subset[i][1]!=j[2]):
                        if(count==0):
                           final=[j]
                           count=count+1
                        else:
                            final.append(j)
            else:
                if(count==0):
                    final=[j]
                    count=count+1
                else:
                    final.append(j)
            set_2=final
            
    #print(set_2)
    
    for i in range(len(set_2)):
        print(set_2[i][0]+","+set_2[i][1]+"-->"+set_2[i][2])
        #print(i)    