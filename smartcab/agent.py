import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.learner = {}
        self.wincount = 0
        self.invalidcount = 0
        self.alpha = 0.3
        self.discount = 0.5
        self.initialvalue = 0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
    
    def qLearn(self, state, action, reward, stateprime, choices):
        self.alpha = 0.5
        statetuple = tuple(state.values())
        if (statetuple, action) not in self.learner:
            self.learner[(statetuple, action)] = self.initialvalue
        else:
            self.learner[(statetuple, action)] = self.learner[(statetuple, action)]*(1-self.alpha) + (reward + self.discount * self.qChoose(state, choices)[0]) * self.alpha
        print self.learner[(statetuple, action)]

    def qChoose(self, state, choices):
        statetuple = tuple(state.values())
        final_choice = (-1000000, None)

        for choice in choices:
            if (statetuple, choice) not in self.learner:
                self.learner[(statetuple, choice)] = self.initialvalue
            choice_weight = self.learner[(statetuple, choice)]
            final_choice = max([final_choice, (choice_weight, choice)])
        
        return final_choice
            
    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = inputs
        self.state['next_waypoint'] = self.next_waypoint

        # TODO: Select action according to your policy
        choices = [None, 'left', 'right', 'forward']
        weighted_action = self.qChoose(self.state, choices)        
        action = weighted_action[1]
        
        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        stateprime = self.env.sense(self)
        stateprime['next_waypoint'] = self.planner.next_waypoint()
        self.qLearn(self.state, action, reward, stateprime, choices)

        if reward == 12:
            self.wincount += 1
        elif reward < 0:
            self.invalidcount += 1
                

        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]        

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.1, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

if __name__ == '__main__':
    run()
