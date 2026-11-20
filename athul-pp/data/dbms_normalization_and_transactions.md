# Database Management Systems: Normalization and Transactions

## Relational Normalization
Normalization is the process of organizing database attributes and tables to eliminate data redundancy and prevent data anomalies (insertion, update, and deletion anomalies) while preserving data integrity:

1. **First Normal Form (1NF)**: Requires that each column contains atomic (indivisible) values and each row is uniquely identifiable via a primary key. No repeating groups or arrays.
2. **Second Normal Form (2NF)**: Must satisfy 1NF and contain no partial dependencies. Every non-prime attribute must be fully functionally dependent on the entire candidate key rather than any proper subset of it.
3. **Third Normal Form (3NF)**: Must satisfy 2NF and have no transitive functional dependencies. Non-prime attributes must not depend on other non-prime attributes; for any dependency X -> Y, X is a super key or Y is a prime attribute.
4. **Boyce-Codd Normal Form (BCNF)**: A stricter variant of 3NF where for every non-trivial functional dependency X -> Y, determinant X must strictly be a super key.

## Transaction Processing and ACID Properties
A transaction is a logical unit of database operations that must satisfy ACID properties:
- **Atomicity**: The "all-or-nothing" rule. Either all transaction operations execute successfully, or the entire transaction is rolled back upon failure.
- **Consistency**: The database must transition from one valid state satisfying all schema integrity constraints to another valid state.
- **Isolation**: Concurrent transactions must execute without interfering with one another. Intermediate uncommitted changes remain invisible to other operations.
- **Durability**: Once a transaction commits, its modifications are permanently recorded in non-volatile storage and survive system crashes.

## Concurrency Control and Locking
To ensure serializability in concurrent execution, database engines use locking protocols. The **Two-Phase Locking (2PL)** protocol guarantees conflict serializability through two phases:
- **Growing Phase**: The transaction may acquire shared (read) or exclusive (write) locks but cannot release any lock.
- **Shrinking Phase**: Once any lock is released, the transaction enters this phase and can only release existing locks without obtaining new ones.
