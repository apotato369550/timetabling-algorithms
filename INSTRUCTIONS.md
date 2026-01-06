What my algorithm does is that it takes a bunch of classes a student wants to enroll in and generates all possible schedules that fit certain constraints. It works pretty well. It uses recursion and some other stuff.

I initially built it for my OOP class, hence the need to apply OOP principles. I used abstract classes, inheritance, and encapsulation. But I don't think that's as necessary anymore for this particular project

I want to develop another feature/algorithm that instead solves the following problem:
Given a number of professors who are capable of teaching certain subjects and who are available on certain times on certain days, and given a list of subjects students need to take per course, generate blocksection schedules given these constraints.

The algorithm should be able to generate all possible schedules that fit the constraints. And should have variations where:
1. The schedules are already given, and it's just a matter of assigning professors/instructors to the schedules, minimizing unassigned profs, maximizing prof availability, and as much as possible fulfilling the subjects.
2. The schedules are not given, and it's a matter of generating schedules that fit the constraints, minimizing unassigned profs, maximizing prof availability, and as much as possible fulfilling the subjects.
3. Among other stuff


I'm still in the process of formalizing the problem itself, but not only could it make as a useful tool, I think the algorithm that could be developed would be beautiful.

My intuition tells me that the algorithm might be, in its own way, a unique contribution in that it might be research-papereable (thesisable hehe). I want ur thoughts. (be nice lol)

In this directory is also a file called SchedulerEngine.js - the engine itself

First concrete steps:
1. Extract the algorithm from the scheduler engine and convert it into Python
2. Create a CLI tool & console menu to run tests on the algorithm
3. Reason out & construct the other variation of the algorithm I just mentioned
4. Create tests & validate the algorithm