<template>
  <v-container class="intro-section" style="height: 100vh;">
    <div class="intro-content">
      <p style="font-size: 48px;">Learn Tatar with AI</p>
      <div class="intro-title" style="height:280px;">
        <span ref="typedElement"></span>
        <span class="cursor"></span>
      </div>
      <v-btn color="primary" @click="scrollToAlphabet" class="intro-btn">Start</v-btn>
    </div>
    <div class="intro-image">
      <img src="http://localhost:8000/media/SystemImages/robot.jpg" alt="Image">
    </div>
  </v-container>
</template>

<script>
import Typed from 'typed.js';

export default {
  name: 'IntroSection',
  mounted() {
    const strings = ['Сәлам, барыгызга да!', 'Әйдәгез бергәләп татарча өйрәник!'];
    const options = {
      strings: strings,
      typeSpeed: 50,
      backSpeed: 30,
      backDelay: 1500,
      startDelay: 0,
      showCursor:false,
      loop: true, 
      smartBackspace: true,
    };

    this.typed = new Typed(this.$refs.typedElement, options);
  },
  beforeUnmount() {
    if (this.typed) {
      this.typed.destroy();
    }
  },
  methods: {
    scrollToAlphabet() {
      this.$emit('scrollToAlphabet');
    }
  }
};
</script>
<style scoped>
  .intro-section {
    width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr; /* Two equal columns */
  align-items: center; /* Center vertically */
  /*justify-items: center; /* Center horizontally */
  height: 100vh; /* Ensure full viewport height */
  margin-right:0px;
  margin-top:0px;
}

.intro-title {
  position: relative;
  font-size: 4rem;
  overflow: hidden;
  word-wrap: break-word;
}

.intro-title::after {
  content: '|';
  font-size: 120%;
  display: inline-block;
  color: orange;
  animation: cursor-blink 0.7s infinite;
}

@keyframes cursor-blink {
  0%, 100% {
    color: transparent;
  }
  50% {
    color: orange;
  }
}

.intro-image {
  margin-left: 100px;
  grid-column: 2; /* Place image in the second column */
}

.intro-image img {
  max-width: 80%;
  max-height: 80%;
}

.intro-btn {
  margin-top: 20px;
}
</style>
