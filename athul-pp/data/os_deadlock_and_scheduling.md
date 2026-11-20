# Operating Systems: Deadlock and CPU Scheduling

## Deadlock Concepts and Conditions
A deadlock in an operating system is a state where a set of processes are blocked because each process is holding a resource and waiting for another resource acquired by some other process. Four necessary conditions (Coffman conditions) must hold simultaneously for a deadlock to occur:

1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode; only one process can use the resource at any given time.
2. **Hold and Wait**: A process must currently hold at least one resource and simultaneously request additional resources that are currently held by other processes.
3. **No Preemption**: Resources cannot be preempted; a resource can only be released voluntarily by the process holding it after that process has completed its task.
4. **Circular Wait**: A closed chain of processes exists such that each process holds at least one resource needed by the next process in the cycle.

Deadlock handling strategies include **prevention** (invalidating at least one of the four conditions), **avoidance** (such as Dijkstra's Banker's Algorithm, which grants resource requests only if the system remains in a safe state), **detection and recovery** (using Resource Allocation Graphs and terminating processes or preempting resources), and the **Ostrich algorithm** (ignoring the problem if deadlocks are rare).

## CPU Scheduling Algorithms
CPU scheduling decides which process in the ready queue is allocated the CPU core:
- **First-Come, First-Served (FCFS)**: Non-preemptive scheduling based on arrival order. Simple, but suffers from the convoy effect where short processes wait behind long CPU-burst tasks.
- **Shortest Job First (SJF)**: Selects the process with the shortest next CPU burst. Provably optimal for minimizing average waiting time, though future burst lengths must be estimated.
- **Round Robin (RR)**: Preemptive scheduling designed for time-sharing systems. Each process gets a fixed slice of time called a time quantum. Performance depends heavily on quantum length.
- **Priority Scheduling**: Allocates CPU according to priority ranks. Preemptive or non-preemptive; prone to starvation, which is mitigated via aging (gradually increasing waiting process priorities).
