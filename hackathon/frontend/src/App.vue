<template>
  <v-app>
    <v-main>
      <IntroSection @scrollToAlphabet="scrollToAlphabet" />
      <AlphabetSection ref="alphabetSection" />
      <WordSection />
      <PhraseSection style="margin-bottom:50px;"/>
    </v-main>
    <FooterSection />
  </v-app>
</template>

<script>
import IntroSection from './components/IntroSection.vue';
import AlphabetSection from './components/AlphabetSection.vue';
import WordSection from './components/WordSection.vue'; // Import the WordSection component
import PhraseSection from './components/PhraseSection.vue';
import FooterSection from './components/FooterSection.vue';

export default {
  name: 'App',
  components: {
    IntroSection,
    AlphabetSection,
    WordSection, // Include the WordSection component
    FooterSection,
    PhraseSection,
  },
  methods: {
    scrollToAlphabet() {
      // Access the DOM element and scroll to it
      this.$nextTick(() => {
        this.$refs.alphabetSection.$el.scrollIntoView({ behavior: 'smooth' });
      });
    },
  },
};
</script>

<style>
@import './assets/animations.css';
html, body {
  height: 100%;
  margin: 0;
}
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>
