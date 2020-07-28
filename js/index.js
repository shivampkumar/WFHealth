let shouldStop = false;
let stopped = false;
const downloadLink = document.getElementById('download');
const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const video = document.querySelector('video');
const recordedChunks = [];

var handleSuccess = function (stream) {
    if (MediaRecorder.isTypeSupported('video/webm;codecs=vp9')) {
        const options = { mimeType: 'video/webm; codecs=vp9' };
        const mediaRecorder = new MediaRecorder(stream, options);

        mediaRecorder.start();
        video.srcObject = stream;

        stopButton.addEventListener('click', function () {

            if (stopped === false) {
                mediaRecorder.stop();
                stopped = true;
            }

            mediaRecorder.addEventListener('dataavailable', function (e) {
                if (e.data.size > 0) {
                    recordedChunks.push(e.data);
                }
            });

            mediaRecorder.addEventListener('stop', function () {
                var url = URL.createObjectURL(new Blob(recordedChunks));
                downloadLink.href = url;
                downloadLink.download = 'health.webm';
                downloadLink.click();

                stream.getTracks().forEach(function (track) {
                    track.stop();
                });

                window.URL.revokeObjectURL(url);
            });
        });
    }
    else {
        console.log("Mime Type not supported...");
        return;
    }
};

// $(document).ready(() => {
//     navigator.mediaDevices.getUserMedia({ video: true })
//         .then(handleSuccess);
// });

startButton.addEventListener('click', function () {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(handleSuccess);
});

