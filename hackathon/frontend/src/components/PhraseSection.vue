<template>
  <div class="phrase-section">
    <h2>Phrase Practice</h2>
    <v-card>
      <v-card-title>Enter Your Phrase</v-card-title>
      <v-card-text>
        <v-text-field v-model="userPhrase" label="Your Phrase" outlined></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="submitPhrase">Submit</v-btn>
      </v-card-actions>
      <div>
        <h3 v-if="submitted">Pronunciation</h3>
        <p>{{ userPhrase }}</p>
        <div id="phrase-waveform"></div>
        <div class="audio-controls">
          <v-btn v-if="submitted" @click="toggleInitialAudio" :color="isPlayingInitial ? 'error' : 'primary'">
            {{ isPlayingInitial ? 'Stop' : 'Play' }}
          </v-btn>
        </div>
      </div>
      <div v-if="resultMessage" class="result-message" :class="resultClass">{{ resultMessage }}</div>
      <div class="audio-recorder mt-4">
        <div id="recorded-waveform" :style="{ height: waveformHeight + 'px' }"></div>
        <div class="audio-controls">
          <v-btn 
            v-if="audioRecorded" 
            @click="toggleRecordedAudio"
            :color="isPlayingRecorded ? 'error' : 'primary'"
          >
            {{ isPlayingRecorded ? 'Stop' : 'Play' }}
          </v-btn>
        </div>
        <v-btn 
          v-if="!isRecording" 
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
      <div class="recommended-text" style="margin:30px;">
        <h2>
            <span v-html="coloredPhrase"></span>
          </h2>
          </div>
           <div class="recommended-sound">
        <h3 v-if="audioRecorded" >Pronunciation details</h3>
        <div id="recommended-waveform"></div>
        <v-btn v-if="audioRecorded" @click="toggleRecommendedAudio" :color="isPlayingRecommended ? 'error' : 'primary'">
          {{ isPlayingRecommended ? 'Stop' : 'Play' }}
        </v-btn>
      </div>
    </v-card>
  </div>
</template>

<script>
import axios from 'axios';
import WaveSurfer from 'wavesurfer.js';
import apiClient from '../services/api';

export default {
  name: 'PhraseSection',
  data() {
    return {
      audioChunks: [],
      isRecording: false,
      audioBlob: null,
      audioUrl: '',
      audioRecorded: false,
      resultMessage: '',
      resultClass: '',
      userPhrase: '',
      initialWaveSurfer: null,
      recordedWaveSurfer: null,
      recommendedWaveSurfer: null,
      isPlayingInitial: false,
      isPlayingRecorded: false,
      isPlayingRecommended: false,
      submitted: false,
      waveformHeight: 100,
      recommendedSoundUrl: 'http://localhost:8000/media/final_slowed_audio.wav',  // Static URL for recommended sound
    };
  },
  methods: {
    async submitPhrase() {
      try {
        await axios.post('http://localhost:8000/api/tts/', { text: this.userPhrase });
        this.audioUrl = "http://localhost:8000/media/uploaded_audio/spoken_phrase.wav";
        this.submitted = true;
        this.initializeInitialWaveSurfer();
      } catch (error) {
        console.error('Error fetching TTS audio:', error);
      }
    },
    initializeInitialWaveSurfer() {
      if (this.initialWaveSurfer) {
        this.initialWaveSurfer.destroy();
      }
      this.initialWaveSurfer = WaveSurfer.create({
        container: '#phrase-waveform',
        waveColor: 'violet',
        progressColor: 'purple',
        height: 100
      });
      this.initialWaveSurfer.load(this.audioUrl);
    },
    toggleInitialAudio() {
      if (this.isPlayingInitial) {
        this.initialWaveSurfer.stop();
      } else {
        this.initialWaveSurfer.play();
      }
      this.isPlayingInitial = !this.isPlayingInitial;
      this.initialWaveSurfer.on('finish', () => {
        this.isPlayingInitial = false;
      });
    },
    async startRecording() {
      this.audioChunks = [];
      this.isRecording = true;

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);

        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = () => {
          this.audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
          this.audioRecorded = true;
          this.initializeRecordedWaveSurfer();
          this.submitRecording();  // Submit the recording as soon as it stops
          this.initializeRecommendedWaveSurfer();
        };

        this.mediaRecorder.start();
      } catch (error) {
        console.error('Error accessing the microphone', error);
        this.isRecording = false;
      }
    },
    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.isRecording = false;
        this.mediaRecorder.stop();
      }
    },
    initializeRecordedWaveSurfer() {
      if (this.recordedWaveSurfer) {
        this.recordedWaveSurfer.destroy();
      }
      this.recordedWaveSurfer = WaveSurfer.create({
        container: '#recorded-waveform',
        waveColor: 'violet',
        progressColor: 'purple',
        height: 100
      });
      console.log("LOADING!");
      this.recordedWaveSurfer.loadBlob(this.audioBlob);
    },
    toggleRecordedAudio() {
      if (this.isPlayingRecorded) {
        this.recordedWaveSurfer.stop();
      } else {
        this.recordedWaveSurfer.play();
      }
      this.isPlayingRecorded = !this.isPlayingRecorded;
      this.recordedWaveSurfer.on('finish', () => {
        this.isPlayingRecorded = false;
      });
    },
    initializeRecommendedWaveSurfer() {
      if (this.recommendedWaveSurfer) {
        this.recommendedWaveSurfer.destroy();
      }
      this.recommendedWaveSurfer = WaveSurfer.create({
        container: '#recommended-waveform',
        waveColor: 'violet',
        progressColor: 'purple',
        height: 100
      });
      this.recommendedWaveSurfer.load(this.recommendedSoundUrl);
    },
    toggleRecommendedAudio() {
      if (this.isPlayingRecommended) {
        this.recommendedWaveSurfer.stop();
      } else {
        this.recommendedWaveSurfer.play();
      }
      this.isPlayingRecommended = !this.isPlayingRecommended;
      this.recommendedWaveSurfer.on('finish', () => {
        this.isPlayingRecommended = false;
      });
    },
    async submitRecording() {
  if (!this.audioChunks.length) return;
  const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });

  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.wav');
  formData.append('phrase', this.userPhrase);

  try {
    const response = await apiClient.post('/uploadPhrase/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    console.log('Response data:', response.data);

    if (response.data.result === true) {
      this.resultMessage = 'Correct!';
      this.resultClass = 'correct';
    } else {
      this.resultMessage = 'Wrong!';
      this.resultClass = 'wrong';
    }

    // Color the phrase based on the evaluation
    this.coloredPhrase = this.colorPhrase(response.data.evaluation);

    setTimeout(() => {
      this.resultMessage = '';
    }, 2000); // match the animation duration
  } catch (error) {
    console.error('Error submitting the recording:', error);
    alert('Failed to submit the recording.');
  }
},
  colorPhrase(evaluation) {
    const coloredPhrase = this.userPhrase.split('').map((char, index) => {
      if (evaluation[index] == 1) {
        return `<span style="color: green;">${char}</span>`;
      } else {
        return `<span style="color: red;">${char}</span>`;
      }
    }).join('');
    return coloredPhrase;
  }
}
};
</script>

<style scoped>
.phrase-section {
  text-align: center;
  margin-top: 30px;
}

.phrase-section h2 {
  margin-bottom: 20px;
}

.v-card {
  max-width: 500px;
  margin: 0 auto;
}

.v-card-title {
  font-size: 20px;
}

.v-text-field {
  width: 100%;
}

.v-btn {
  margin-top: 10px;
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
</style>
