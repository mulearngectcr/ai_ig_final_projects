# Data Structures and Algorithms: Time Complexity and Asymptotics

## Asymptotic Analysis and Big-O Notation
Big-O notation describes the limiting behavior of an algorithm's execution time or memory requirements as input size $n$ approaches infinity. It defines the formal upper bound (worst-case performance) of algorithmic efficiency:

- **O(1) Constant Time**: Execution time remains independent of input size. Examples include direct array indexing, pushing or popping from a stack, and hash map operations in the absence of collisions.
- **O(log n) Logarithmic Time**: The problem space divides by a constant factor at each step. Examples include Binary Search on sorted arrays and balanced binary search tree operations (AVL, Red-Black trees).
- **O(n) Linear Time**: Execution scales directly in proportion to input elements. Examples include linear search through an array and single traversals of linked lists.
- **O(n log n) Linearithmic Time**: The theoretical lower bound for comparison-based sorting algorithms. Examples include Merge Sort, Heap Sort, and average-case Quick Sort.
- **O(n^2) Quadratic Time**: Typical of nested loops over input collections. Examples include Bubble Sort, Insertion Sort, and Selection Sort.
- **O(2^n) Exponential Time**: Execution doubles with every additional input element, characteristic of naive recursive solutions (e.g., recursive Fibonacci) and brute-force power set exploration.

## Data Structure Performance Trade-offs
Understanding data structures requires evaluating their operational complexities:
- **Arrays**: Provide $O(1)$ random access by index via contiguous memory allocation, but require $O(n)$ time for arbitrary insertions and deletions due to element shifting.
- **Linked Lists**: Support $O(1)$ insertions and deletions once node references are held, but lack random access, requiring $O(n)$ traversal time.
- **Hash Tables**: Achieve expected $O(1)$ time for search, insertion, and deletion, though heavy collisions can degrade performance to $O(n)$.
- **Graph Traversals**: Breadth-First Search (BFS) and Depth-First Search (DFS) visit every vertex and edge, yielding an optimal runtime of $O(V + E)$ when using adjacency list representations.
