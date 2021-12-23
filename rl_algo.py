# You are allowed to use the following modules
import numpy as np
import matplotlib.pyplot as plt
import pygame
from spaceship_modified import Game
from pygame.locals import *
from tqdm import tqdm

# Your code here
#Code taken from itertools documentation
#Source : https://docs.python.org/3/library/itertools.html
def permutations(iterable, r=None):
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return

def combinations_with_replacement(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)

def cvalues(iterable,num_features):
    cwr=list(combinations_with_replacement(iterable,num_features))
    cvs=[]
    for c in cwr:
        pwc=permutations(c,len(c))
        for p in pwc:
            if p not in cvs:
                cvs.append(p)
    return np.asarray(cvs)

#preparing a dict of cvalues for faster calculation
cv={}
for i in range(2,4):
    cv[i]=cvalues(np.arange(i+1),6)

def cvalues_dict(iterable,num_features):
    if num_features==6 and len(iterable)>2 and len(iterable)<9:
        return cv[len(iterable)-1]
    else:
        return cvalues(iterable,num_features)


def fourier_basis(m1x,m1d,m2x,m2d,m3x,m3d,order):
    m1x=(300+m1x)/600
    m2x=(300+m2x)/600
    m3x=(300+m3x)/600
    m1d=m1d/500
    m2d=m2d/500
    m3d=m3d/500
    features=np.array([m1x,m1d,m2x,m2d,m3x,m3d])
    C=cvalues_dict(np.arange(order+1),len(features))
    return np.cos(np.pi*np.dot(C,features))

def policy(m1x,m1d,m2x,m2d,m3x,m3d,o,theta):
    x=fourier_basis(m1x,m1d,m2x,m2d,m3x,m3d,o)
    r1=np.append(x,np.zeros(2*(o+1)**6))
    r2=np.append(np.append(np.zeros((o+1)**6),x),np.zeros((o+1)**6))
    r3=np.append(np.zeros(2*(o+1)**6),x)
    x=np.array([r1,r2,r3])
    values=np.matmul(x,theta)
    values=np.exp(values-np.max(values))/sum(np.exp(values-np.max(values)))
    act=np.random.choice([-1,0,1],p=values)
    return act,values
theta=np.zeros(4096*3)
w=np.zeros(4096)

def actorcritic(theta,w,policy=policy,fourier_basis=fourier_basis,order=3,lambda_t=.7,lambda_w=.7,alpha_t=.0007,alpha_w=.0007,gamma=1):
    game = Game()
    starship_state,meteor_state,end,cycle_count,reward=game.playfirststep()
    m1x=meteor_state[0][3]
    m1d=meteor_state[0][5]
    m2x=meteor_state[1][3]
    m2d=meteor_state[1][5]
    m3x=meteor_state[2][3]
    m3d=meteor_state[2][5]
    z_t=np.zeros(4096*3)
    z_w=np.zeros(4096)
    i=1
    count=0
    total_reward=reward
    end=False
    actions=[0]
    states=[[starship_state,meteor_state,cycle_count]]
    while not end:
        action,values=policy(m1x,m1d,m2x,m2d,m3x,m3d,order,theta)
        starship_state_n,meteor_state_n,end,cycle_count_n,reward=\
            game.playstep(starship_state,meteor_state,cycle_count,action)
        states.append([starship_state_n,meteor_state_n,cycle_count])
        actions.append(action)
        total_reward+=reward
        m1x_n=meteor_state_n[0][3]
        m1d_n=meteor_state_n[0][5]
        m2x_n=meteor_state_n[1][3]
        m2d_n=meteor_state_n[1][5]
        m3x_n=meteor_state_n[2][3]
        m3d_n=meteor_state_n[2][5]
        
        if end:
            delta=reward-np.matmul(w,fourier_basis(m1x,m1d,m2x,m2d,m3x,m3d,order).T)
        else:
            delta=reward+gamma*np.matmul(w,fourier_basis(m1x_n,m1d_n,m2x_n,m2d_n,m3x_n,m3d_n,order).T)\
            -np.matmul(w,fourier_basis(m1x,m1d,m2x,m2d,m3x,m3d,order).T)
        z_w=gamma*lambda_w*z_w+fourier_basis(m1x,m1d,m2x,m2d,m3x,m3d,order)
        x=fourier_basis(m1x,m1d,m2x,m2d,m3x,m3d,order)
        r1=np.append(x,np.zeros(2*(order+1)**6))
        r2=np.append(np.append(np.zeros((order+1)**6),x),np.zeros((order+1)**6))
        r3=np.append(np.zeros(2*(order+1)**6),x)
        x=np.array([r1,r2,r3])
        lndelta=x[action+1]-np.matmul(values,x)
        z_t=gamma*lambda_t*z_t+i*lndelta
        w=w+alpha_w*delta*z_w
        theta=theta+alpha_t*delta*z_t
        i=gamma*i
        m1x=m1x_n
        m1d=m1d_n
        m2x=m2x_n
        m2d=m2d_n
        m3x=m3x_n
        m3d=m3d_n
        starship_state=starship_state_n
        meteor_state=meteor_state_n
        cycle_count=cycle_count_n
        count+=1
    return theta,w,count,total_reward,states,actions


super_count=[]
super_reward=[]
for i in tqdm(range(10)):
    counts=[]
    rewards=[]
    theta=np.zeros(4096*3)
    w=np.zeros(4096)
    for j in range(50):
        theta,w,count,reward,state,action=actorcritic(theta,w)
        counts.append(count)
        rewards.append(reward)
    super_count.append(counts)
    super_reward.append(rewards)

super_count=np.array(super_count)

plt.plot(super_count.mean(axis=0))
plt.ylabel('Average Length of episode')
plt.xlabel('Episode Number')
plt.show()

super_reward=np.array(super_reward)

plt.plot(super_reward.mean(axis=0))
plt.ylabel('Average Reward of episode')
plt.xlabel('Episode Number')
plt.show()




'''super_count=[]
super_reward=[]
for i in range(10):
    theta=np.zeros(4096*3)
    w=np.zeros(4096)
    counts=[]
    rewards=[]
    for i in tqdm(range(500)):
        theta,w,count,reward,state,action=actorcritic(theta,w)
        counts.append(count)
        rewards.append(reward)
    super_count.append(counts)
    super_reward.append(rewards)

super_count=np.asarray(super_reward)
plt.plot(np.mean(super_count,axis=0))
plt.show()
plt.savefig('episode_count.png')

super_count=np.asarray(super_reward)
plt.plot(np.mean(super_count,axis=0))
plt.show()
plt.savefit('rewards.png')'''

def main(): 
    print('Starting Game')
    game = Game()
    #game.play()
    for state,action in zip(states[0],actions[0]):
        starship_state,meteor_state,end,cycle_count,reward=\
            game.playstep(state[0],state[1],state[2],action)
        print(starship_state,meteor_state,end,cycle_count,reward)
    print('Game Over')
