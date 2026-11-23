---
canvas_key: lab6-sim            # Canvas identity; never changes. See docs/adr/0002.
site_page: weber_assignments/labs/lab6-sim
rubric_source: docs/weber_assignments/labs/lab6/LOGGER-SIM.md
repo_task: lab6-pure-pursuit
repo_folder: docs/weber_assignments/labs/lab6
assignment_group: Labs
points: 100
due_week: 7             # see calendar in canvas/course.yml; the lock is two weeks later
notes: lecture Wed of week 7
team: false
submission_types: [online_text_entry]   # repo URL plus the demonstration video URL
---

Write a waypoint logger that records the car's poses to a CSV file, then drive a full lap in the simulator and record it. The CSV you produce here is the path your Pure Pursuit node drives in Lab 7.

You do this half by yourself, in the simulator. Localize with the particle filter and log `/pf/pose/odom`, not the simulator's own `/ego_racecar/odom`: ground truth is easier to log and teaches you nothing the car can use. The topic you write against here is the topic the car publishes, so Lab 6 Car is a port rather than a rewrite.

Your repository holds the `pure_pursuit` package for both Lab 6 and Lab 7, so you keep it for the next lab. The full instructions, deliverables, and rubric are on the course site.

**Submit here**, in the text box:

1. The URL of your repository.
2. The link to your video (YouTube, unlisted).

Paste both into the box as plain links. The video link belongs here, not in `SUBMISSION.md` - putting it here is what makes it one click to open while your work is being graded. A video that has to be downloaded to watch is not graded, so YouTube unlisted only.
