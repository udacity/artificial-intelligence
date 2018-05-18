
# Overview

Heuristics derived from the planning graph are defined in Chapter 10 of Artificial Intelligence: a Modern Approach (AIMA) 3rd edition (Chapter 11 in the 2nd edition–linked in the project readme).  The pseudocode below provides functional descriptions of the three planning graph heuristics that must be implemented for this project.

Note that the pseudocode is _accurate_, but it isn't necessarily _efficient_ to compute them this way.  The most significant inefficiency is that each function starts by building a _complete_ planning graph until it levels off.  However, in many cases the heuristics can be computed before the full planning graph is built.  See the last section below for an example of changing the pseudocode for the MaxLevel heuristic so that it incrementally constructs the planning graph, cutting the runtime for that heuristic on most problems in half.  You should discuss the other heuristics below with your peers to look for more efficient implementations.


## LevelCost
The level cost is a helper function used by MaxLevel and LevelSum. The level cost of a goal is equal to the level number of the first literal layer in the planning graph where the goal literal appears.

---
**function** LevelCost(_graph_, _goal_) **returns** a value  
&emsp;**inputs:**  
&emsp;&emsp;_graph_, a leveled planning graph  
&emsp;&emsp;_goal_, a literal that is a goal in the planning graph  
  
&emsp;**for each** _layer<sub>i_ in _graph.literalLayers_ **do**  
&emsp;&emsp;**if** _goal_ in _layer<sub>i_ **then return** i  

---

## MaxLevel

> The max-level heuristic simply takes the maximum level cost of any of the goals; this is admissible, but not necessarily accurate.

&emsp;—AIMA Chapter 10

---
**function** MaxLevel(_graph_) **returns** a value  
&emsp;**inputs:**  
&emsp;&emsp;_graph_, an initialized (unleveled) planning graph  
  
&emsp;_costs_ = []  
&emsp;_graph_.fill()  _/* fill the planning graph until it levels off */_  
&emsp;**for each** _goal_ in _graph.goalLiterals_ **do**  
&emsp;&emsp;_costs_.append(**LevelCost**(_graph_, _goal_))  
&emsp;**return max**(_costs_)  

---

## LevelSum

> The level sum heuristic, following the subgoal independence assumption, returns the sum of the level costs of the goals; this can be inadmissible but works well in practice for problems that are largely decomposable.

&emsp;—AIMA Chapter 10

---
**function** LevelSum(_graph_) **returns** a value  
&emsp;**inputs:**  
&emsp;&emsp;_graph_, an initialized (unleveled) planning graph  
  
&emsp;_costs_ = []  
&emsp;_graph_.fill()  _/* fill the planning graph until it levels off */_  
&emsp;**for each** _goal_ in _graph.goalLiterals_ **do**  
&emsp;&emsp;_costs_.append(**LevelCost**(_graph_, _goal_))  
&emsp;**return sum**(_costs_)  

---

## SetLevel

> The set-level heuristic finds the level at which all the literals in the conjunctive goal appear in the planning graph without any pair of them being mutually exclusive.

&emsp;—AIMA Chapter 10

---
**function** SetLevel(_graph_) **returns** a value  
&emsp;**inputs:**  
&emsp;&emsp;_graph_, an initialized (unleveled) planning graph  
  
&emsp;_graph_.fill()  _/* fill the planning graph until it levels off */_  
&emsp;**for** _layer<sub>i_ in _graph.literalLayers_ **do**  
&emsp;&emsp;_allGoalsMet_ <- _true_  
&emsp;&emsp;**for each** _goal_ in _graph.goalLiterals_ **do**  
&emsp;&emsp;&emsp;**if** _goal_ not in _layer<sub>i_ **then** _allGoalsMet_ <- _false_  
&emsp;&emsp;**if** not _allGoalsMet_ **then** continue  
  
&emsp;&emsp;_goalsAreMutex_ <- _false_  
&emsp;&emsp;**for each** _goalA_ in _graph.goalLiterals_ **do**  
&emsp;&emsp;&emsp;**for each** _goalB_ in _graph.goalLiterals_ **do**  
&emsp;&emsp;&emsp;&emsp;**if** _layer<sub>i_.isMutex(_goalA_, _goalB_) **then** _goalsAreMutex_ <- _true_  
&emsp;&emsp;**if** not _goalsAreMutex_ **then return** _i_

---

## Improving Efficiency

These heuristics can be made _much_ more efficient by incrementally growing the graph rather than building until it levels off. A straightforward implementation of the alternate MaxLevel pseudocode shown below is at least 2x faster than the simple version above.

---
**function** MaxLevel(_graph_) **returns** a value  
&emsp;**inputs:** _graph_, an initialized (unleveled) planning graph  
  
&emsp;_i_ <- 0  
&emsp;**loop until** _graph_.isLeveled **do**  
&emsp;&emsp;_allGoalsMet_ <- true  
&emsp;&emsp;**for each** _goal_ in _graph.goalLiterals_ **do**  
&emsp;&emsp;&emsp;**if** _goal_ not in _graph_.getLastLiteralLayer() **then** _allGoalsMet_ <- false  
&emsp;&emsp;**if** _allGoalsMet_ **then return** _i_  
&emsp;&emsp;**else** _graph_.extend() /* add the next literal layer */  
&emsp;&emsp;_i_ <- _i_ + 1  

---
