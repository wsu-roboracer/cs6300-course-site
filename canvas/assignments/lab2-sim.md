---
canvas_key: lab2-sim            # Canvas identity; never changes. See docs/adr/0002.
site_page: weber_assignments/labs/lab2-sim
rubric_source: docs/weber_assignments/labs/lab2/SIM.md
repo_task: lab2-aeb
repo_folder: docs/weber_assignments/labs/lab2
assignment_group: Labs
points: 100
due_week: 2             # see calendar in canvas/course.yml; the lock is two weeks later
notes: lecture Wed of week 2, with in-class simulator work the same week
team: false
submission_types: [online_text_entry]   # repo URL plus the demonstration video URL
---
Write a safety node that stops the car before it hits something. It reads the lidar scan and the car's speed, works out the time to collision, and brakes when a collision is close.

You do this half by yourself, in the simulator. In Lab 2 Car your team runs it on a real RoboRacer in class, so get the braking logic right here, where a crash costs you a reset.

You can write it in Python or C++. The full instructions, deliverables, and rubric are on the course site. Your repository includes a check script that scores everything except the video.

**Submit here**, in the text box:

1. The URL of your repository.
2. The link to your video (YouTube, unlisted).

Paste both into the box as plain links. The video link belongs here, not in `SUBMISSION.md` - putting it here is what makes it one click to open while your work is being graded. A video that has to be downloaded to watch is not graded, so YouTube unlisted only.
