<template>
  <v-container id="alphabet-section" class="my-5">
    <h2>Tatar Alphabet</h2>
    <p>Click on a letter to hear its pronunciation and upload your own audio to see if it matches.</p>
    <v-row justify="center">
      <v-col
        v-for="letter in alphabet"
        :key="letter"
        cols="auto"
      >
        <v-btn 
          @click="selectLetter(letter)" 
          :style="{ backgroundColor: isLetterCorrect(letter) ? 'green' : '', color: isLetterCorrect(letter) ? 'white' : 'black' }"  
          outlined
        >
          {{ letter }}
        </v-btn>
      </v-col>
    </v-row>
    <v-dialog v-model="dialog" persistent max-width="600px">
      <v-card>
        <v-card-title class="headline">{{ selectedLetter }}</v-card-title>
        <v-card-text>
          <div>
            <p>Listen to the pronunciation:</p>
            <div id="initial-waveform"></div>
            <div class="audio-controls">
              <v-btn @click="toggleAudio" :color="isPlaying ? 'error' : 'primary'">
                {{ isPlaying ? 'Stop' : 'Play' }}
              </v-btn>
            </div>
          </div>
          <div v-if="resultMessage" class="result-message" :class="resultClass">{{ resultMessage }}</div>
          <div class="audio-recorder mt-4">
            <p v-if="audioRecorded">Your voice</p>
            <div id="waveform" :style="{ height: waveformHeight + 'px' }"></div>
            <v-btn 
              id="botcontrols" 
              v-if="audioRecorded" 
              @click="toggleAudioRecorded" 
              :color="isPlayingRecorded ? 'error' : 'primary'"
            >
              {{ isPlayingRecorded ? 'Stop' : 'Play' }}
            </v-btn>
            <v-btn 
              v-if="!isRecording" 
              style="margin-top:60px;" 
              @click="startRecording" 
              color="primary"
              class="recBut"
            >
              Try to say it!
            </v-btn>
            <v-btn 
              v-if="isRecording" 
              style="margin-top:60px;" 
              @click="stopRecording" 
              color="error"
              class="recBut"
            >
              Stop Recording
            </v-btn>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" @click="closeDialog">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import apiClient from '../services/api'; // Adjust the path based on your structure

import WaveSurfer from 'wavesurfer.js';


export default {
  name: 'AlphabetSection',
  data() {
    return {
      alphabet: ['А', 'Ә', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'Җ', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'Ң', 'О', 'Ө', 'П', 'Р', 'С', 'Т', 'У', 'Ү', 'Ф', 'Х', 'Һ', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я'],
      selectedLetter: '',
      dialog: false,
      audioSrc: '',
      resultMessage: '',
      resultClass: '',
      // Audio recording related data
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      audioBlob: null,
      waveSurfer: null,
      audioRecorded: false,
      initialWaveSurfer: null,
      correctLetters: [], // Array to store correct letters
      isPlaying: false,  // Add this line
      isPlayingRecorded: false,
      waveformHeight: 0, // Reactive property for recorded waveform height
    };
  },
  methods: {
    selectLetter(letter) {
      this.selectedLetter = letter;
      this.audioSrc = `http://localhost:8000/media/LettersAudio/${letter}.wav`; // Adjust the path as needed
      this.dialog = true;

      this.$nextTick(() => {
        this.waveSurfer = WaveSurfer.create({
          container: '#waveform',
          waveColor: 'violet',
          progressColor: 'purple',
          cursorWidth: 0 // Set cursor width to 0 to disable the cursor line
        });
        this.initialWaveSurfer = WaveSurfer.create({
          container: '#initial-waveform',
          waveColor: 'violet',
          progressColor: 'purple',
          cursorWidth: 0 // Set cursor width to 0 to disable the cursor line
        });

        this.initialWaveSurfer.load(this.audioSrc); 
        this.initialWaveSurfer.on('finish', this.audioFinished);
        this.waveSurfer.on('finish', this.audioFinishedRecorded);
        this.waveformHeight = 0;
      });

    },
    async startRecording() {
  this.audioChunks = [];
  this.isRecording = true;
  this.waveformHeight = 0;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.mediaRecorder = new MediaRecorder(stream);

    this.mediaRecorder.ondataavailable = (event) => {
      console.log('Data available:', event.data);
      this.audioChunks.push(event.data);
      // Update the waveform visualization
      this.waveSurfer.loadBlob(event.data);
    };

    await new Promise((resolve) => {
      this.mediaRecorder.onstart = resolve;
      this.mediaRecorder.start();
    });
  } catch (error) {
    console.error('Error accessing the microphone', error);
    this.isRecording = false;
  }
},

async stopRecording() {
  if (this.mediaRecorder && this.isRecording) {
    this.isRecording = false;

    await new Promise((resolve) => {
      this.mediaRecorder.onstop = resolve;
      this.mediaRecorder.stop();
    });

    this.waveformHeight = 100;
    // Stop the waveform visualization
    this.waveSurfer.stop();
    this.audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
    this.submitRecording();
  } else {
    console.error('MediaRecorder is not initialized or not recording');
  }
},

async submitRecording() {
  if (!this.audioBlob) return;
  this.audioRecorded = true;
  const formData = new FormData();
  formData.append('file', this.audioBlob, 'recording.wav');
  formData.append('letter', this.selectedLetter);

  try {
    const response = await apiClient.post('/uploadLetter/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    console.log('Response data:', response.data); // Log the response data

    if (response.data.result === true) {
      this.resultMessage = 'Correct!';
      this.resultClass = 'correct';
      this.correctLetters.push(this.selectedLetter);
    } else {
      this.resultMessage = 'Wrong!';
      this.resultClass = 'wrong';
    }

    // Show the result message
    setTimeout(() => {
      this.resultMessage = '';
    }, 2000); // match the animation duration
  } catch (error) {
    console.error('Error submitting the recording:', error);
    alert('Failed to submit the recording.');
  }
},
    closeDialog() {
      this.dialog = false;
      this.audioRecorded = false;
      this.isRecording = false;
      this.mediaRecorder = null;
      this.isPlaying= false;  // Add this line
      this.isPlayingRecorded= false;
    },
    toggleAudio() {
      if (this.isPlaying) {
        this.stopInitialAudio();
      } else {
        this.playInitialAudio();
      }
      this.isPlaying = !this.isPlaying;
    },
    toggleAudioRecorded() {
      if (this.isPlayingRecorded) {
        this.stopAudio();
      } else {
        this.playAudio();
      }
      this.isPlayingRecorded = !this.isPlayingRecorded;
    },
    playAudio() {
    if (this.waveSurfer) {
      this.waveSurfer.play();
    }
    },
    playInitialAudio() {
      if (this.initialWaveSurfer) {
        this.initialWaveSurfer.play();
      }
    },

    // Method to stop the initial audio playback
    stopInitialAudio() {
      if (this.initialWaveSurfer) {
        this.initialWaveSurfer.stop();
      }
    },
    // Method to stop the audio
    stopAudio() {
      if (this.waveSurfer) {
        this.waveSurfer.stop();
      }
    },
    audioFinished() {
      this.isPlaying = false;
    },
    audioFinishedRecorded() {
      this.isPlayingRecorded = false;
    }
  },
  computed: {
  // Computed property to determine if a letter has been marked as correct
  isLetterCorrect() {
    return (letter) => {
      // Assuming you have a list of correct letters in your component data
      return this.correctLetters.includes(letter);
    };
  }
}
};
</script>

<style scoped>
#alphabet-section {
  text-align: center;
}

#alphabet-section h2 {
  margin-bottom: 20px;
}

#alphabet-section p {
  margin-bottom: 30px; /* Adjust the margin bottom as needed */
}

.v-dialog__content {
  text-align: left;
}

.result-message {
  margin-top: 20px; /* Adjust the margin top as needed */
  padding: 10px 20px; /* Add padding for better appearance */
  border-radius: 5px; /* Add border-radius for rounded corners */
  font-weight: bold; /* Make the text bold */
}

.correct {
  color: white;
  background-color: green;
}

.wrong {
  color: white;
  background-color: red;
}

.audio-recorder {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.audio-recorder v-btn {
  animation: pulse 1s infinite;
}

.recBut {
  z-index:3;
}
/* Animation */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

#waveform,
#comparison-waveform {
  width: 100%;
  height: 150px; /* Adjust the height as needed */
  z-index:2;
}

#botcontrols {
  margin-top:30px;
  z-index:5;
}

#waveform > div {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
}

/* Styling for the waveform itself */
#waveform > div > div {
  background-color: #3498db; /* Waveform color */
}

/* Styling for the progress of the waveform */
#waveform > div > div.wavesurfer-progress {
  background-color: #2980b9; /* Progress color */
}

.audio-controls {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

.audio-controls v-btn {
  margin: 0 5px;
  z-index: 2;
}

/* Add styles for the initial waveform display */
#initial-waveform {
  width: 100%;
  height: 100px; /* Adjust the height as needed */
  position: relative;
  z-index: -1;
}

#initial-waveform > div {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
}
</style>
