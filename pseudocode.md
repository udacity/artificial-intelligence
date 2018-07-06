
## Naked Twins

The naked twins strategy says that if you have two or more unallocated boxes in a unit and there are only two digits that can go in those two boxes, then those two digits can be eliminated from the possible assignments of all other boxes in the same unit.

This pseudocode is accurate, but it isn't very efficient.  You should discuss the other strategies with your peers to look for more efficient implementations. 

Note: It is best to treat the input to this function as immutable. Mutating the state during execution can cause unexpected results during testing because mutating the input can erase pairs of naked twins before they're discovered. 

---
**function** NakedTwins(_values_) **returns** a dict mapping from Sudoku box names to a list of feasible values  
&emsp;**inputs:**  
&emsp;&emsp;_values_, a dict mapping from Sudoku box names to a list of feasible values  
  
&emsp;_out_ <- **copy**(_values_)  /* make a deep copy */  
&emsp;**for each** _boxA_ in _values_ **do**  
&emsp;&emsp;**for each** _boxB_ of **PEERS**(_boxA_) **do**  
&emsp;&emsp;&emsp;**if** both _values_[_boxA_] and _values_[_boxB_] exactly match and have only two feasible digits **do**  
&emsp;&emsp;&emsp;&emsp;**for each** _peer_ of **INTERSECTION**(**PEERS**(_boxA_), **PEERS**(_boxB_)) **do**  
&emsp;&emsp;&emsp;&emsp;&emsp;**for each** _digit_ of _values_[_boxA_] **do**  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;remove digit _d_ from _out_[_peer_]  
&emsp;**return** _out_  

---
