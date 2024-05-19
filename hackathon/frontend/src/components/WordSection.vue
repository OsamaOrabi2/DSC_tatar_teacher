<template>
  <div class="word-section">
    <h2>Word Practice</h2>
    <v-btn @click="openDialog" class="generate-btn">Try to pronounce a Tatar word</v-btn>
    <v-dialog v-model="dialogOpen" max-width="600px">
      <v-card>
        <v-card-title class="headline">Word Practice</v-card-title>
        <v-card-text class="text-center">
          <div v-if="wordExists">
            <p class="generated-word">{{ generatedWord }}</p>
            <img :src="imageUrl" alt="Generated Image" class="word-image" />
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
              <div id="waveform"></div>
              <!--div id="waveform" :style="{ height: waveformHeight + 'px' }"></div-->
              <div class="audio-controls">
                <v-btn 
                  v-if="audioRecorded" 
                  style="margin-top:50px;"
                  @click="toggleAudioRecorded"
                  :color="isPlayingRecorded ? 'error' : 'primary'"
                >
                  {{ isPlayingRecorded ? 'Stop' : 'Play' }}
                </v-btn>
              </div>
            </div>
            <v-btn 
              v-if="!isRecording" 
              @click="startRecording" 
              style="margin-top:100px;"
              color="primary"
              class="recBut"
            >
              Try to say it!
            </v-btn>
            <v-btn 
              v-if="isRecording"  
              @click="stopRecording" 
              style="margin-top:100px;"
              color="error"
              class="recBut"
            >
              Stop Recording
            </v-btn>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" @click="generateWord">Generate Word</v-btn>
          <v-btn color="error" @click="closeDialog">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>


<script>
  import apiClient from '../services/api';
  import WaveSurfer from 'wavesurfer.js';
export default {
  name: 'WordSection',
  data() {
    return {
      dialogOpen: false,
      generatedWord: '',
      wordExists: false,
      imageUrl: '', // Property to hold the image URL
      audioSrc: '',
      resultMessage: '',
      resultClass: '',
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      audioBlob: null,
      waveSurfer: null,
      audioRecorded: false,
      initialWaveSurfer: null,
      isPlaying: false,  // Add this line
      isPlayingRecorded: false,
    };
  },
  methods: {
  async startRecording() {
  this.audioChunks = [];
  this.isRecording = true;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.mediaRecorder = new MediaRecorder(stream);

    this.mediaRecorder.ondataavailable = (event) => {
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
    this.audioRecorded = true;
    this.audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
    // Stop the waveform visualization
    this.waveSurfer.stop();
    this.submitRecording();
  } else {
    console.error('MediaRecorder is not initialized or not recording');
  }
},

async submitRecording() {
  if(!this.audioBlob){
      this.resultMessage = 'Wrong!';
      this.resultClass = 'wrong';
    return;
  }
  const formData = new FormData();
  formData.append('file', this.audioBlob, 'recording.wav');
  formData.append('word', this.generatedWord); // Adjust this as needed

  try {
    const response = await apiClient.post('/uploadWord/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    console.log('Response data:', response.data); // Log the response data

    if (response.data.result === true) {
      this.resultMessage = 'Correct!';
      this.resultClass = 'correct';
    } else {
      this.resultMessage = 'Wrong!';
      this.resultClass = 'wrong';
    }
    // Show the result message
    setTimeout(() => {
      this.resultMessage = '';
    }, 10000); // match the animation duration
  } catch (error) {
    console.error('Error submitting the recording:', error);
    alert('Failed to submit the recording.');
  }
},

    openDialog() {
      this.dialogOpen = true;
    },
    generateWord() {
      if(this.wordExists)return;
      // Replace this with your logic to generate a random word
      this.generatedWord = "алма"; // Example
      this.imageUrl = "http://localhost:8000/media/wordImages/алма.jpg"; // Path to your static image
      this.audioSrc = "http://localhost:8000/media/wordImages/алма.wav";
      this.wordExists = true;

      this.$nextTick(() => {
        this.waveSurfer = WaveSurfer.create({
          container: '#waveform',
          waveColor: 'violet',
          progressColor: 'purple',
          cursorWidth: 0 // Set cursor width to 0 to disable the cursor line
        });
        this.initialWaveSurfer = WaveSurfer.create({
          container: '#initial-waveform',
          waveColor: 'green',
          progressColor: 'blue',
          cursorWidth: 0 // Set cursor width to 0 to disable the cursor line
        });

        this.initialWaveSurfer.load(this.audioSrc); 
        this.initialWaveSurfer.on('finish', this.audioFinished);
        this.waveSurfer.on('finish', this.audioFinishedRecorded);
      });
    },
    closeDialog() {
      this.dialogOpen = false;
      this.wordExists= false;
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
      this.audioRecorded = true;
    },
  },
};
</script>

<style scoped>
.word-section {
  text-align: center;
  margin-top: 30px; /* Adjust margin top as needed */
}

.word-image {
  margin-top: 10px;
  max-width: 100%;
  height: auto;
}

.audio-controls v-btn {
  margin: 0 5px;
}

.audio-controls {
  margin-top: 10px;
  display: flex;
  justify-content: center;
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

.v-card-actions {
  margin-top: 20px;
}

</style>

