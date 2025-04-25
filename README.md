# [Web Application Development](https://gitlab.msu.edu/cse477-spring-2025/course-materials/): Final Exam

## Purpose

The purpose of this Final Exam is to assess your understanding of the essential elements of web application development covered this semester; these elements include:

1. Reactive front-end design 

2. Design of a data-driven backend 

3. Session management 

4. Asynchronous communication 

   

## Exam Format and Expectations

The exam is an asynchronous take-home that is worth 35% of the final course grade. Please note that: like any class, you are given more time to complete homework assignments than the exam; and, like any class, the purpose of the exam is to assess (i) your independent problem-solving abilities and (ii) your understanding of the course material. 

It is against the spirit of our exam (like any exam) for us to offer students with implementation support, hints, or extensions. To be perfectly clear: 

* The teaching team will **only** answer questions that seek to clarify an exam requirement. 

- The teaching team **will not** help debug code, problem solve, or assist with deployment. 
- The teaching team **will not** provide extensions on the Final Exam. 

Your exam application should be stand-alone – that is, it should not be a tab within the application you have been developing in Homeworks 1-3. However, you are welcome to reuse any parts of your prior implementation (including your DockerFiles) to help complete the exam.

Critically, the exam will be graded strictly according to the rubric provided at the end of this document. Just like the homework assignments, you will only be evaluated on the criteria explicitly defined in the rubric. To be clear: any features or implementation details that are not mentioned in the rubric will not affect your grade, unless they interfere with the evaluation of a required element; for example, if your font color matches your background color and renders text unreadable, that would inhibit assessment and may result in lost credit. It is also important to note that all rubric requirements must function as expected without requiring undocumented or unusual prerequisites.



## Exam Goals

The goal of the final exam is to build an extended version of the group scheduling tool [When2Meet](https://www.when2meet.com/).

When2Meet is a scheduling platform that allows users to create events and collaboratively indicate their availability using a grid-based calendar interface. As more users mark themselves as available for a time slot, the color intensity of that slot increases—visually highlighting periods of overlap. The platform is commonly used to identify the best meeting time for a group.

Your task is to replicate the core features of When2Meet and extend them to include richer group logic and interactivity. Before starting your implementation, you are **strongly encouraged to visit [https://www.when2meet.com](https://www.when2meet.com)** and familiarize yourself with its basic functionality and interface—it will make the specific exam requirements provided below significantly easier to understand and implement.



## Specific Requirements

### 1. **Signup System** (10 points)

* Users must be able to register using an email and password.
* Users must be able to log in and out securely.
* Only logged-in users should be able see access pages where they provide their availability / see the availability of others.
* Passwords must be encrypted.



---

### 2. **The Interface**

#### 2.1 **Sign-In Properties** (10 points)

After logging in, users must be presented with two clear options on the interface:  (i) Create a New Event, or  (ii) Join an Existing Event.

**Creating a New Event** must require the following inputs from the user:

- Event Name: a short descriptive title for the event (e.g., “Team Meeting Scheduler”).
- Start Date and End Date: these define the date range over which availability will be collected. Both dates must be inclusive.
- Daily Time Range: the hours of the day in which availability will be collected (e.g., 8:00 AM to 8:00 PM). 
- List of Invitee Emails: a comma-separated list of email addresses belonging to registered users who should be allowed to view and participate in the event. 

Once the form is submitted:

* A new Event should be created and stored in the database, along with the corresponding date and time parameters.
* The currently logged-in user (creator) must be added as a participant in the Event, and be automatically redirected to the Event Page following creation
* All invitees must also be associated with the Event in the backend (even if they have not yet logged in, or created an account).

**Joining an Existing Event** must behave as follows:

* Users who have been listed as invitees by an Event creator must be able to see a list of all Events they were invited to; this list should appear when selecting “Join Existing Event” after login.
* Each Event in the list must be displayed with: the Event Name, the Creator’s email and the date range of the Event
* The user must be able to click on an Event from the list of events to open the Event-specific Page.



---

#### 2.2 **Event Page Properties** (10 points)

Each Event must have a dedicated and secure Event Page accessible only to users who have been explicitly invited to the Event. The Event Page must include the following components and behaviors:

**Event Metadata Display**: the following information must be clearly displayed at the top of the page.

* The Event Title (as provided by the creator)
* The Date Range (e.g., “April 15–April 20, 2025”)

**Availability Grid**: The page must display an interactive grid where:

* Rows represent time slots in half-hour increments (e.g., 8:00–8:30, 8:30–9:00, etc.)
* Columns represent each day in the event's date range.
* Each cell in the grid represents one 30-minute time slot on a given day.

**Availability Modes**: There must be a clearly visible mode selector (i.e. a dropdown) that allows users to switch between the following three availability states:

* Available: User is fully available for this time slot.
* Maybe: User is tentatively available for this time slot.
* Unavailable: User is not available for this time slot.

The currently selected mode must be visually distinguished (e.g., highlighted or outlined). When the user clicks or drags on grid cells, the selected mode must be applied to those cells and persisted in the database.

**Access Control**: Only users who are listed as invitees for the event (or the creator) should be able to access the Event Page. If a logged-in user attempts to access an Event for which they are not invited, the system must redirect them away or display an “Access Denied” message.



---

#### 2.3 **Availability Grid Interactions** (10 points)

The availability grid must be fully interactive and support intuitive click-and-drag behavior for applying availability statuses. The grid interaction system must meet the following requirements:

**Click-and-Drag Behavior**:  Users must be able to click and drag across one or more grid cells to apply their currently selected availability status to all selected cells in a single operation. Dragging must support both horizontal (within a day) and vertical (across multiple days) motions.  Users must also be able to single-click to modify individual cells.

**Status Application Logic**: The availability mode applied to each selected cell must match the currently selected mode from the mode selector (Available, Maybe, or Unavailable). Switching the mode selector should immediately update what is applied when interacting with the grid thereafter.

**Visual Feedback**: Each grid cell must visually indicate its current status; the styling must be consistent and immediately update in response to user interaction:

* "Available" cells should appear in one distinct color (e.g., green).
* "Maybe" cells should appear in a different distinct color (e.g., yellow).
* "Unavailable" cells should appear in a neutral or low-contrast color (e.g., grey, transparent, or white).

**Persistence of Selections**: All user selections must be saved in the backend as soon as they are made. These records must be written in such a way that they are retrievable when the user reloads the page or logs in again. When a user returns to the Event Page or refreshes it, their previously selected availability statuses must be correctly rendered on the grid exactly as they left it.



---

#### 2.4 **Heatmap Visualization** (10 points)

Your application must implement a live heatmap overlay on the availability grid that visually reflects the collective responses of all users in the event. This visualization allows participants to quickly identify time blocks with the highest likelihood of group availability.

**Color Intensity for “Available”**: The background color of each grid cell must become progressively darker or more saturated as more users select Available for that specific time block. For example:

* 1 user available → light green
* 2 users available → medium green
* 3 or more users available → dark green

The exact mapping of availability counts to color intensity must be consistent and perceptible (e.g., via a defined CSS gradient scale). You must support a minimum of 3 levels of intensity, reflecting at least 3 distinct group counts.

**Color Differentiation for Other Modes**:

* If one or more users have selected Maybe for a time slot (and no users are marked as Available), the cell must appear in a distinct yellow hue.
* If one or more users have selected Unavailable for a time slot (and no other statuses apply), the cell must appear in a low-contrast color (e.g., light grey, transparent, or white).
* If multiple status types are present (e.g., some users Available, others Maybe or Unavailable), the color should still prioritize Available and reflect the correct availability count via intensity.

**Rendering and Responsiveness**: The heatmap must render immediately after users make changes to their availability (i.e., no page reload). 

---

#### 2.5 **Best Time Calculation** (10 points)

Each Event Page must contain a clearly labeled section titled “Best Time to Meet”, which dynamically identifies and displays the single most optimal 30-minute time slot for the entire group. This feature must meet the following requirements:

**Best Time Calculation Logic**: Your application must compute the “best” time slot using the following priority rules; this computation must be made based on all user availability data currently stored in the backend for the Event:

1. Highest number of users marked as “Available” for that time slot.
2. If two or more slots are tied for the highest “Available” count, select the slot with the fewest users marked as “Unavailable”.
3. If a tie still exists after applying both rules above, select the earliest time slot among the tied options.

**Visual Display Requirements**: The “Best Time to Meet” section must be clearly visible on the Event Page—either above or beside the grid. The section must include the following text-based content:

* Date of the best slot (e.g., “Tuesday, April 16”)
* Start and End Time of the 30-minute block (e.g., “2:00 PM – 2:30 PM”)

**Edge Case Handling**: If no users have submitted any availability data, display a neutral message (e.g., “No availability submitted yet”). If all time slots have zero availability, display the earliest time slot in the range with a note that no one is currently available.

---

#### 2.6 **Live Synchronization** (30 points)

Your application must support real-time synchronization of user interactions across all clients currently viewing the same Event. This ensures that all participants see up-to-date availability data without needing to refresh the page.

**Real-Time Availability Updates**: When a user changes the availability status of any grid cell (whether by clicking or dragging), the affected grid cell must update in real-time to reflect the new availability status (e.g., change in color intensity).

**Real-Time Heatmap Updates**: The heatmap must dynamically reflect changes in group availability as users update their selections. For example, if a new user selects “Available” for a time block already selected by others, the color intensity of that cell must increase immediately on all connected clients.

**Real-Time Best Time Recalculation**: If a user changes their availability, the Best Time to Meet section (see 2.5) must recalculate and update instantly for everyone else on the page. No page reloads, polling intervals, or “refresh” buttons are permitted.

**Technology Requirements**: This behavior must be implemented using a real-time communication mechanism, such as WebSockets. Solutions based on periodic polling (e.g. setInterval or AJAX with fixed delays) will not be accepted for this requirement.

**Scope of Synchronization**: Only users currently viewing the Event Page should receive real-time updates. Users logged into other Events or idle elsewhere in the application must not receive unrelated synchronization messages.



## Submitting your assignment

Be sure to perform all development in the `Final-Exam` directory of your <u>Personal Course Repository</u>

**Submit Exam Code:** Submit your assignment by navigating to the main directory of your <u>Personal Course Repository</u> and Pushing your repo to Gitlab

**Deploy your web application to Google Cloud**: Deploy your Dockerized App to Google Cloud. As we did in the homeworks, please retain the <u>Service URL</u>.



### Submit Final Exam Service URL (This is required):

[Submit the Service URL for your live web application in this Google Form](https://docs.google.com/forms/d/e/1FAIpQLSeujaUEYKbIjibH8R6ZLmIZbaOgeJEZWSW_0qIVNuKvir6mhg/viewform?usp=header).



## Rubric

The exam is graded on a 100 point scale; all individual requirements recieve an "all or nothing" grade. The following guide will be used when grading your submission:



**Specific Requirements:**

**1:** <u>10 points</u> – All "Signup System" requirements were met.

**2.1:** <u>10 points</u> – All Interface "Sign-in Properties" requirements were met.

**2.2:** <u>10 points</u> – All Interface "Event Page Properties" requirements were met.

**2.3:** <u>10 points</u> – All Interface "Availability Grid Interactions" requirements were met.

**2.4:** <u>10 points</u> – All Interface "Heatmap Visualization" requirements were met.

**2.5:** <u>10 points</u> – All Interface "Best Time Calculation" requirements were met.

**2.6:** <u>30 points</u> – All Interface "Live Synchronization" requirements were met.



**General Requirements:**

<u>5 points</u> - Does the code adhere to Frontend best practices covered throughout the semester?

<u>5 points</u> - Does the code adhere to Backend best practices covered throughout the semester?



**Please note that you will receive a 0 on the assignment if any of the following conditions are met:**

* Your containerized application does not compile
* Your application is non-functional
* Your submission was late
* Your work was plagiarized, borrowed, or copied
  * If this condition is met, you will also fail the course.
