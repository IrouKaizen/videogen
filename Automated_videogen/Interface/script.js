document.getElementById('generate-btn').addEventListener('click', () => {
    const textInput = document.getElementById('text-input').value;

    if (!textInput.trim()) {
        alert('Please enter some text!');
        return;
    }

    fetch('/generate-video', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: textInput }),
    })
        .then(response => response.json())
        .then(data => {
            const videoDisplay = document.getElementById('video-display');
            videoDisplay.innerHTML = ''; // Clear placeholder content

            const videoElement = document.createElement('video');
            videoElement.src = data.video_url;
            videoElement.controls = true;
            videoElement.autoplay = true;
            videoElement.style.borderRadius = '12px';
            videoDisplay.appendChild(videoElement);
        })
        .catch(error => {
            console.error('Error generating video:', error);
            alert('An error occurred while generating the video.');
        });
});
