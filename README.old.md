# IARC-2019
Autonomous flight code for IARC http://www.aerialroboticscompetition.org/

## Initial Notes

The following changes were made after receiving suggestions from the team

* The Movement class was incorporated into the DroneBase class. The drone can now be told to move through more simple commands, such as drone.move(c.UP, 2).
* The "safety loop" has been incorporated into DroneController. DroneController now runs on the main thread. This simplified communicating among different threads because it took away an unnecessary layer of complexity.
* The constants class was cleaned up, and the constants that were candidated for enums turned out to be unnecessary constants in the first place, and so they were removed.

Also of note is that the Task class is currently as it was during the meeting. After thinking about this for a long time, I came to the conclusion that drones should not "have" tasks because tasks contain the logic for flight, and a drone should not know how to control itself - that is what DroneController is for. DroneController "has" a drone which is shared among the various tasks that are created over the lifetime of the program's execution. Let me know if you have any objections.

## How to Run

From just outside of the IARC-2019 directory:
```python -m IARC-2019.Missions.test_mission```

Alternatively, you can add IARC-2019 to the path python checks so that you can run it from anywhere.

*Note*: The drone hovers in place after it completes its sample instructions. Press ctrl-c to land the drone.

## Additional Information

I have edited the googled doc at https://docs.google.com/document/d/163wfbQL27OfVNjDYWRLaQ6VAZdHyqeTQUx8KXFmavQo/edit to reflect the changes made. Some of the diagrams were no longer valid and so I removed them. I might add updated diagrams if I have time.

## How Can You Ensure The Code Works?

I don't have any unit tests at the moment (they are the next thing I plan to do). I will be on vacation for the week following this pull request, and but wanted to submit what I had so far.

If you have a Ubuntu and all the other necessary software, you could try running it and trying to get it to fail. I've done a lot of testing by hand in that way. If the unit tests are absolutely needed, I can resubmit the pull request a while down the road.

You can find videos of gazebo simulations on the team's Google Drive under Media/Videos/Gazebo Flight Simulations/.

## Known Issues

Because the code relies on blindly trusted dronekit methods, the drones movement is sometimes unpredictable. Sometimes the drone flies quite well, and other times very weird drifting happens (but the safety checks work to ensure nothing too crazy happens, or else the drone lands). Hovering is similar in that sometimes it is very steady, and other times bobbing up and down quite a bit.

## How to contribute
1. First make sure you are on the up to date `develop` branch.
```
git checkout develop
git pull
```
2. Create a branch to add your changes by running.
```
git checkout -b "branch_name"
```
> `branch_name` should follow the convention `feature/{feature_name}`, or `hotfix/{fix_name}`
3. Make changes in your new branch.
4. Once changes are complete, go to GitHub and submit a "Pull Request". Fill in necessary information.
5. Once it has been reviewed by other members of the team, it can be accepted to the `develop` branch and the cycle continues...

> More info on the process [here](https://nvie.com/posts/a-successful-git-branching-model/) and [here](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

