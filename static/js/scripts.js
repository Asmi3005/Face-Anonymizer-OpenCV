let currentBlur = "blur";
const blurOptions = ["blur", "pixelate", "blackout", "emoji"];
let currentIndex = 0;

// Webcam state
let isWebcamActive = false;
let animationFrameId;

document.addEventListener("DOMContentLoaded", () => {
  const webcamSection = document.getElementById("webcam");
  const uploadSection = document.getElementById("upload");
  
  // Result elements
  const resultContainer = document.getElementById("result-container");
  const downloadLink = document.getElementById("download-link");
  
  // Webcam elements
  const effectName = document.getElementById("effect-name");
  const video = document.getElementById("webcam-stream");
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");

  // --- Core Logic ---

  function stopWebcam() {
    if (video.srcObject) {
      video.srcObject.getTracks().forEach(track => track.stop());
      video.srcObject = null;
    }
    isWebcamActive = false;
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
    }
  }

  function startWebcam() {
    stopWebcam(); // Ensure any previous stream is stopped
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        video.srcObject = stream;
        video.play();
        isWebcamActive = true;
        // Hide the static result container and download link
        resultContainer.innerHTML = '';
        downloadLink.style.display = 'none';
        // Start the processing loop
        animationFrameId = requestAnimationFrame(processWebcamFrameLoop);
      })
      .catch(err => {
        console.error("Webcam access error:", err);
        alert("Could not access webcam. Please ensure it is not in use by another application and that you have granted permission.");
      });
  }

  async function processWebcamFrameLoop() {
    if (!isWebcamActive) return;

    // Capture a frame
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL("image/png");

    // Prepare data to send
    const formData = new FormData();
    formData.append('image_data', dataURL);
    formData.append('blur_type', currentBlur);

    try {
      const res = await fetch('/process_frame/', { method: 'POST', body: formData });
      if (res.ok) {
        const data = await res.json();
        // Display the processed frame in a new image element
        // This avoids waiting for the old image to load and reduces flicker
        if (!document.getElementById('processed-webcam-frame')) {
            resultContainer.innerHTML = '<img id="processed-webcam-frame" style="max-width: 100%; border-radius: 10px;" />';
        }
        document.getElementById('processed-webcam-frame').src = data.image_data;
      }
    } catch (error) {
      console.error("Error processing frame:", error);
      stopWebcam(); // Stop on error
    }

    // Continue the loop
    if (isWebcamActive) {
      animationFrameId = requestAnimationFrame(processWebcamFrameLoop);
    }
  }

  // --- Event Handlers & UI Functions ---

  window.showSection = function (id) {
    stopWebcam(); // Always stop webcam when switching sections
    uploadSection.classList.add("hidden");
    webcamSection.classList.add("hidden");
    
    const section = document.getElementById(id);
    section.classList.remove("hidden");

    // Clear previous results
    resultContainer.innerHTML = '';
    downloadLink.style.display = 'none';

    if (id === "webcam") {
      startWebcam();
    }
  };

  document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = e.target.querySelector('input[type="file"]');
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please select a file to upload.");
        return;
    }
    
    const formData = new FormData(e.target);
    const file = fileInput.files[0];
    const isVideo = file.type.startsWith('video/');

    try {
        const res = await fetch("/upload/", { method: "POST", body: formData });
        if (res.ok) {
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            
            // Clear previous result and create a new element
            resultContainer.innerHTML = '';
            let resultElement;
            if (isVideo) {
                resultElement = document.createElement('video');
                resultElement.controls = true;
                resultElement.autoplay = true;
                resultElement.loop = true;
            } else {
                resultElement = document.createElement('img');
            }
            resultElement.src = url;
            resultElement.style.maxWidth = '100%';
            resultElement.style.borderRadius = '10px';
            resultContainer.appendChild(resultElement);

            downloadLink.href = url;
            downloadLink.download = `processed_${file.name}`;
            downloadLink.style.display = 'inline-block';
        } else {
            alert("Upload failed. The server encountered an error.");
        }
    } catch (error) {
        console.error("Upload error:", error);
        alert("An error occurred during the upload.");
    }
  });

  window.toggleEffect = function () {
    currentIndex = (currentIndex + 1) % blurOptions.length;
    currentBlur = blurOptions[currentIndex];
    effectName.textContent = currentBlur.charAt(0).toUpperCase() + currentBlur.slice(1);
  };

  window.downloadFrame = function () {
    const processedFrame = document.getElementById('processed-webcam-frame');
    if (processedFrame && processedFrame.src) {
        downloadLink.href = processedFrame.src;
        downloadLink.download = `anonymized_${currentBlur}.png`;
        downloadLink.style.display = 'inline-block';
        // Give user feedback
        setTimeout(() => { alert('Download link is ready below the image.'); }, 100);
    } else {
        alert("No processed frame is available to download.");
    }
  };
});
