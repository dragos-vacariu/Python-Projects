import pygame
import sched, time

pygame.mixer.init()
song_1 = pygame.mixer.Sound('song1.mp3')
song_2 = pygame.mixer.Sound('song2.mp3')
pygame.mixer.fadeout(10000)
song_1.play(0)

scheduler = sched.scheduler(time.time, time.sleep)    
playback_time = 0
switch = 0;


def function():
    global playback_time
    global switch
    playback_time+=1
    if playback_time > song_1.get_length() -5 and switch==0:
        song_2.play(0)
        switch = 1;

    pygame.time.delay(1000)
    try:
        scheduler.enter(0.1, 1, function)
        scheduler.run()
    except Exception as exp:
        print( str(exp))
    

function()