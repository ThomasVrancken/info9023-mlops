# INFO9023 - Machine Learning Systems Design

The course of Machine Learning System Designs (or MLOps) aims at enabling students to truly build fully functional "user-ready" ML systems. It will look at the whole lifecycle of building a real world ML application. At the end of the course, students will be familiar with key tools and frameworks of MLOps.

We are in the early days of the AI revolution, which is expected to bring a large impact to many industries. There is a large demand for skilled engineers who are able to build ML systems.

Bringing a Machine Learning application to production requires many more efforts than solely the ML model development. Famously, there is a large hidden technical debts in designing and implementing all the components coming around your model.

This course and material contained in this repo aims at closing that technical debt by providing essential tools and best practices in MLOps.

## Logistic
- **Teaching Staff**: 
  - Thomas Vrancken (Instructor): t.vrancken@uliege.be
  - Matthias Pirlet (Teaching Assistant): Matthias.Pirlet@uliege.be 
- **Class time & place**: Classes are held from **9:00** to **12:30** every Monday in B37 S.42 (-1/42) [Liège Sart-Tilman - Polytech]
  - Note that it was changed from the original room B28 R.75 (0/75) as we were a too large group for it.
  - The new room is *not available on the 04/03/2024*. That day we will be back in room B28 R.75 (0/75).- **Support**: You can ask any question by **email**, during (or after) **classes** or in person during **open office hours** every Monday till 18:00 in office 77B (building B28).
- **Communication**: Main communication point will be Discord ([link](https://discord.gg/4jsySN4z)). Official communication might also come by email.

## Agenda

Note that links to the lecture and labs slides will always be provided shortly before the actual date.

| Date       | Week #     | Sprint #       | Description                                                 | Material (gradually added)                    |
|------------|------------|----------------|-------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| 05/02/2024 | W0         | Sprint 0       | Course introduction                                         | [lecture slides](lectures/00_course_introduction.pdf)                                                                  |
| 12/02/2024 | W1         | Sprint 1       | Use case definition                                         | [lecture slides](lectures/01_use_case_definition.pdf)                                                                  |
| 19/02/2024 | W2         | Sprint 1       | Project organisation<br/> Lab git code versioning           | [lecture slides](lectures/02_project_organization.pdf) <br/> [labo slides](labs/02_lab_git_code_versioning.pdf)              |
| 26/02/2024 | W3         | Sprint 2       | Data processing<br/> Lab YData-profiling                    | [lecture slides](lectures/03_data_preparation.pdf) <br/> [labo slides](labs/03_lab_ydata_profiling.pdf) - [labo notebook](labs/ydata_tuto.ipynb) |
| 04/03/2024 | W4         | Sprint 2       | Model development              (_class in B28 R.75 (0/75)_) | [lecture slides](lectures/04_model_experimentation_and_containerisation.pdf) <br/> [labo folder](labs/04_containerisation)    | 
| 11/03/2024 - 18/03/2024 | [MS 1 presentations](#project)                                              |
| 11/03/2024 | W5         | Sprint 3       | API implementation      |                |
| 18/03/2024 | W6         | Sprint 3       | Model serving & Cloud infrastructure                        |                           |
| 25/03/2024 | W7         | Sprint 4       | Serving & training optimisation      |           |
| 01/04/2024 | _No Class_ | _No Class_     | _No Class_          | _No Class_                          |
| 08/04/2024 | W8         | Sprint 4       | Model Pipeline                                              |                                               |
| 15/04/2024 - 17/04/2024 | (To be confirmed !) [MS 2 presentations](#project)                                              |
| 15/04/2024 | W9         | Sprint 5       | Monitoring & dashboarding                                   |                                               |
| 22/04/2024 | _No Class_ | _No Class_     | _No Class_                                                  | _No Class_                                    |
| 29/04/2024 | _No Class_ | _No Class_     | _No Class_                                                  | _No Class_                                    |
| 06/05/2024 | W10        | Sprint 5       | CICD                                                        |                                               |
| 13/05/2024 | W11        | Closing sprint | Ethics & Real world use cases                               |                                               |
| (Dates to be confirmed) | [MS 3 presentations](#project)                                              |

## Course culture

#### Pillars
1. **Relevant**: Focused on core concepts of building ML applications. Tailored choice of current best practices.
2. **Practical**: Concrete Labs, resources, real life examples, time to experiment, support line, …
3. **Engagin**: Interactive class session. Healthy tempo (break out exercises, QA, …). … And lots of memes.

#### Learning Streams
There are 3 points of learnings for students following this course:
1. **Lectures**: Present theoretical concepts and practices. Usually the first part of each class.
2. **Labs**: Labs are there to learn how to use key tools widely used to build ML systems. They've been cherry picked based on usability, performance, popularity and accessibility. 
3. **Project**: You will apply the theoretical and technical learnings in one large group project. You will build a ML application in an engaging way - you're in the driving seat.

## Topics covered

You can find a full view of the topics in the "`Course Introduction`" lecture.

Here is an overview of how the sprints are organised:

![Topics overview](figures/classes_overview.png)

## Project 

All the project info can be found in the [project/project_description.pdf](project/project_description.pdf) document.

Important to highlight that you are the **decision makers for the design of your project** :open_hands: Design it in a coherent way. Spend time on features that **make sense**. Don't see the workpackages as a long checklist, rather on possible points to implement.

For example, if you implement a computer vision model you might spend more time on the model serving rather than the data exploration. Or conversely, if you need to get tabular data from external APIs you might want to spend more time on the data construction rather than on model serving optimisation. Those are design choices you need to make depending on your project - and as always make sure to ask questions to the teaching staff if you have any (ideally at the end of lectures).  

#### Milestones

The main way to handover the results of your projects will be during the 3 **milestones**.

The first Milestone will be used to present the work you did during sprint 1 & 2, the second Milestone for the work you did in sprint 3 & 4 and the final milestone will be used to present the overall project outcome and work from sprint 5.

The main purpose of the Milestones is to provide feedback and guidance on the project. The final project grade will be determined at the end of the project. If there are any issues highlighted during the milestone there is room for fixing it in the later development of the project.

Make it your own! Focus on what is relevant and interesting. You are free to decide which material (if any) you will use to present your results (short slide deck, demo, show codes, ...).

#### Handovers
1. At each milestone, you will show your results through a **10 minutes presentation** followed by a 5 minutes QA from the teaching staff. There are two options for those presentations:
2. Next to that, you will **submit the codes** you implemented so far by creating a pull requests in Github and asking the teaching staff to review it.
Make sure to clearly document what is important in the code base for the teaching staff to look at. By default, the teaching staff will focus on the README and the pull request description.

#### Practicals
:warning: Each team needs **to book a meeting** slot to present their Milestone. Link will be *shared by email* (if a group has no students in the mailing list please let the teaching staff know.). There are two options for those meetings:
1. You can book an online meeting via a Google Meets between 13:00 and 17:00 in the days available for each specific milestone (for exact days see calendar invite and [timing section](#timing))
2. You can present it in the classroom from 11:30 to 12:30 right after the lectures in the two weeks following the closing sprint of a milestone (for exact days see calendar invite and [timing section](#timing)). As the class will be busy with presentations after the course those weeks, it means that other teams can still use the time to work on their projects but from another location. Support on the project will then be more ad-hoc those weeks. You can still raise questions by email, Discord or during the open office hours every Monday till 18:00 in office 77B in building B28.


Make sure to send an email with a **link to the pull request** to the teaching staff when it is ready. Notifications on Github are not the single point.

You can present your project [ML Canvas](https://madewithml.com/courses/mlops/product-design) during the first Milestone presentation.

#### Timing
- Milestone 1 presentations will happen between the 11/03/2024 and the 18/03/2024
- Milestone 2 and 3 timing still needs to be set.

## Exam 

You can find a practice exam in the [exams/practice_exam_june_2024.pdf](exams/practice_exam_june_2024.pdf) document.

## Resources

#### Similar classes
- University of Bari.
  - Paper: "Teaching MLOps in Higher Education through Project-Based Learning." arXiv preprint arXiv:2302.01048 (2023) ([link](https://upcommons.upc.edu/bitstream/handle/2117/390805/ICSE_SEET_2023_MLOps.pdf?sequence=3))
  - Lanubile Filippo, Silverio Martínez-Fernández and Luigi Quaranta
- Stanford University
  - CS 329S: Machine Learning Systems Design ([link](https://stanford-cs329s.github.io/))
  - Chip Huyen
- Carnegie-Mellon University
  - Machine Learning in Production / AI Engineering ([link](https://ckaestne.github.io/seai/)) 
  - Christian Kästner

#### General MLOps resources
- Machine Learning Engineering for Production (MLOps) Specialization (Coursera, Andrew Ng) ([link](https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops?utm_campaign=video-youtube-mlops-video-series&utm_medium=institutions&utm_source=deeplearning-ai))
- Made with ML ([link](https://madewithml.com/))
- Marvelous MLOps ([link](https://marvelousmlops.substack.com/))
- Hidden Technical Debt in Machine Learning System - Google ([link](https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf))

#### Books
- Building Machine Learning Powered Applications: Going from Idea to Product (Emmanuel Ameisen)
- Introducing MLOps (Mark Treveil, Nicolas Omont, Clément Stenac et al.)
- Machine Learning Design Patterns (Valliappa Lakshmanan, Sara Robinson, Michael Munn)

# Credits

Many people helped and supported through the preparation of this course. Special thanks to:
- Gilles Louppe
- Filippo Lanubile
- Luigi Quaranta
- Robbe Sneyders
- Sebastian Wehkamp
- Ruwan Lambrichts
- Jason Li
- Thomas Janssens