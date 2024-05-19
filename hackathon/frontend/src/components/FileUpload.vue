<!-- src/components/FileUpload.vue -->
<!--template>
  <div>
    <h2>Upload Audio File</h2>
    <input type="file" @change="handleFileUpload" accept="audio/*" />
    <button @click="submitFile">Submit</button>
  </div>
</template-->

<template>
  <div class="upload-container">
    <h2>Upload Audio File</h2>
    <input type="file" @change="handleFileUpload" accept="audio/*" class="file-input" />
    <button @click="submitFile" class="submit-button">Submit</button>
  </div>
</template>

<script>
import apiClient from '../services/api'; // Adjust the path based on your structure

export default {
  data() {
    return {
      selectedFile: null,
    };
  },
  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
    },
    async submitFile() {
      if (!this.selectedFile) {
        alert('Please select a file first.');
        return;
      }

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await apiClient.post('/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        // Check response status
        if (response.status === 201) {
          alert('File uploaded successfully: ' + response.data.file_path);
        } else {
          alert('Unexpected response status: ' + response.status);
        }
      } catch (error) {
        console.error('There was an error uploading the file:', error);
        alert('Failed to upload the file.');
      }
    },
  },
};
</script>

<style scoped>
.upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  max-width: 400px;
  margin: auto;
  background-color: #f9f9f9;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.file-input {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}

.submit-button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background-color: #42b983;
  color: white;
  cursor: pointer;
  font-size: 16px;
}

.submit-button:hover {
  background-color: #38a16f;
}
</style>
