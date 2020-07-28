var ffmpeg = require('ffmpeg');
const fs = require("fs");

const extractButton = document.getElementById('extract');

extractButton.addEventListener('click', () => {
    try {
        console.log("Started...");
        const path = "health.webm";
        if (fs.existsSync(path)) {
            console.log("File exists.")
        } else {
            console.log("File does not exist.")
        }
    
        var process = new ffmpeg(path);
    
        process.then((video) => {
            console.log('The video is ready to be processed');
            var options = {
                frame_rate : 1,
                number : 5,
                file_name : 'my_frame_%t_%s'
            };
    
            video.fnExtractFrameToJPG('../frames/', (options))
            .then((files) => {
                console.log('Frames: ' + files);
            }).catch((err) => {
                console.log('Error: ' + err);
            });
    
        }).catch((err) => {
            console.log('Error: ' + err);
        });
    } catch (e) {
        console.log(e.code);
        console.log(e.msg);
    }    
});
