# RL-Framework
University of Washington Tacoma TCSS 556 Final Project
-------------
```
As reinforcement learning techniques become more powerful, it becomes
 possible for researchers to specify a reinforcement learning agent
 at a higher conceptual level. We present a GUI framework for a user
 to specify, train, and test an RL agent entirely within a user
-friendly and non-technical GUI. Included in the framework are
 several types of general RL agents to choose from, which may be
 applied to several OpenAI Gym environments. In addition, an API is
 available for specifying an arbitrary agent type or environment to
 include in the framework as a plugin. 
```
##Getting Started:

The following are basic instructions set up and run a copy of the
 application on your local machine for testing and development
  purposes. 
  
###Prerequisites:
  
To setup, first install the required pip packages using these commands
 in a Python 3.7 environment:
```
pip install pillow
pip install gym
pip install pandas
pip install numpy
pip install tensorflow
pip install joblib
pip install ttkthemes
pip install ttkwidgets
pip install opencv-python
```

(if not on Windows): 
```
pip (or pip3) install gym[atari]
```
(OR if on Windows with the Visual C++ Build Tools installed):
```
pip install --no-index -f https://github.com/Kojoley/atari-py
/releases atari_pypip install git+https://github.com/Kojoley/atari-py.git)
```
##Running the Program:
First, run the following on either Mac Linux or Windows PC...

-For Linux Command line:
```
./PortalRL
```
-For Windows CmdPrompt
```
python portalrl.py
```
Note: We have CartPole with discretized states and a Q-Table, and
 CartPole  with continuous states and Deep Q learning implemented. We
  also have FrozenLake partially implemented with Q-Learning, which
   prints its output to the console instead of displaying in the GUI
    for now. Also, FrozenLake's data is not yet displaying on the
     graph.

##Running the tests
###The Framework:
The framework of the graphical interface is based on a tab system
. Each tab represents an agent/environment pair which may be
 trained/tested concurrently with, and independent of, all other tabs
 . 
 
 Associated with each agent are parameters that are editable by the
 user prior to training/testing. 
 
 In order to control the training and testing processes, the user is
  given the options to start/halt training/testing, save the trained
   agent, load a trained agent , reset the currently loaded agent
    , and to save the results of the training/testing process.

The types of agent types available by default are as follows: 
```
Q-Table SARSA/Q-Learning
deep Q-learning
deep recurrent Q-learning
action deep recurrent Q-learning. 

```
The default agent types are all based on model-free algorithms
, and serve to approximate the optimal Q-function Q*. 
```
 ?^? (s) = arg (maxQ/a)^?(s, a)
```
###Selecting training parameters:

####For CartPole with discretized states and a Q-Table:
```
Click 'New Agent' -> 'Cart Pole Discretized' -> 'Q-Learning' Tab
```
####For CartPole with continuous states and a DQN:
```
Click 'New Agent' -> 'Cart Pole' -> 'Deep Q Learning' Tab
```
####For FrozenLake with a Q-Table:
```
Click 'New Agent' -> 'Frozen Lake' -> 'Q-Learning' Tab
```
###Demo
Our demonstration video makes it clear how a GUI can greatly simplify
 the process of defining, training, and test- ing a reinforcement
  learning agent. In the video, one can see how a user on a typical
   consumer-grade desktop computer can quickly produce RL agents with
    minimal knowledge of AI and even programming in general.

* [Demo](https://www.overleaf.com/project/5edbdec4b060950001e5e6c1
) - Video explanation of the RL-Framework application

###Deployment:
Notes about how to deploy on a live system

##Reference on RL-Framework
###Built with:
Notes with relevant tools or resources used to build RL-Framework

###Literature:
* [Paper](https://www.overleaf.com/project/5edbdec4b060950001e5e6c1
) - User Friendly Reinforcement Learning

###Contributing:
Notes on our code of conduct and or on the process for submitting
 pull requests from us.

###Authors:
* James Haines-Temons
* Neil Hulbert
* Kevin Flora
* Brandon Francis
* Sam Spillers

###License:
This project is licensed by The University of Washington Tacoma

###Acknowledgements:
* A
* B

 