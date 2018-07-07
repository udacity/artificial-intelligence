
## PlanningGraph
A planning graph consists of a sequence of "layers" alternating between `LiteralLayer` instances and `ActionLayer` instances. Each layer is a collection of literals or actions that _might_ be possible at that level of the planning graph. The implementation used in this project provides a `Set` interface for the collection in each layer, so the layers are iterable (the iterator yields the individual nodes) and support efficient set operations (union, intersection, inclusion, etc.).

```
(ActionLayer_Null) -> LiteralLayer_0 -> ActionLayer_0 -> LiteralLayer_1 -> ActionLayer_1 -> ... -> LiteralLayer_N
    empty               Literal_0         Action_0         Literal_0         Action_0                Literal_0
                        Literal_1         Action_1         Literal_1         Action_1                Literal_1
                        Literal_2                          Literal_2         Action_3                Literal_2
                                                           Literal_3                                 Literal_3
                                                                                                        ....
                                                                                                     Literal_k
```

#### `fill() : PlanningGraph`
    The fill method extends the planning graph until it is leveled, or until a specified number of levels have been added. This function simply calls the `_extend()` method in a loop until the terminating condition is satisfied.

#### `_extend() : None`
    The extend method grows the planning graph by adding both a new action layer and a new literal layer (a planning graph can never end on an action layer). When the planning graph will be used by a search heuristic, it is usually more efficient to construct the planning graph layer-by-layer because it stops immediately when the heuristic value is known rather than building the full graph until it levels off.


### Examples:

#### Iterating over layers in the planning graph
(Note: This example function only illustrates the class interface; it not useful in the project.)
```
class PlanningGraph:
    ...
    def layerloop(self):
        for ll in self.literal_layers:
            print(ll)
        for al in self.action_layers:
            print(al)
```


## LiteralLayer
This layer represents a collection of symbolic expressions identical to those in a planning problem instance. The class implements the `Set` interface--so the elements are iterable, the object is hashable, and it support efficient set operations (intersection, difference, union, contains, etc.). The class automatically manage mutual exclusion links between nodes and references from each node to its parents in the preceding layer and children in the following layer.

#### parent_layer : ActionLayer
A reference to previous layer in the planning graph.

#### parents : dict
A dict mapping from each node in the layer to a set of parent nodes in the previous layer. For literal layers, the parents of each literal node L are the actions in the previous layer that includes L as an effect.

#### children : dict
A dict mapping from each node in the layer to a set of children nodes in the next layer. For literal layers, the children of each literal node L are the actions in the next layer that include L as a precondition.

#### is_mutex() : bool
Given two literal expressions, this function returns True if there is a mutual exclusion between them in this literal layer, and False otherwise.

### Examples:

#### LiteralLayer children vs action preconditions
This example demonstrates how you could add a method to verify that the child nodes of each literal L in the layer are actions that have L as a precondition. (Note: This example function only illustrates the class interface; it not useful in the project.)
```
class LiteralLayer:
    ...
    def test_children(self):
        for literal in self:
            assert all(literal in action.preconditions for action in self.children[literal])

            for action in self.children[literal]:
                print(action)
```

#### LiteralLayer parents vs action effects
This example demonstrates how you could add a method to verify that the parent nodes of each literal L in the layer are actions that have L as an effect. (Note: This example function only illustrates the class interface; it not useful in the project.)
```
class ActionLayer:
    ...
    def test_parents(self):
        for literal in self:
            assert all(literal in action.effects for action in self.children[literal])

            for action in self.parents[literal]:
                print(action)
```


## ActionLayer

The nodes in action layers wrap the action expressions from a planning problem instance to provide a uniform API for planning graph nodes by aliasing the preconditions and effects of each action to match the parents and children attributes of literal layer nodes. The class implements the `Set` interface--so the elements are iterable, the object is hashable, and it support efficient set operations (intersection, difference, union, contains, etc.). The class automatically manage mutual exclusion links between nodes and references from each node to its parents in the preceding layer and children in the following layer.

#### parent_layer : LiteralLayer
A reference to previous layer in the planning graph.

#### parents : dict
A dict mapping from each node in the layer to a set of parent nodes in the previous layer. For action layers, the parents of each action node N are the literals in the previous layer that are preconditions for action N.

### children : dict
A dict mapping from each node in the layer to a set of children nodes in the next layer. For action layers, the children of each action node N are the literals in the next layer that are effects for action N.

#### is_mutex() : bool
Given two actions, this function returns True if there is a mutual exclusion between them in this action layer, and False otherwise.


### Examples:

#### ActionLayer children vs action effects
This example demonstrates how you could add a method to verify that the child nodes of each action N in the layer are equivalent to the effects of the action. (Note: This example function only illustrates the class interface; it not useful in the project.)
```
class ActionLayer:
    ...

    def check_children(self):
        for action in self:
            assert action.effects == self.children[action]

            for literal in self.children[action]:
                print(literal)
```

#### ActionLayer parents vs action preconditions
This example demonstrates how you could add a method to verify that the parent nodes of each action N in the layer are equivalent to the preconditions of the action. (Note: This example function only illustrates the class interface; it not useful in the project.)
```
class ActionLayer:
    ...

    def check_parents(self):
        for action in self:
            assert action.preconditions == self.parents[action]

            for literal in self.parents[action]:
                print(literal)
```
