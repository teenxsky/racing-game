'''from openal import *
from time import sleep

running_max_volume = float()
running_max_pitch = float()
idle_max_volume = float()
idle_max_pitch = float()
class car_conroller:
    def __init__(self, speed, max_speed):
        self.speed = speed
        self.max_speed = max_speed
        self.pitch = 0

        self.source = oalOpen("/Users/ruslankutorgin/Desktop/cars/chevrolet_camaro/stallionon.wav")
        self.source.play()
        self.source.set_looping(True)

    def change_pitch(self):
        while self.source.get_state() == AL_PLAYING:
            self.pitch += 0.001
            self.source.set_pitch(self.pitch)
            self.source.update()
            sleep(0.01)

oalQuit()
'''

'''from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import make_chunks

sound = AudioSegment.from_file('/Users/ruslankutorgin/Desktop/cars/chevrolet_camaro/stallionidle_1.mp3', format="mp3")

octaves = -5

# shift the pitch up by half an octave (speed will increase proportionally)
while octaves != 2:
    octaves += 1

    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))

    # keep the same samples but tell the computer they ought to be played at the
    # new, higher sample rate. This file sounds like a chipmunk but has a weird sample rate.
    hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})

    # now we just convert it to a common sample rate (44.1k - standard audio CD) to
    # make sure it works in regular audio players. Other than potentially losing audio quality (if
    # you set it too low - 44.1k is plenty) this should now noticeable change how the audio sounds.
    hipitch_sound = hipitch_sound.set_frame_rate(44100)

    #Play pitch changed sound
    play(hipitch_sound)
    print(octaves)

#export / save pitch changed sound
#hipitch_sound.export("/Users/ruslankutorgin/Desktop/cars/chevrolet_camaro/stallionon_out.mp3", format="mp3")'''


'''from pydub import AudioSegment
from pydub.effects import pitch_shift

# Load the audio file
audio = AudioSegment.from_file("input.wav", format="wav")

# Shift the pitch by 2 semitones higher
shifted_audio = pitch_shift(audio, n=2)'''

from pydub import AudioSegment
from pydub.utils import make_chunks

audio = AudioSegment.from_file("/Users/ruslankutorgin/Desktop/cars/chevrolet_camaro/stallionidle_1.mp3")

# Define the loop start and end points in milliseconds
loop_start = 0
loop_end = 500

# Create a Loop object
loop = AudioSegment.from_mono_audiosegments(make_chunks(audio[loop_start:loop_end], len(audio)))

# Apply the loop to the audio file
looped_audio = audio.apply_loop(loop)

# Export the looped audio to a new file
looped_audio.export("looped_audio.wav", format="wav")