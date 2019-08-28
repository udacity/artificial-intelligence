# util.py
# -------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# util.py
# -------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import sys
import inspect
import heapq, random
import io


class FixedRandom:
    def __init__(self):
        fixedState = (3, (2147483648, 507801126, 683453281, 310439348, 2597246090, \
            2209084787, 2267831527, 979920060, 3098657677, 37650879, 807947081, 3974896263, \
            881243242, 3100634921, 1334775171, 3965168385, 746264660, 4074750168, 500078808, \
            776561771, 702988163, 1636311725, 2559226045, 157578202, 2498342920, 2794591496, \
            4130598723, 496985844, 2944563015, 3731321600, 3514814613, 3362575829, 3038768745, \
            2206497038, 1108748846, 1317460727, 3134077628, 988312410, 1674063516, 746456451, \
            3958482413, 1857117812, 708750586, 1583423339, 3466495450, 1536929345, 1137240525, \
            3875025632, 2466137587, 1235845595, 4214575620, 3792516855, 657994358, 1241843248, \
            1695651859, 3678946666, 1929922113, 2351044952, 2317810202, 2039319015, 460787996, \
            3654096216, 4068721415, 1814163703, 2904112444, 1386111013, 574629867, 2654529343, \
            3833135042, 2725328455, 552431551, 4006991378, 1331562057, 3710134542, 303171486, \
            1203231078, 2670768975, 54570816, 2679609001, 578983064, 1271454725, 3230871056, \
            2496832891, 2944938195, 1608828728, 367886575, 2544708204, 103775539, 1912402393, \
            1098482180, 2738577070, 3091646463, 1505274463, 2079416566, 659100352, 839995305, \
            1696257633, 274389836, 3973303017, 671127655, 1061109122, 517486945, 1379749962, \
            3421383928, 3116950429, 2165882425, 2346928266, 2892678711, 2936066049, 1316407868, \
            2873411858, 4279682888, 2744351923, 3290373816, 1014377279, 955200944, 4220990860, \
            2386098930, 1772997650, 3757346974, 1621616438, 2877097197, 442116595, 2010480266, \
            2867861469, 2955352695, 605335967, 2222936009, 2067554933, 4129906358, 1519608541, \
            1195006590, 1942991038, 2736562236, 279162408, 1415982909, 4099901426, 1732201505, \
            2934657937, 860563237, 2479235483, 3081651097, 2244720867, 3112631622, 1636991639, \
            3860393305, 2312061927, 48780114, 1149090394, 2643246550, 1764050647, 3836789087, \
            3474859076, 4237194338, 1735191073, 2150369208, 92164394, 756974036, 2314453957, \
            323969533, 4267621035, 283649842, 810004843, 727855536, 1757827251, 3334960421, \
            3261035106, 38417393, 2660980472, 1256633965, 2184045390, 811213141, 2857482069, \
            2237770878, 3891003138, 2787806886, 2435192790, 2249324662, 3507764896, 995388363, \
            856944153, 619213904, 3233967826, 3703465555, 3286531781, 3863193356, 2992340714, \
            413696855, 3865185632, 1704163171, 3043634452, 2225424707, 2199018022, 3506117517, \
            3311559776, 3374443561, 1207829628, 668793165, 1822020716, 2082656160, 1160606415, \
            3034757648, 741703672, 3094328738, 459332691, 2702383376, 1610239915, 4162939394, \
            557861574, 3805706338, 3832520705, 1248934879, 3250424034, 892335058, 74323433, \
            3209751608, 3213220797, 3444035873, 3743886725, 1783837251, 610968664, 580745246, \
            4041979504, 201684874, 2673219253, 1377283008, 3497299167, 2344209394, 2304982920, \
            3081403782, 2599256854, 3184475235, 3373055826, 695186388, 2423332338, 222864327, \
            1258227992, 3627871647, 3487724980, 4027953808, 3053320360, 533627073, 3026232514, \
            2340271949, 867277230, 868513116, 2158535651, 2487822909, 3428235761, 3067196046, \
            3435119657, 1908441839, 788668797, 3367703138, 3317763187, 908264443, 2252100381, \
            764223334, 4127108988, 384641349, 3377374722, 1263833251, 1958694944, 3847832657, \
            1253909612, 1096494446, 555725445, 2277045895, 3340096504, 1383318686, 4234428127, \
            1072582179, 94169494, 1064509968, 2681151917, 2681864920, 734708852, 1338914021, \
            1270409500, 1789469116, 4191988204, 1716329784, 2213764829, 3712538840, 919910444, \
            1318414447, 3383806712, 3054941722, 3378649942, 1205735655, 1268136494, 2214009444, \
            2532395133, 3232230447, 230294038, 342599089, 772808141, 4096882234, 3146662953, \
            2784264306, 1860954704, 2675279609, 2984212876, 2466966981, 2627986059, 2985545332, \
            2578042598, 1458940786, 2944243755, 3959506256, 1509151382, 325761900, 942251521, \
            4184289782, 2756231555, 3297811774, 1169708099, 3280524138, 3805245319, 3227360276, \
            3199632491, 2235795585, 2865407118, 36763651, 2441503575, 3314890374, 1755526087, \
            17915536, 1196948233, 949343045, 3815841867, 489007833, 2654997597, 2834744136, \
            417688687, 2843220846, 85621843, 747339336, 2043645709, 3520444394, 1825470818, \
            647778910, 275904777, 1249389189, 3640887431, 4200779599, 323384601, 3446088641, \
            4049835786, 1718989062, 3563787136, 44099190, 3281263107, 22910812, 1826109246, \
            745118154, 3392171319, 1571490704, 354891067, 815955642, 1453450421, 940015623, \
            796817754, 1260148619, 3898237757, 176670141, 1870249326, 3317738680, 448918002, \
            4059166594, 2003827551, 987091377, 224855998, 3520570137, 789522610, 2604445123, \
            454472869, 475688926, 2990723466, 523362238, 3897608102, 806637149, 2642229586, \
            2928614432, 1564415411, 1691381054, 3816907227, 4082581003, 1895544448, 3728217394, \
            3214813157, 4054301607, 1882632454, 2873728645, 3694943071, 1297991732, 2101682438, \
            3952579552, 678650400, 1391722293, 478833748, 2976468591, 158586606, 2576499787, \
            662690848, 3799889765, 3328894692, 2474578497, 2383901391, 1718193504, 3003184595, \
            3630561213, 1929441113, 3848238627, 1594310094, 3040359840, 3051803867, 2462788790, \
            954409915, 802581771, 681703307, 545982392, 2738993819, 8025358, 2827719383, \
            770471093, 3484895980, 3111306320, 3900000891, 2116916652, 397746721, 2087689510, \
            721433935, 1396088885, 2751612384, 1998988613, 2135074843, 2521131298, 707009172, \
            2398321482, 688041159, 2264560137, 482388305, 207864885, 3735036991, 3490348331, \
            1963642811, 3260224305, 3493564223, 1939428454, 1128799656, 1366012432, 2858822447, \
            1428147157, 2261125391, 1611208390, 1134826333, 2374102525, 3833625209, 2266397263, \
            3189115077, 770080230, 2674657172, 4280146640, 3604531615, 4235071805, 3436987249, \
            509704467, 2582695198, 4256268040, 3391197562, 1460642842, 1617931012, 457825497, \
            1031452907, 1330422862, 4125947620, 2280712485, 431892090, 2387410588, 2061126784, \
            896457479, 3480499461, 2488196663, 4021103792, 1877063114, 2744470201, 1046140599, \
            2129952955, 3583049218, 4217723693, 2720341743, 820661843, 1079873609, 3360954200, \
            3652304997, 3335838575, 2178810636, 1908053374, 4026721976, 1793145418, 476541615, \
            973420250, 515553040, 919292001, 2601786155, 1685119450, 3030170809, 1590676150, \
            1665099167, 651151584, 2077190587, 957892642, 646336572, 2743719258, 866169074, \
            851118829, 4225766285, 963748226, 799549420, 1955032629, 799460000, 2425744063, \
            2441291571, 1928963772, 528930629, 2591962884, 3495142819, 1896021824, 901320159, \
            3181820243, 843061941, 3338628510, 3782438992, 9515330, 1705797226, 953535929, \
            764833876, 3202464965, 2970244591, 519154982, 3390617541, 566616744, 3438031503, \
            1853838297, 170608755, 1393728434, 676900116, 3184965776, 1843100290, 78995357, \
            2227939888, 3460264600, 1745705055, 1474086965, 572796246, 4081303004, 882828851, \
            1295445825, 137639900, 3304579600, 2722437017, 4093422709, 273203373, 2666507854, \
            3998836510, 493829981, 1623949669, 3482036755, 3390023939, 833233937, 1639668730, \
            1499455075, 249728260, 1210694006, 3836497489, 1551488720, 3253074267, 3388238003, \
            2372035079, 3945715164, 2029501215, 3362012634, 2007375355, 4074709820, 631485888, \
            3135015769, 4273087084, 3648076204, 2739943601, 1374020358, 1760722448, 3773939706, \
            1313027823, 1895251226, 4224465911, 421382535, 1141067370, 3660034846, 3393185650, \
            1850995280, 1451917312, 3841455409, 3926840308, 1397397252, 2572864479, 2500171350, \
            3119920613, 531400869, 1626487579, 1099320497, 407414753, 2438623324, 99073255, \
            3175491512, 656431560, 1153671785, 236307875, 2824738046, 2320621382, 892174056, \
            230984053, 719791226, 2718891946, 624), None)
        self.random = random.Random()
        self.random.setstate(fixedState)

"""
 Data structures useful for implementing SearchAgents
"""

class Stack:
    "A container with a last-in-first-out (LIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Push 'item' onto the stack"
        self.list.append(item)

    def pop(self):
        "Pop the most recently pushed item from the stack"
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the stack is empty"
        return len(self.list) == 0

class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0

class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

class PriorityQueueWithFunction(PriorityQueue):
    """
    Implements a priority queue with the same push/pop signature of the
    Queue and the Stack classes. This is designed for drop-in replacement for
    those two classes. The caller has to provide a priority function, which
    extracts each item's priority.
    """
    def  __init__(self, priorityFunction):
        "priorityFunction (item) -> priority"
        self.priorityFunction = priorityFunction      # store the priority function
        PriorityQueue.__init__(self)        # super-class initializer

    def push(self, item):
        "Adds an item to the queue with priority from the priority function"
        PriorityQueue.push(self, item, self.priorityFunction(item))


def manhattanDistance( xy1, xy2 ):
    "Returns the Manhattan distance between points xy1 and xy2"
    return abs( xy1[0] - xy2[0] ) + abs( xy1[1] - xy2[1] )

"""
  Data structures and functions useful for various course projects

  The search project should not need anything below this line.
"""

class Counter(dict):
    """
    A counter keeps track of counts for a set of keys.

    The counter class is an extension of the standard python
    dictionary type.  It is specialized to have number values
    (integers or floats), and includes a handful of additional
    functions to ease the task of counting data.  In particular,
    all keys are defaulted to have value 0.  Using a dictionary:

    a = {}
    print a['test']

    would give an error, while the Counter class analogue:

    >>> a = Counter()
    >>> print a['test']
    0

    returns the default 0 value. Note that to reference a key
    that you know is contained in the counter,
    you can still use the dictionary syntax:

    >>> a = Counter()
    >>> a['test'] = 2
    >>> print a['test']
    2

    This is very useful for counting things without initializing their counts,
    see for example:

    >>> a['blah'] += 1
    >>> print a['blah']
    1

    The counter also includes additional functionality useful in implementing
    the classifiers for this assignment.  Two counters can be added,
    subtracted or multiplied together.  See below for details.  They can
    also be normalized and their total count and arg max can be extracted.
    """
    def __getitem__(self, idx):
        self.setdefault(idx, 0)
        return dict.__getitem__(self, idx)

    def incrementAll(self, keys, count):
        """
        Increments all elements of keys by the same count.

        >>> a = Counter()
        >>> a.incrementAll(['one','two', 'three'], 1)
        >>> a['one']
        1
        >>> a['two']
        1
        """
        for key in keys:
            self[key] += count

    def argMax(self):
        """
        Returns the key with the highest value.
        """
        if len(list(self.keys())) == 0: return None
        all = list(self.items())
        values = [x[1] for x in all]
        maxIndex = values.index(max(values))
        return all[maxIndex][0]

    def sortedKeys(self):
        """
        Returns a list of keys sorted by their values.  Keys
        with the highest values will appear first.

        >>> a = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> a['third'] = 1
        >>> a.sortedKeys()
        ['second', 'third', 'first']
        """
        sortedItems = list(self.items())
        compare = lambda x, y:  sign(y[1] - x[1])
        sortedItems.sort(cmp=compare)
        return [x[0] for x in sortedItems]

    def totalCount(self):
        """
        Returns the sum of counts for all keys.
        """
        return sum(self.values())

    def normalize(self):
        """
        Edits the counter such that the total count of all
        keys sums to 1.  The ratio of counts for all keys
        will remain the same. Note that normalizing an empty
        Counter will result in an error.
        """
        total = float(self.totalCount())
        if total == 0: return
        for key in list(self.keys()):
            self[key] = self[key] / total

    def divideAll(self, divisor):
        """
        Divides all counts by divisor
        """
        divisor = float(divisor)
        for key in self:
            self[key] /= divisor

    def copy(self):
        """
        Returns a copy of the counter
        """
        return Counter(dict.copy(self))

    def __mul__(self, y ):
        """
        Multiplying two counters gives the dot product of their vectors where
        each unique label is a vector element.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['second'] = 5
        >>> a['third'] = 1.5
        >>> a['fourth'] = 2.5
        >>> a * b
        14
        """
        sum = 0
        x = self
        if len(x) > len(y):
            x,y = y,x
        for key in x:
            if key not in y:
                continue
            sum += x[key] * y[key]
        return sum

    def __radd__(self, y):
        """
        Adding another counter to a counter increments the current counter
        by the values stored in the second counter.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> a += b
        >>> a['first']
        1
        """
        for key, value in list(y.items()):
            self[key] += value

    def __add__( self, y ):
        """
        Adding two counters gives a counter with the union of all keys and
        counts of the second added to counts of the first.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> (a + b)['first']
        1
        """
        addend = Counter()
        for key in self:
            if key in y:
                addend[key] = self[key] + y[key]
            else:
                addend[key] = self[key]
        for key in y:
            if key in self:
                continue
            addend[key] = y[key]
        return addend

    def __sub__( self, y ):
        """
        Subtracting a counter from another gives a counter with the union of all keys and
        counts of the second subtracted from counts of the first.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> (a - b)['first']
        -5
        """
        addend = Counter()
        for key in self:
            if key in y:
                addend[key] = self[key] - y[key]
            else:
                addend[key] = self[key]
        for key in y:
            if key in self:
                continue
            addend[key] = -1 * y[key]
        return addend

def raiseNotDefined():
    fileName = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print("*** Method not implemented: %s at line %s of %s" % (method, line, fileName))
    sys.exit(1)

def normalize(vectorOrCounter):
    """
    normalize a vector or counter by dividing each value by the sum of all values
    """
    normalizedCounter = Counter()
    if type(vectorOrCounter) == type(normalizedCounter):
        counter = vectorOrCounter
        total = float(counter.totalCount())
        if total == 0: return counter
        for key in list(counter.keys()):
            value = counter[key]
            normalizedCounter[key] = value / total
        return normalizedCounter
    else:
        vector = vectorOrCounter
        s = float(sum(vector))
        if s == 0: return vector
        return [el / s for el in vector]

def nSample(distribution, values, n):
    if sum(distribution) != 1:
        distribution = normalize(distribution)
    rand = [random.random() for i in range(n)]
    rand.sort()
    samples = []
    samplePos, distPos, cdf = 0,0, distribution[0]
    while samplePos < n:
        if rand[samplePos] < cdf:
            samplePos += 1
            samples.append(values[distPos])
        else:
            distPos += 1
            cdf += distribution[distPos]
    return samples

def sample(distribution, values = None):
    if type(distribution) == Counter:
        items = sorted(distribution.items())
        distribution = [i[1] for i in items]
        values = [i[0] for i in items]
    if sum(distribution) != 1:
        distribution = normalize(distribution)
    choice = random.random()
    i, total= 0, distribution[0]
    while choice > total:
        i += 1
        total += distribution[i]
    return values[i]

def sampleFromCounter(ctr):
    items = sorted(ctr.items())
    return sample([v for k,v in items], [k for k,v in items])

def getProbability(value, distribution, values):
    """
      Gives the probability of a value under a discrete distribution
      defined by (distributions, values).
    """
    total = 0.0
    for prob, val in zip(distribution, values):
        if val == value:
            total += prob
    return total

def flipCoin( p ):
    r = random.random()
    return r < p

def chooseFromDistribution( distribution ):
    "Takes either a counter or a list of (prob, key) pairs and samples"
    if type(distribution) == dict or type(distribution) == Counter:
        return sample(distribution)
    r = random.random()
    base = 0.0
    for prob, element in distribution:
        base += prob
        if r <= base: return element

def nearestPoint( pos ):
    """
    Finds the nearest grid point to a position (discretizes).
    """
    ( current_row, current_col ) = pos

    grid_row = int( current_row + 0.5 )
    grid_col = int( current_col + 0.5 )
    return ( grid_row, grid_col )

def sign( x ):
    """
    Returns 1 or -1 depending on the sign of x
    """
    if( x >= 0 ):
        return 1
    else:
        return -1

def arrayInvert(array):
    """
    Inverts a matrix stored as a list of lists.
    """
    result = [[] for i in array]
    for outer in array:
        for inner in range(len(outer)):
            result[inner].append(outer[inner])
    return result

def matrixAsList( matrix, value = True ):
    """
    Turns a matrix into a list of coordinates matching the specified value
    """
    rows, cols = len( matrix ), len( matrix[0] )
    cells = []
    for row in range( rows ):
        for col in range( cols ):
            if matrix[row][col] == value:
                cells.append( ( row, col ) )
    return cells

def lookup(name, namespace):
    """
    Get a method or class from any imported module from its name.
    Usage: lookup(functionName, globals())
    """
    dots = name.count('.')
    if dots > 0:
        moduleName, objName = '.'.join(name.split('.')[:-1]), name.split('.')[-1]
        module = __import__(moduleName)
        return getattr(module, objName)
    else:
        modules = [obj for obj in list(namespace.values()) if str(type(obj)) == "<type 'module'>"]
        options = [getattr(module, name) for module in modules if name in dir(module)]
        options += [obj[1] for obj in list(namespace.items()) if obj[0] == name ]
        if len(options) == 1: return options[0]
        if len(options) > 1: raise Exception('Name conflict for %s')
        raise Exception('%s not found as a method or class' % name)

def pause():
    """
    Pauses the output stream awaiting user feedback.
    """
    print("<Press enter/return to continue>")
    input()


# code to handle timeouts
#
# FIXME
# NOTE: TimeoutFuncton is NOT reentrant.  Later timeouts will silently
# disable earlier timeouts.  Could be solved by maintaining a global list
# of active time outs.  Currently, questions which have test cases calling
# this have all student code so wrapped.
#
import signal
import time
class TimeoutFunctionException(Exception):
    """Exception to raise on a timeout"""
    pass


class TimeoutFunction:
    def __init__(self, function, timeout):
        self.timeout = timeout
        self.function = function

    def handle_timeout(self, signum, frame):
        raise TimeoutFunctionException()

    def __call__(self, *args, **keyArgs):
        # If we have SIGALRM signal, use it to cause an exception if and
        # when this function runs too long.  Otherwise check the time taken
        # after the method has returned, and throw an exception then.
        if hasattr(signal, 'SIGALRM'):
            old = signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.timeout)
            try:
                result = self.function(*args, **keyArgs)
            finally:
                signal.signal(signal.SIGALRM, old)
            signal.alarm(0)
        else:
            startTime = time.time()
            result = self.function(*args, **keyArgs)
            timeElapsed = time.time() - startTime
            if timeElapsed >= self.timeout:
                self.handle_timeout(None, None)
        return result



_ORIGINAL_STDOUT = None
_ORIGINAL_STDERR = None
_MUTED = False

class WritableNull:
    def write(self, string):
        pass

def mutePrint():
    global _ORIGINAL_STDOUT, _ORIGINAL_STDERR, _MUTED
    if _MUTED:
        return
    _MUTED = True

    _ORIGINAL_STDOUT = sys.stdout
    #_ORIGINAL_STDERR = sys.stderr
    sys.stdout = WritableNull()
    #sys.stderr = WritableNull()

def unmutePrint():
    global _ORIGINAL_STDOUT, _ORIGINAL_STDERR, _MUTED
    if not _MUTED:
        return
    _MUTED = False

    sys.stdout = _ORIGINAL_STDOUT
    #sys.stderr = _ORIGINAL_STDERR

